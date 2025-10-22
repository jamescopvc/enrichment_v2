import logging
from typing import Dict, List, Any, Optional, Tuple
from apollo_client import ApolloClient
from openai_client import OpenAIClient
from config import VALID_LIST_SOURCES, OWNER_ASSIGNMENTS

logger = logging.getLogger(__name__)

class EnrichmentService:
    def __init__(self):
        self.apollo_client = ApolloClient()
        self.openai_client = None  # Initialize lazily
    
    def validate_list_source(self, list_source: str) -> Tuple[bool, Optional[str]]:
        """
        Validate list source and determine owner
        """
        logger.info(f"Validating list source: {list_source}")
        
        for valid_source in VALID_LIST_SOURCES:
            if list_source.startswith(valid_source):
                owner = OWNER_ASSIGNMENTS.get(valid_source)
                logger.info(f"Valid list source: {list_source} -> Owner: {owner}")
                return True, owner
        
        logger.warning(f"Invalid list source: {list_source}")
        return False, None
    
    def enrich_company(self, domain: str, list_source: str) -> Dict[str, Any]:
        """
        Main enrichment pipeline
        """
        logger.info(f"🚀 Starting enrichment: {domain} ({list_source})")
        
        # Validate list source
        is_valid, owner = self.validate_list_source(list_source)
        if not is_valid:
            logger.error("❌ Invalid list source")
            return {"status": "failed", "message": "Invalid list source"}
        
        logger.info(f"✅ Owner: {owner}")
        
        # Step 0: Get company info
        logger.info("📍 Step 0: Company enrichment")
        company_data = self.apollo_client.get_company_by_domain(domain)
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
        
        # Step 1: Search for founders
        logger.info("👥 Step 1: Founder search")
        founders_data = self.apollo_client.search_founders(domain)
        logger.info(f"📊 Found {len(founders_data)} potential founders")
        
        founders = []
        if founders_data:
            for i, founder in enumerate(founders_data, 1):
                full_name = founder.get('name', 'Unknown')
                name_parts = full_name.split(' ', 1) if full_name != 'Unknown' else ['Unknown', '']
                first_name = name_parts[0] if name_parts else 'Unknown'
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                email = founder.get('email', '')
                person_id = founder.get('id')
                
                logger.info(f"  [{i}] {full_name} ({founder.get('title', '')}) - Email: {email}")
                
                # Check if email is unlocked
                if email and email != 'email_not_unlocked@domain.com':
                    logger.info(f"      ✅ Email available")
                    self._add_founder_to_list(
                        founders, full_name, first_name, last_name,
                        founder.get('title', ''), email,
                        founder.get('linkedin_url', ''),
                        company_info, industry, owner
                    )
                else:
                    # Step 2: Try to enrich person if we have ID
                    logger.info(f"      🔓 Email locked, attempting enrichment...")
                    if person_id:
                        enriched = self.apollo_client.enrich_person(person_id)
                        if enriched and enriched.get('email') and enriched.get('email') != 'email_not_unlocked@domain.com':
                            logger.info(f"      ✅ Enriched email: {enriched.get('email')}")
                            self._add_founder_to_list(
                                founders, full_name, first_name, last_name,
                                founder.get('title', ''), enriched.get('email'),
                                founder.get('linkedin_url', ''),
                                company_info, industry, owner
                            )
                        else:
                            logger.warning(f"      ❌ Enrichment failed or no email")
                    else:
                        logger.warning(f"      ❌ No person ID to enrich")
        
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
