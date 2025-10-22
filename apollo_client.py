import requests
import logging
from typing import Dict, List, Any, Optional
from config import APOLLO_API_KEY, APOLLO_BASE_URL

logger = logging.getLogger(__name__)

class ApolloClient:
    def __init__(self):
        self.api_key = APOLLO_API_KEY
        self.base_url = APOLLO_BASE_URL
        self.headers = {
            'accept': 'application/json',
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json',
            'x-api-key': self.api_key
        }
    
    def get_company_by_domain(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Step 0: Get company info by domain
        """
        url = f"{self.base_url}/organizations/enrich?domain={domain}"
        
        logger.info(f"Step 0: Getting company info for domain: {domain}")
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            # Extract from nested organization object
            org = data.get('organization', data)
            
            company_data = {
                'id': org.get('id'),
                'name': org.get('name', 'Unknown'),
                'domain': org.get('primary_domain', domain),
                'description': org.get('short_description', org.get('description', '')),
                'short_description': org.get('short_description', ''),
                'keywords': org.get('keywords', []),
                'industry': org.get('industry', 'Unknown'),
                'location': f"{org.get('city', 'Unknown')}, {org.get('state', '')}".strip(),
                'employee_count': org.get('estimated_num_employees', 0),
                'linkedin_url': org.get('linkedin_url', ''),
                'website_url': org.get('website_url', ''),
                'founded_year': org.get('founded_year')
            }
            
            logger.info(f"Company data retrieved: {company_data['name']}")
            return company_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Apollo API error for company search: {e}")
            return None
    
    def search_founders(self, domain: str) -> List[Dict[str, Any]]:
        """
        Step 1: Search for founders by domain and titles
        """
        url = f"{self.base_url}/mixed_people/search"
        payload = {
            "person_titles": ["CEO", "CTO", "Co-Founder"],
            "q_organization_domains_list": [domain]
        }
        
        logger.info(f"Step 1: Searching for founders at domain: {domain}")
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            # Apollo returns founders in EITHER 'contacts' or 'people' field
            founders = data.get('contacts', [])
            if not founders:
                founders = data.get('people', [])
            
            logger.info(f"Found {len(founders)} potential founders")
            
            return founders
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Apollo API error for founders search: {e}")
            return []
    
    def enrich_person(self, person_id: str) -> Optional[Dict[str, Any]]:
        """
        Step 2: Enrich individual person by person_id
        """
        url = f"{self.base_url}/people/match"
        payload = {
            "id": person_id,
            "reveal_personal_emails": False,
            "reveal_phone_number": False
        }
        
        logger.info(f"Step 2: Enriching person with ID: {person_id}")
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Person enriched: {data.get('name', 'Unknown')}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Apollo API error for person enrichment: {e}")
            return None
