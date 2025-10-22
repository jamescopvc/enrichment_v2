import openai
import logging
import json
from typing import Dict, Any
from config import OPENAI_API_KEY, CALENDLY_LINKS

logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=OPENAI_API_KEY,
            timeout=30.0
        )
        self.model = "gpt-4o-mini"
    
    def classify_industry(self, company_data: Dict[str, Any]) -> str:
        """
        Stage 1: Analyze company to determine vertical for personalization
        """
        logger.info(f"Stage 1: Analyzing company - {company_data.get('name')}")
        
        # Format keywords for the prompt
        keywords_str = ", ".join(company_data.get('keywords', [])[:10]) if company_data.get('keywords') else "None"
        
        prompt = f"""Analyze company data to determine applicable vertical for ScOp VC's cold emails.

Company: {company_data.get('name')}
Location: {company_data.get('location')}
Industry: {company_data.get('industry')}
Description: {company_data.get('description', '')}
Keywords: {keywords_str}

Return ONLY a JSON object:
{{
  "vertical": "string or null"
}}

Vertical must be ONE of: "Financial Services", "Construction", "Proptech", "AI Infrastructure", "HealthTech", "Vertical SaaS", or null

RULES:
- HealthTech: healthcare, hospitals, clinical, medical, patient care, surgery centers, healthcare operations
- Financial Services: fintech, banking, payments, lending, insurance, accounting
- Construction: construction tech, contractors, building, BIM, project management for construction
- Proptech: property management, real estate tech, facility management (NOT construction)
- AI Infrastructure: LLM, vector databases, AI/ML ops, foundation models, knowledge graphs
- Vertical SaaS: Any B2B SaaS targeting specific industry not above
- null: if unclear or consumer software

Return ONLY the JSON, no markdown or explanation."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=50,
                seed=42
            )
            
            raw_content = response.choices[0].message.content.strip()
            # Clean markdown
            if raw_content.startswith('```'):
                raw_content = raw_content.split('```')[1].strip()
                if raw_content.startswith('json'):
                    raw_content = raw_content[4:].strip()
            
            result = json.loads(raw_content)
            vertical = result.get('vertical')
            
            logger.info(f"Stage 1 complete - Vertical: {vertical}")
            return vertical or "Other"
            
        except Exception as e:
            logger.error(f"Stage 1 error: {e}")
            return "Other"
    
    def generate_email(self, company_data: Dict[str, Any], founder_data: Dict[str, Any], 
                      industry: str, owner: str) -> str:
        """
        Stage 2: Generate email using exact deterministic templates
        """
        company_name = company_data.get('name', 'Unknown')
        founder_first_name = founder_data.get('first_name', 'Unknown')
        location = company_data.get('location', '')
        
        # Extract location if it matches
        location_match = None
        if location:
            if 'New York' in location or 'New York' in location:
                location_match = 'New York'
            elif any(city in location for city in ['Los Angeles', 'San Diego', 'Santa Barbara', 'San Luis Obispo']):
                location_match = 'Southern California'
        
        # Get owner info
        owner_name = owner.split('@')[0] if '@' in owner else owner
        calendly_link = CALENDLY_LINKS.get(owner_name, '')
        sender_name = "James" if owner_name == "james" else "Zi"
        
        logger.info(f"Stage 2: Generating email for {founder_first_name} at {company_name}")
        logger.info(f"  Industry: {industry}, Location: {location_match}, Owner: {sender_name}")
        
        # Build the email using exact templates
        email = self._build_email_from_template(
            company_name=company_name,
            founder_first_name=founder_first_name,
            vertical=industry,
            location=location_match,
            calendly_link=calendly_link,
            sender_name=sender_name
        )
        
        logger.info("Stage 2 complete - Email generated")
        return email
    
    def _build_email_from_template(self, company_name, founder_first_name, vertical, location, 
                                   calendly_link, sender_name):
        """
        Build email using exact deterministic templates - NO creativity
        """
        # Stage 1: Greeting
        greeting = f"Hi {founder_first_name}," if founder_first_name and founder_first_name != 'Unknown' else "Hi there,"
        
        # Stage 2: Build opening paragraph with vertical-specific content
        opening = "I just came across you guys and wanted to introduce our fund, ScOp Venture Capital - our team all comes from operating backgrounds in software, and we lead pre-seed through Series A rounds in vertical software and AI."
        
        # Add vertical-specific content
        vertical_additions = {
            "Financial Services": "We have experience with companies in financial services - our portfolio company Rogo raised a $50m Series B from Thrive building a full AI suite for banks and large financial institutions.",
            "Construction": "We have deep experience and network in construction - our partner Kevin wrote the first check to Procore, and we have the CEO and lots of early Procore employees as LPs.",
            "Proptech": "We have strong experience in proptech, and have the founders of Appfolio and Procore as LPs.",
            "AI Infrastructure": "Our partners Kevin and Ivan built and sold the knowledge graph software that powered Amazon Alexa, and we have founders of MongoDB, Twilio, DoubleClick, and more as LPs.",
            "HealthTech": "We have some experience in healthcare - our portfolio includes a patient communications company, an RCM platform, and a consumer health tracking app.",
            "Vertical SaaS": "Our partner Kevin founded DoubleClick (sold to Google), and Graphiq (sold to Amazon) - we have the founders of Procore, Appfolio, MongoDB, Twilio, and more as LPs.",
        }
        
        if vertical in vertical_additions:
            opening += " " + vertical_additions[vertical]
        
        # Add location-specific content
        location_additions = {
            "New York": "We have several portcos in New York as well (Rogo, Promptlayer, Pangram Labs, SuiteOp).",
            "Southern California": "We're based in Santa Barbara and have pretty good local coverage and network throughout SoCal.",
        }
        
        if location in location_additions:
            opening += " " + location_additions[location]
        
        # Stage 3: Company interest
        company_interest = f"{company_name} looks really interesting, I would love to learn more about the business and what you've built."
        
        # Stage 4: CTA
        cta = f"Any times work to chat in the next few weeks? {calendly_link}"
        
        # Stage 5: Sign-off
        sign_off = f"All the best!\n\n{sender_name}"
        
        # Assemble the email
        email = f"{greeting}\n\n{opening}\n\n{company_interest}\n\n{cta}\n\n{sign_off}"
        
        return email
