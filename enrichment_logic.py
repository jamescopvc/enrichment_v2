import logging
from typing import Dict, List, Any, Optional, Tuple
from apollo_client import ApolloClient
from openai_client import OpenAIClient
from config import VALID_LIST_SOURCES, OWNER_ASSIGNMENTS

logger = logging.getLogger(__name__)

class EnrichmentService:
    def __init__(self):
        self.apollo_client = ApolloClient()
        self.openai_client = None  # Initialize lazily to avoid compatibility issues
    
    def validate_list_source(self, list_source: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if the list source is authorized and determine owner
        """
        logger.info(f"Validating list source: {list_source}")
        
        for valid_source in VALID_LIST_SOURCES:
            if valid_source.lower() in list_source.lower():
                owner = OWNER_ASSIGNMENTS.get(valid_source)
                logger.info(f"Valid list source: {list_source} -> Owner: {owner}")
                return True, owner
        
        logger.warning(f"Invalid list source: {list_source}")
        return False, None
    
    def enrich_company(self, domain: str, list_source: str) -> Dict[str, Any]:
        """
        Main enrichment logic - takes domain and returns enriched company data
        """
        logger.info(f"Starting enrichment for domain: {domain}, list_source: {list_source}")
        
        # Validate list source
        is_valid, owner = self.validate_list_source(list_source)
        if not is_valid:
            return {
                "status": "invalid",
                "message": "Unauthorized list source"
            }
        
        # Search for company
        logger.info(f"Searching for company with domain: {domain}")
        company_data = self.apollo_client.search_company_by_domain(domain)
        
        if not company_data:
            logger.warning(f"No company found for domain: {domain}")
            return {
                "status": "failed",
                "message": "Company not found"
            }
        
        # Extract company information
        company_info = {
            "name": company_data.get('name', 'Unknown'),
            "domain": domain,
            "industry": company_data.get('industry', 'Unknown'),
            "location": company_data.get('location', 'Unknown'),
            "employee_count": company_data.get('employee_count', 0),
            "linkedin": company_data.get('linkedin_url', ''),
            "description": company_data.get('description', '')
        }
        
        logger.info(f"Found company: {company_info['name']}")
        
        # Classify industry using AI
        logger.info("Classifying industry using AI")
        if self.openai_client is None:
            self.openai_client = OpenAIClient()
        classified_industry = self.openai_client.classify_industry(company_data)
        company_info['industry'] = classified_industry
        
        # Search for founders
        logger.info("Searching for founders")
        founders_data = self.apollo_client.search_founders(domain)
        
        founders = []
        if founders_data:
            logger.info(f"Found {len(founders_data)} potential founders")
            
            for founder in founders_data:
                # Extract founder info directly from people data
                full_name = founder.get('name', 'Unknown')
                
                # Parse first and last name
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
                
                # Generate personalized email
                if founder_info['email']:
                    logger.info(f"Generating email for founder: {founder_info['name']}")
                    if self.openai_client is None:
                        self.openai_client = OpenAIClient()
                    email_content = self.openai_client.generate_email(
                        company_info, founder_info, classified_industry, owner
                    )
                    founder_info['generated_email'] = email_content
                
                founders.append(founder_info)
                logger.info(f"Added founder: {founder_info['name']} ({founder_info['title']})")
        
        # Determine status
        if founders and any(f.get('email') for f in founders):
            status = "enriched"
            logger.info("Status: enriched - Found company and founders with emails")
        elif founders:
            status = "partial"
            logger.info("Status: partial - Found company and founders but no emails")
        else:
            status = "partial"
            logger.info("Status: partial - Found company but no founders")
        
        result = {
            "status": status,
            "company": company_info,
            "founders": founders,
            "owner": owner
        }
        
        logger.info(f"Enrichment completed with status: {status}")
        return result
