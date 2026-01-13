import logging
from typing import Dict, List, Any, Optional, Tuple
from specter_client import SpecterClient
from apollo_client import ApolloClient
from openai_client import OpenAIClient
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
        if not company_data:
            logger.error("❌ Company not found")
            return {"status": "failed", "message": "Company not found"}
        
        logger.info(f"✅ Company: {company_data['name']}")
        
        # Initialize OpenAI client
        if self.openai_client is None:
            self.openai_client = OpenAIClient()
        
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
        
        return {
            "status": status,
            "company": company_info,
            "founders": founders,
            "owner": owner
        }
    
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
