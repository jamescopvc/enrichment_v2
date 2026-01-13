import requests
import logging
from typing import Dict, Any, Optional
from config import APOLLO_API_KEY, APOLLO_BASE_URL

logger = logging.getLogger(__name__)


class ApolloClient:
    """
    Apollo API client - used as fallback for email lookup when Specter fails.
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

