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
        logger.info(f"Starting enrichment for domain: {domain}, list_source: {list_source}")
        
        # Validate list source
        is_valid, owner = self.validate_list_source(list_source)
        if not is_valid:
            return {
                "status": "failed",
                "message": "Invalid list source"
            }
        
        # Step 0: Get company info
        logger.info("Step 0: Getting company information")
        company_data = self.apollo_client.get_company_by_domain(domain)
        if not company_data:
            return {
                "status": "failed",
                "message": "Company not found"
            }
        
        # Initialize OpenAI client
        if self.openai_client is None:
            self.openai_client = OpenAIClient()
        
        # Classify industry
        logger.info("Classifying industry")
        industry = self.openai_client.classify_industry(company_data)
        
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
        
        logger.info(f"Company: {company_info['name']} ({industry})")
        
        # Step 1: Search for founders
        logger.info("Step 1: Searching for founders")
        founders_data = self.apollo_client.search_founders(domain)
        
        founders = []
        if founders_data:
            logger.info(f"Found {len(founders_data)} potential founders")
            
            for founder in founders_data:
                # Extract founder info
                full_name = founder.get('name', 'Unknown')
                name_parts = full_name.split(' ', 1) if full_name != 'Unknown' else ['Unknown', '']
                first_name = name_parts[0] if name_parts else 'Unknown'
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                
                founder_info = {
                    "name": full_name,
                    "first_name": first_name,
                    "last_name": last_name,
                    "title": founder.get('title', ''),
                    "email": founder.get('email', ''),
                    "linkedin": founder.get('linkedin_url', '')
                }
                
                # Check if email is available
                if founder_info['email'] and founder_info['email'] != 'email_not_unlocked@domain.com':
                    logger.info(f"Founder {founder_info['name']} has email: {founder_info['email']}")
                    
                    # Generate personalized email
                    email_content = self.openai_client.generate_email(
                        company_info, founder_info, industry, owner
                    )
                    founder_info['generated_email'] = email_content
                    
                    founders.append(founder_info)
                    logger.info(f"Added founder: {founder_info['name']} ({founder_info['title']})")
                
                else:
                    logger.info(f"Founder {founder_info['name']} needs enrichment - email: {founder_info['email']}")
                    
                    # Step 2: Enrich person if needed
                    person_id = founder.get('person_id')
                    if person_id:
                        logger.info(f"Step 2: Enriching person {founder_info['name']} with ID: {person_id}")
                        enriched_person = self.apollo_client.enrich_person(person_id)
                        
                        if enriched_person and enriched_person.get('email'):
                            founder_info['email'] = enriched_person.get('email')
                            logger.info(f"Enriched email for {founder_info['name']}: {founder_info['email']}")
                            
                            # Generate email
                            email_content = self.openai_client.generate_email(
                                company_info, founder_info, industry, owner
                            )
                            founder_info['generated_email'] = email_content
                            
                            founders.append(founder_info)
                            logger.info(f"Added enriched founder: {founder_info['name']} ({founder_info['title']})")
                        else:
                            logger.warning(f"Could not enrich email for {founder_info['name']}")
                    else:
                        logger.warning(f"No person_id for {founder_info['name']}")
        
        # Determine status
        if founders and any(f.get('email') for f in founders):
            status = "enriched"
            logger.info("Status: enriched - Found company and founders with emails")
        elif founders:
            status = "partial"
            logger.info("Status: partial - Found company and founders but no emails")
        else:
            status = "failed"
            logger.info("Status: failed - No founders found")
        
        return {
            "status": status,
            "company": company_info,
            "founders": founders,
            "owner": owner
        }
