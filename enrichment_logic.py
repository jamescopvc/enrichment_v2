import logging
from typing import Dict, List, Any, Optional, Tuple
from specter_client import SpecterClient
from apollo_client import ApolloClient
from openai_client import OpenAIClient
from gemini_client import filter_vc_investors, rank_top_investors, resolve_investor_domain
from config import VALID_LIST_SOURCES, OWNER_ASSIGNMENTS

logger = logging.getLogger(__name__)

class EnrichmentService:
    def __init__(self):
        self.specter_client = SpecterClient()
        self.apollo_client = None  # Initialize lazily (fallback for email)
        self.openai_client = None  # Initialize lazily
    
    def validate_list_source(self, list_source: str) -> Tuple[bool, Optional[str]]:
        """
        Validate list source and determine owner
        """
        logger.info(f"Validating list source: {list_source}")
        
        list_source_lower = list_source.lower()
        for valid_source in VALID_LIST_SOURCES:
            if valid_source in list_source_lower:
                owner = OWNER_ASSIGNMENTS.get(valid_source)
                logger.info(f"Valid list source: {list_source} -> Owner: {owner}")
                return True, owner
        
        logger.warning(f"Invalid list source: {list_source}")
        return False, None
    
    def enrich_company(self, domain: str, list_source: str) -> Dict[str, Any]:
        """
        Main enrichment pipeline using Specter API
        """
        logger.info(f"🚀 Starting enrichment: {domain} ({list_source})")
        
        # Validate list source
        is_valid, owner = self.validate_list_source(list_source)
        if not is_valid:
            logger.error("❌ Invalid list source")
            return {"status": "failed", "message": "Invalid list source"}
        
        logger.info(f"✅ Owner: {owner}")
        
        # Step 0: Get company info (includes founder_info)
        logger.info("📍 Step 0: Company enrichment")
        company_data = self.specter_client.get_company_by_domain(domain)
        
        # Initialize OpenAI client
        if self.openai_client is None:
            self.openai_client = OpenAIClient()
        
        if company_data:
            logger.info(f"✅ Company: {company_data['name']}")
            
            # Classify industry
            logger.info("🤖 Analyzing vertical...")
            industry = self.openai_client.classify_industry(company_data)
            logger.info(f"✅ Vertical: {industry}")
            
            # Prepare company info
            company_info = {
                "name": company_data.get('name', 'Unknown'),
                "domain": domain,
                "industry": industry,
                "location": company_data.get('location', 'Unknown'),
                "employee_count": company_data.get('employee_count', 0),
                "linkedin": company_data.get('linkedin_url', ''),
                "description": company_data.get('description', '')
            }
        else:
            # Specter didn't find company - use basic info and Apollo fallback for founders
            logger.warning("⚠️  Specter didn't find company, using Apollo fallback...")
            company_data = {}  # Empty so founder_info_list will be empty, triggering Apollo fallback
            industry = "Unknown"
            company_info = {
                "name": domain.split('.')[0].title(),  # Best guess from domain
                "domain": domain,
                "industry": industry,
                "location": "Unknown",
                "employee_count": 0,
                "linkedin": "",
                "description": ""
            }
        
        # Step 1: Get founders from company data (Specter includes founder_info in company response)
        logger.info("👥 Step 1: Processing founders from company data")
        founder_info_list = company_data.get('founder_info', [])
        logger.info(f"📊 Found {len(founder_info_list)} founders in company data")
        
        founders = []
        if founder_info_list:
            for i, founder_basic in enumerate(founder_info_list, 1):
                person_id = founder_basic.get('specter_person_id')
                basic_name = founder_basic.get('full_name', 'Unknown')
                basic_title = founder_basic.get('title', '')
                
                logger.info(f"  [{i}] {basic_name} ({basic_title})")
                
                if not person_id:
                    logger.warning(f"      ⚠️  No person ID available, skipping")
                    continue
                
                # Step 2: Get full person details
                logger.info(f"      🔍 Fetching person details...")
                person_data = self.specter_client.get_person(person_id)
                
                if person_data and person_data.get('status') == 'pending':
                    logger.warning(f"      ⏳ Person enrichment pending (202)")
                    # Include with basic data only
                    self._add_founder_to_list(
                        founders, basic_name, 
                        basic_name.split()[0] if basic_name != 'Unknown' else 'Unknown',
                        ' '.join(basic_name.split()[1:]) if basic_name != 'Unknown' else '',
                        basic_title, '',
                        '',
                        company_info, industry, owner
                    )
                    continue
                
                if not person_data:
                    logger.warning(f"      ⚠️  Could not fetch person details")
                    continue
                
                # Extract person info
                full_name = person_data.get('full_name', basic_name)
                first_name = person_data.get('first_name', '')
                last_name = person_data.get('last_name', '')
                title = person_data.get('title', '') or basic_title
                linkedin_url = person_data.get('linkedin_url', '')
                
                # Step 3: Get email (Specter first, Apollo fallback)
                logger.info(f"      📧 Fetching email...")
                email = self.specter_client.get_person_email(person_id)
                
                if email:
                    logger.info(f"      ✅ Email (Specter): {email}")
                else:
                    # Apollo fallback - try by LinkedIn URL first, then by name
                    logger.info(f"      🔄 Specter failed, trying Apollo fallback...")
                    if self.apollo_client is None:
                        self.apollo_client = ApolloClient()
                    
                    if linkedin_url:
                        email = self.apollo_client.get_email_by_linkedin(linkedin_url)
                    
                    if not email and first_name and last_name:
                        email = self.apollo_client.enrich_person(first_name, last_name, company_info['domain'])
                    
                    if email:
                        logger.info(f"      ✅ Email (Apollo): {email}")
                    else:
                        logger.warning(f"      ⚠️  No email available from either source")
                
                # Add founder to list
                self._add_founder_to_list(
                    founders, full_name, first_name, last_name,
                    title, email or '',
                    linkedin_url,
                    company_info, industry, owner
                )
        
        # Apollo fallback: Search for founders if Specter has none
        if not founders:
            logger.info("🔄 No founders from Specter, trying Apollo fallback...")
            if self.apollo_client is None:
                self.apollo_client = ApolloClient()
            
            apollo_founders = self.apollo_client.search_founders(domain)
            
            if apollo_founders:
                logger.info(f"✅ Apollo found {len(apollo_founders)} founders")
                for i, af in enumerate(apollo_founders, 1):
                    # Use Apollo data (already enriched by ID in search_founders)
                    full_name = af.get('full_name', 'Unknown')
                    first_name = af.get('first_name', '')
                    last_name = af.get('last_name', '')
                    title = af.get('title', '')
                    email = af.get('email', '')
                    linkedin_url = af.get('linkedin_url', '')
                    
                    logger.info(f"  [{i}] {full_name} ({title})")
                    
                    if email:
                        logger.info(f"      ✅ Email (Apollo): {email}")
                    
                    # Specter fallback: Only if Apollo has no email but has LinkedIn
                    if not email and linkedin_url:
                        logger.info(f"      🔄 No Apollo email, trying Specter via LinkedIn...")
                        specter_person = self.specter_client.lookup_person_by_linkedin(linkedin_url)
                        
                        if specter_person and specter_person.get('person_id'):
                            person_id = specter_person['person_id']
                            specter_email = self.specter_client.get_person_email(person_id)
                            if specter_email:
                                email = specter_email
                                logger.info(f"      ✅ Email (Specter fallback): {email}")
                    
                    if not email:
                        logger.warning(f"      ⚠️  No email available")
                    
                    self._add_founder_to_list(
                        founders, full_name, first_name, last_name,
                        title, email or '',
                        linkedin_url,
                        company_info, industry, owner
                    )
            else:
                logger.warning("❌ Apollo also found no founders")
        
        # Step 4: Get top investors with domains
        logger.info("💰 Step 4: Processing investors")
        investors_list = self._get_top_investors(company_data, company_info)
        logger.info(f"✅ Found {len(investors_list)} top investors")
        
        # Flatten investors to individual fields for Zapier compatibility
        investor_fields = {}
        for i in range(3):  # Always output 3 investor slots
            if i < len(investors_list):
                investor_fields[f"investor_{i+1}_name"] = investors_list[i].get("name", "")
                investor_fields[f"investor_{i+1}_domain"] = investors_list[i].get("domain", "")
            else:
                investor_fields[f"investor_{i+1}_name"] = ""
                investor_fields[f"investor_{i+1}_domain"] = ""
        
        # Determine status
        if founders and any(f.get('email') for f in founders):
            status = "enriched"
            logger.info(f"✅ Status: enriched - {len(founders)} founders with emails")
        elif founders:
            status = "partial"
            logger.info(f"⚠️  Status: partial - {len(founders)} founders but no emails")
        else:
            status = "failed"
            logger.error("❌ Status: failed - No founders found")
        
        result = {
            "status": status,
            "company": company_info,
            "founders": founders,
            "owner": owner
        }
        # Add flat investor fields to result
        result.update(investor_fields)
        
        return result
    
    def _add_founder_to_list(self, founders_list, full_name, first_name, last_name,
                            title, email, linkedin, company_info, industry, owner):
        """
        Helper to add a founder with generated email to the list
        """
        founder_info = {
            "name": full_name,
            "first_name": first_name,
            "last_name": last_name,
            "title": title,
            "email": email,
            "linkedin": linkedin
        }
        
        # Generate personalized email
        logger.info(f"      ✉️  Generating email...")
        email_content = self.openai_client.generate_email(
            company_info, founder_info, industry, owner
        )
        founder_info['generated_email'] = email_content
        
        founders_list.append(founder_info)
        logger.info(f"      ➕ Added to list")
    
    def _get_top_investors(self, company_data: Dict[str, Any], company_info: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Get top 3 investors with their domains.
        Pipeline: Extract investors -> Filter VCs/accelerators -> Rank top 3 -> Resolve domains
        """
        # Extract raw investors from Specter company data
        raw_investors = company_data.get('investors', [])
        
        if not raw_investors:
            logger.info("   No investors found in company data")
            return []
        
        logger.info(f"   📋 Raw investors: {len(raw_investors)}")
        
        try:
            # Step 1: Filter to VCs and accelerators only
            logger.info("   🔍 Filtering to VCs/accelerators...")
            filtered = filter_vc_investors(raw_investors)
            included = filtered.get('all_included_names', [])
            
            if not included:
                logger.info("   No VCs/accelerators found after filtering")
                return []
            
            logger.info(f"   ✅ Filtered to {len(included)} VCs/accelerators")
            
            # Step 2: Rank top 3
            logger.info("   🏆 Ranking top 3 investors...")
            company_context = f"{company_info.get('industry', 'Tech')}, {company_info.get('location', '')}"
            ranked = rank_top_investors(
                included,
                company_name=company_info.get('name'),
                company_context=company_context
            )
            top_names = ranked.get('top_names', [])
            
            if not top_names:
                logger.info("   No investors ranked")
                return []
            
            logger.info(f"   ✅ Top investors: {top_names}")
            
            # Step 3: Resolve domains for each
            logger.info("   🌐 Resolving domains...")
            investors_with_domains = []
            
            for name in top_names:
                result = resolve_investor_domain(name)
                domain = result.get('domain')
                
                investor_entry = {
                    "name": name,
                    "domain": domain
                }
                investors_with_domains.append(investor_entry)
                logger.info(f"      {name} -> {domain or 'NOT FOUND'}")
            
            return investors_with_domains
            
        except Exception as e:
            logger.error(f"   ❌ Error in investor enrichment: {e}")
            return []
