import requests
import logging
from typing import Dict, Any, Optional, List
from config import APOLLO_API_KEY, APOLLO_BASE_URL

logger = logging.getLogger(__name__)


class ApolloClient:
    """
    Apollo API client - used as fallback for:
    1. Founder search when Specter has no founders
    2. Email lookup when Specter email fails
    """
    
    def __init__(self):
        self.api_key = APOLLO_API_KEY
        self.base_url = APOLLO_BASE_URL
        self.headers = {
            'accept': 'application/json',
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json',
            'x-api-key': self.api_key
        }
        
        # Founder titles to search for
        self.founder_titles = [
            'founder',
            'co-founder', 
            'cofounder',
            'CEO',
            'CTO',
            'Chief Executive Officer',
            'Chief Technology Officer'
        ]
    
    def search_founders(self, domain: str) -> List[Dict[str, Any]]:
        """
        Search for founders/executives at a company by domain.
        Used as fallback when Specter has no founder data.
        
        Args:
            domain: Company domain (e.g. 'buildern.com')
            
        Returns:
            List of founder dicts with name, title, email, linkedin_url, etc.
        """
        if not self.api_key or not domain:
            return []
        
        # Build query params
        params = {
            'q_organization_domains_list[]': domain
        }
        # Add title filters
        for title in self.founder_titles:
            params.setdefault('person_titles[]', [])
            if isinstance(params['person_titles[]'], list):
                params['person_titles[]'].append(title)
        
        url = f"{self.base_url}/mixed_people/api_search"
        
        logger.info(f"Apollo fallback: Searching for founders at {domain}")
        
        try:
            response = requests.post(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            people = data.get('people', [])
            
            if not people:
                logger.warning(f"Apollo fallback: No founders found for {domain}")
                return []
            
            logger.info(f"Apollo fallback: Found {len(people)} potential founders at {domain}")
            
            founders = []
            for person in people:
                apollo_id = person.get('id')
                title = person.get('title', '')
                first_name = person.get('first_name', '')
                
                logger.info(f"   - {first_name} ({title}) - enriching...")
                
                # Enrich by ID to get full data (LinkedIn URL, last name, email)
                if apollo_id:
                    enriched = self.enrich_person_by_id(apollo_id)
                    if enriched:
                        founders.append(enriched)
                        continue
                
                # Fallback to basic data if enrichment fails
                last_name = person.get('last_name', '')
                full_name = f"{first_name} {last_name}".strip() or 'Unknown'
                
                founder_data = {
                    'full_name': full_name,
                    'first_name': first_name,
                    'last_name': last_name,
                    'title': title,
                    'email': None,
                    'linkedin_url': '',
                    'apollo_id': apollo_id,
                    'source': 'apollo'
                }
                founders.append(founder_data)
                logger.info(f"   - {full_name} ({title}) - using basic data")
            
            return founders
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Apollo founder search error: {e}")
            return []
        except (ValueError, KeyError) as e:
            logger.warning(f"Apollo founder search parse error: {e}")
            return []
    
    def enrich_person_by_id(self, apollo_id: str) -> Optional[Dict[str, Any]]:
        """
        Enrich a person by their Apollo ID to get full data including LinkedIn URL and email.
        
        Args:
            apollo_id: The Apollo person ID from search results
            
        Returns:
            Dict with full person data or None if not found
        """
        if not self.api_key or not apollo_id:
            return None
        
        url = f"{self.base_url}/people/match"
        params = {
            'id': apollo_id,
            'reveal_personal_emails': 'false',
            'reveal_phone_number': 'false'
        }
        
        logger.info(f"Apollo: Enriching person by ID {apollo_id}")
        
        try:
            response = requests.post(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            person = data.get('person')
            
            if not person:
                logger.warning(f"Apollo: No person data for ID {apollo_id}")
                return None
            
            # Extract email (filter out placeholder)
            email = person.get('email')
            if email == 'email_not_unlocked@domain.com':
                email = None
            
            result = {
                'apollo_id': apollo_id,
                'first_name': person.get('first_name', ''),
                'last_name': person.get('last_name', ''),
                'full_name': person.get('name', ''),
                'title': person.get('title', ''),
                'email': email,
                'linkedin_url': person.get('linkedin_url', ''),
                'source': 'apollo'
            }
            
            logger.info(f"Apollo: Enriched {result['full_name']} | Email: {email or 'N/A'} | LinkedIn: {'✓' if result['linkedin_url'] else 'N/A'}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Apollo enrich by ID error: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.warning(f"Apollo enrich by ID parse error: {e}")
            return None
    
    def get_email_by_linkedin(self, linkedin_url: str) -> Optional[str]:
        """
        Look up a person's email by their LinkedIn URL using Apollo's people/match endpoint.
        
        Args:
            linkedin_url: The person's LinkedIn profile URL
            
        Returns:
            Email address string or None if not found
        """
        if not linkedin_url or not self.api_key:
            return None
            
        url = f"{self.base_url}/people/match"
        payload = {
            "linkedin_url": linkedin_url,
            "reveal_personal_emails": False,
            "reveal_phone_number": False
        }
        
        logger.info(f"Apollo fallback: Looking up email for {linkedin_url}")
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            person = data.get('person')
            
            if person:
                email = person.get('email')
                if email and email != 'email_not_unlocked@domain.com':
                    logger.info(f"Apollo fallback: Found email {email}")
                    return email
                else:
                    logger.warning(f"Apollo fallback: No valid email in response")
                    return None
            else:
                logger.warning(f"Apollo fallback: No person data in response")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Apollo fallback error: {e}")
            return None
    
    def enrich_person(self, first_name: str, last_name: str, domain: str) -> Optional[str]:
        """
        Alternative lookup: find email by name and company domain.
        
        Args:
            first_name: Person's first name
            last_name: Person's last name
            domain: Company domain
            
        Returns:
            Email address string or None if not found
        """
        if not self.api_key:
            return None
            
        url = f"{self.base_url}/people/match"
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "organization_domain": domain,
            "reveal_personal_emails": False,
            "reveal_phone_number": False
        }
        
        logger.info(f"Apollo fallback: Looking up {first_name} {last_name} at {domain}")
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            person = data.get('person')
            
            if person:
                email = person.get('email')
                if email and email != 'email_not_unlocked@domain.com':
                    logger.info(f"Apollo fallback: Found email {email}")
                    return email
                    
            return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Apollo fallback error: {e}")
            return None


