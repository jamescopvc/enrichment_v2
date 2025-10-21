import openai
import logging
from typing import Dict, Any, Optional
from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self):
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    def classify_industry(self, company_data: Dict[str, Any]) -> str:
        """
        Use OpenAI to classify the company's industry/vertical
        """
        company_name = company_data.get('name', 'Unknown')
        company_description = company_data.get('description', '')
        company_industry = company_data.get('industry', '')
        
        prompt = f"""
        Analyze this company and classify its primary industry/vertical:
        
        Company Name: {company_name}
        Description: {company_description}
        Current Industry: {company_industry}
        
        Choose the most appropriate category from these options:
        - Financial Services
        - Construction
        - Proptech
        - AI Infrastructure
        - HealthTech
        - Vertical SaaS
        - Other
        
        Respond with only the category name, nothing else.
        """
        
        logger.info(f"Classifying industry for company: {company_name}")
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # Low temperature for deterministic results
                max_tokens=50
            )
            
            industry = response.choices[0].message.content.strip()
            logger.info(f"Classified industry: {industry}")
            return industry
            
        except Exception as e:
            logger.error(f"OpenAI API error for industry classification: {e}")
            return "Other"
    
    def generate_email(self, company_data: Dict[str, Any], founder_data: Dict[str, Any], 
                      industry: str, owner: str) -> str:
        """
        Generate personalized email using OpenAI
        """
        company_name = company_data.get('name', 'Unknown')
        founder_name = founder_data.get('name', 'Unknown')
        founder_title = founder_data.get('title', '')
        company_location = company_data.get('location', '')
        
        # Get owner-specific calendly link
        from config import CALENDLY_LINKS
        calendly_link = CALENDLY_LINKS.get(owner, '')
        
        # Get sender name based on owner
        sender_name = "James" if owner == "james" else "Zi"
        
        prompt = f"""
        Generate a personalized outreach email for a venture capital fund (ScOp Venture Capital) to a founder.
        
        Company: {company_name}
        Founder: {founder_name} ({founder_title})
        Industry: {industry}
        Location: {company_location}
        Sender: {sender_name}
        Calendly Link: {calendly_link}
        
        Use this base template and personalize it:
        
        Hi [FirstName],
        
        I just came across you guys and wanted to introduce our fund, ScOp Venture Capital - our team all comes from operating backgrounds in software, and we lead pre-seed through Series A rounds in vertical software and AI.
        
        [Company Name] looks really interesting, I would love to learn more about the business and what you've built.
        
        Any times work to chat in the next few weeks? [Calendly Link]
        
        All the best!
        
        [Sender Name]
        
        Add industry-specific content from these templates:
        - Financial Services: "We have experience with companies in financial services - our portfolio company Rogo raised a $50m Series B from Thrive building a full AI suite for banks and large financial institutions."
        - Construction: "We have deep experience and network in construction - our partner Kevin wrote the first check to Procore, and we have the CEO and lots of early Procore employees as LPs."
        - Proptech: "We have strong experience in proptech, and have the founders of Appfolio and Procore as LPs."
        - AI Infrastructure: "Our partners Kevin and Ivan built and sold the knowledge graph software that powered Amazon Alexa, and we have founders of MongoDB, Twilio, DoubleClick, and more as LPs."
        - HealthTech: "We have some experience in healthcare - our portfolio includes a patient communications company, an RCM platform, and a consumer health tracking app."
        - Vertical SaaS: "Our partner Kevin founded DoubleClick (sold to Google), and Graphiq (sold to Amazon) - we have the founders of Procore, Appfolio, MongoDB, Twilio, and more as LPs."
        
        Add location-specific content:
        - New York: "We have several portcos in New York as well (Rogo, Promptlayer, Pangram Labs, SuiteOp)."
        - Southern California: "We're based in Santa Barbara and have pretty good local coverage and network throughout SoCal."
        
        Generate the complete email with proper personalization.
        """
        
        logger.info(f"Generating email for {founder_name} at {company_name}")
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,  # Higher temperature for creative email generation
                max_tokens=500
            )
            
            email = response.choices[0].message.content.strip()
            logger.info(f"Generated email for {founder_name}")
            return email
            
        except Exception as e:
            logger.error(f"OpenAI API error for email generation: {e}")
            return f"Hi {founder_name},\n\nI just came across you guys and wanted to introduce our fund, ScOp Venture Capital.\n\n{company_name} looks really interesting, I would love to learn more about the business and what you've built.\n\nAny times work to chat in the next few weeks? {calendly_link}\n\nAll the best!\n{sender_name}"
