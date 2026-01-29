import requests
import logging
from typing import Dict, List, Any, Optional
from config import SPECTER_API_KEY, SPECTER_BASE_URL

logger = logging.getLogger(__name__)


class SpecterClient:
    def __init__(self):
        self.api_key = SPECTER_API_KEY
        self.base_url = SPECTER_BASE_URL
        self.headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key
        }
    
    def get_company_by_domain(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Get company info by domain using Specter enrichment API.
        Returns company data including founder_info array.
        """
        url = f"{self.base_url}/companies"
        payload = {"domain": domain}
        
        logger.info(f"Step 0: Getting company info for domain: {domain}")
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            # Handle case where API returns a list of companies
            if isinstance(data, list):
                if not data:
                    logger.warning("Specter API returned empty list")
                    return None
                data = data[0]  # Take first matching company
                logger.info(f"Specter returned list, using first result")
            
            # Debug: log available fields (set to debug level for production)
            logger.debug(f"Specter company fields: {list(data.keys())}")
            
            # Extract location from hq object
            hq = data.get('hq', {})
            location = hq.get('city', '') if isinstance(hq, dict) else 'Unknown'
            if isinstance(hq, dict) and hq.get('region'):
                location = f"{location}, {hq.get('region')}" if location else hq.get('region')
            
            # Extract LinkedIn from socials
            socials = data.get('socials', {})
            linkedin_data = socials.get('linkedin', {}) if isinstance(socials, dict) else {}
            if isinstance(linkedin_data, dict):
                linkedin_url = linkedin_data.get('url', '')
                if linkedin_url and not linkedin_url.startswith('http'):
                    linkedin_url = f"https://{linkedin_url}"
            else:
                linkedin_url = str(linkedin_data) if linkedin_data else ''
            
            # Extract industries
            industries = data.get('industries', [])
            industry = industries[0] if industries else 'Unknown'
            
            company_data = {
                'id': data.get('id'),
                'name': data.get('organization_name', 'Unknown'),
                'domain': data.get('website', domain),
                'description': data.get('description', ''),
                'short_description': data.get('tagline', ''),
                'keywords': data.get('tags', []),
                'industry': industry,
                'location': location or 'Unknown',
                'employee_count': data.get('employee_count', 0),
                'linkedin_url': linkedin_url,
                'website_url': data.get('website', ''),
                'founded_year': data.get('founded_year'),
                'founder_info': data.get('founder_info') or [],
                'investors': data.get('investors') or [],
                'investor_count': data.get('investor_count', 0)
            }
            
            logger.info(f"Company data retrieved: {company_data['name']}")
            logger.info(f"Found {len(company_data['founder_info'])} founders in company data")
            logger.info(f"Found {len(company_data['investors'])} investors in company data")
            return company_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Specter API error for company search: {e}")
            return None
    
    def get_person(self, person_id: str) -> Optional[Dict[str, Any]]:
        """
        Get person profile by Specter person ID.
        Returns full person profile with name, title, linkedin, etc.
        """
        url = f"{self.base_url}/people/{person_id}"
        
        logger.info(f"Getting person details for ID: {person_id}")
        
        try:
            response = requests.get(url, headers=self.headers)
            
            # Handle 202 Accepted (async enrichment in progress)
            if response.status_code == 202:
                logger.warning(f"Person {person_id} enrichment in progress (202 Accepted)")
                return {'status': 'pending', 'person_id': person_id}
            
            response.raise_for_status()
            
            data = response.json()
            
            person_data = {
                'person_id': data.get('person_id'),
                'first_name': data.get('first_name', ''),
                'last_name': data.get('last_name', ''),
                'full_name': data.get('full_name', 'Unknown'),
                'title': data.get('current_position_title', ''),
                'linkedin_url': data.get('linkedin_url', ''),
                'location': data.get('location', ''),
                'about': data.get('about', ''),
                'tagline': data.get('tagline', ''),
                'profile_picture_url': data.get('profile_picture_url'),
                'twitter_url': data.get('twitter_url'),
                'github_url': data.get('github_url'),
                'highlights': data.get('highlights', []),
                'skills': data.get('skills', []),
            }
            
            logger.info(f"Person data retrieved: {person_data['full_name']}")
            return person_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Specter API error for person lookup: {e}")
            return None
    
    def lookup_person_by_linkedin(self, linkedin_url: str) -> Optional[Dict[str, Any]]:
        """
        Create/lookup a person in Specter by LinkedIn URL.
        Returns person data including person_id for email lookup.
        
        Args:
            linkedin_url: The person's LinkedIn profile URL
            
        Returns:
            Dict with person_id, full_name, first_name, last_name, title, linkedin_url
            or None if lookup failed
        """
        if not linkedin_url:
            return None
            
        url = f"{self.base_url}/people"
        payload = {"linkedin_url": linkedin_url}
        
        logger.info(f"Specter: Looking up person by LinkedIn: {linkedin_url}")
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            
            # Handle 202 Accepted (async enrichment in progress)
            if response.status_code == 202:
                data = response.json() if response.text else {}
                person_id = data.get('person_id')
                if person_id:
                    logger.info(f"Specter: Person enrichment pending, got ID: {person_id}")
                    return {'person_id': person_id, 'status': 'pending'}
                logger.warning(f"Specter: Person enrichment pending (202), no ID returned")
                return None
            
            response.raise_for_status()
            
            # Handle empty response
            if not response.text or not response.text.strip():
                logger.warning(f"Specter: Empty response for LinkedIn lookup")
                return None
            
            data = response.json()
            
            person_id = data.get('person_id')
            if not person_id:
                logger.warning(f"Specter: No person_id in response")
                return None
            
            person_data = {
                'person_id': person_id,
                'first_name': data.get('first_name', ''),
                'last_name': data.get('last_name', ''),
                'full_name': data.get('full_name', ''),
                'title': data.get('current_position_title', ''),
                'linkedin_url': data.get('linkedin_url', linkedin_url),
                'status': 'found'
            }
            
            logger.info(f"Specter: Found person {person_data['full_name']} (ID: {person_id})")
            return person_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Specter API error for LinkedIn lookup: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.warning(f"Specter: Invalid response for LinkedIn lookup: {e}")
            return None
    
    def get_person_email(self, person_id: str, email_type: str = "professional") -> Optional[str]:
        """
        Get person's email by Specter person ID.
        
        Args:
            person_id: The Specter person ID
            email_type: 'professional' or 'personal' (defaults to professional)
        
        Returns:
            Email address string or None if not found
        """
        url = f"{self.base_url}/people/{person_id}/email"
        params = {"type": email_type}
        
        logger.info(f"Getting {email_type} email for person ID: {person_id}")
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            
            # Handle 202 Accepted (async enrichment in progress)
            if response.status_code == 202:
                logger.warning(f"Email enrichment in progress for {person_id} (202 Accepted)")
                return None
            
            # Handle 404 - email not found
            if response.status_code == 404:
                logger.warning(f"No {email_type} email found for person {person_id}")
                return None
            
            response.raise_for_status()
            
            # Handle empty response body
            if not response.text or not response.text.strip():
                logger.warning(f"Empty response body for email lookup: {person_id}")
                return None
            
            data = response.json()
            email = data.get('email')
            returned_type = data.get('type', email_type)
            
            if email:
                logger.info(f"Email retrieved: {email} (type: {returned_type})")
            else:
                logger.warning(f"No email in response for person {person_id}")
            
            return email
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Specter API error for email lookup: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.warning(f"Invalid response from Specter email API for {person_id}: {e}")
            return None
    
    def get_founders(self, domain: str) -> List[Dict[str, Any]]:
        """
        Convenience method: Get company by domain and return enriched founder data.
        Combines company lookup with person enrichment for each founder.
        """
        company_data = self.get_company_by_domain(domain)
        if not company_data:
            return []
        
        founder_info = company_data.get('founder_info', [])
        if not founder_info:
            logger.info("No founders found in company data")
            return []
        
        logger.info(f"Enriching {len(founder_info)} founders")
        
        enriched_founders = []
        for founder in founder_info:
            person_id = founder.get('specter_person_id')
            if not person_id:
                logger.warning(f"No person ID for founder: {founder.get('full_name', 'Unknown')}")
                continue
            
            # Get full person details
            person_data = self.get_person(person_id)
            if person_data and person_data.get('status') != 'pending':
                # Get email
                email = self.get_person_email(person_id)
                person_data['email'] = email
                
                # Use title from founder_info if current_position_title is empty
                if not person_data.get('title') and founder.get('title'):
                    person_data['title'] = founder.get('title')
                
                enriched_founders.append(person_data)
            else:
                # Include partial data from founder_info
                enriched_founders.append({
                    'person_id': person_id,
                    'full_name': founder.get('full_name', 'Unknown'),
                    'first_name': founder.get('full_name', '').split()[0] if founder.get('full_name') else '',
                    'last_name': ' '.join(founder.get('full_name', '').split()[1:]) if founder.get('full_name') else '',
                    'title': founder.get('title', ''),
                    'email': None,
                    'linkedin_url': '',
                    'status': 'pending'
                })
        
        return enriched_founders

