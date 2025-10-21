import requests
import logging
from typing import Dict, List, Optional, Any
from config import APOLLO_API_KEY, APOLLO_BASE_URL

logger = logging.getLogger(__name__)

class ApolloClient:
    def __init__(self):
        self.api_key = APOLLO_API_KEY
        self.base_url = APOLLO_BASE_URL
        self.headers = {
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json',
            'accept': 'application/json',
            'x-api-key': self.api_key
        }
    
    def search_company_by_domain(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Search for company by domain using Apollo API
        """
        url = f"{self.base_url}/mixed_companies/search"
        payload = {
            "q_organization_domains": domain
        }
        
        logger.info(f"Searching for company with domain: {domain}")
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Apollo company search response: {data}")
            
            if data.get('organizations') and len(data['organizations']) > 0:
                company = data['organizations'][0]
                logger.info(f"Found company: {company.get('name', 'Unknown')} (ID: {company.get('id')})")
                return company
            else:
                logger.warning(f"No company found for domain: {domain}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Apollo API error for company search: {e}")
            return None
    
    def search_founders(self, company_id: str) -> List[Dict[str, Any]]:
        """
        Search for founders at a company using the provided Apollo endpoint
        """
        url = f"{self.base_url}/mixed_people/search"
        payload = {
            "person_titles": ["Co-Founder", "CEO", "CTO"],
            "person_locations": [],
            "person_seniorities": [],
            "q_organization_domains_list": [company_id]
        }
        
        logger.info(f"Searching for founders at company ID: {company_id}")
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Apollo founders search response: {data}")
            
            founders = data.get('people', [])
            logger.info(f"Found {len(founders)} potential founders")
            
            return founders
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Apollo API error for founders search: {e}")
            return []
    
    def enrich_person(self, person_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed person information including email
        """
        url = f"{self.base_url}/people/match"
        payload = {
            "person_id": person_id
        }
        
        logger.info(f"Enriching person with ID: {person_id}")
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Apollo person enrichment response: {data}")
            
            return data.get('person')
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Apollo API error for person enrichment: {e}")
            return None
