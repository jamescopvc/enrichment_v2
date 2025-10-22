#!/usr/bin/env python3
"""
Simple CLI test tool for Company Enrichment API
Usage: python test.py [command] [args]
"""

import sys
import json
import logging
from apollo_client import ApolloClient
from openai_client import OpenAIClient
from enrichment_logic import EnrichmentService

# Suppress external logging, only show our output
logging.getLogger('openai').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)

def print_header(text):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def print_step(step_num, title):
    """Print a step header"""
    print(f"\n[Step {step_num}] {title}")
    print("-" * 60)

def print_success(msg):
    """Print success message"""
    print(f"✅ {msg}")

def print_error(msg):
    """Print error message"""
    print(f"❌ {msg}")

def print_info(msg):
    """Print info message"""
    print(f"ℹ️  {msg}")

def test_full_pipeline(domain, list_source):
    """Test complete enrichment pipeline"""
    print_header(f"Testing: {domain} ({list_source})")
    
    # Step 0: Company Search
    print_step(0, "Company Search")
    apollo = ApolloClient()
    company_data = apollo.get_company_by_domain(domain)
    
    if not company_data:
        print_error(f"Company not found for domain: {domain}")
        return
    
    company_name = company_data.get('name')
    print_success(f"Found company: {company_name}")
    
    # Step 1: Vertical Classification
    print_step(1, "Vertical Classification")
    openai_client = OpenAIClient()
    industry = openai_client.classify_industry(company_data)
    print_success(f"Classified as: {industry}")
    
    # Step 2: Founder Search
    print_step(2, "Founder Search")
    founders_data = apollo.search_founders(domain)
    print_success(f"Found {len(founders_data)} potential founders")
    
    if not founders_data:
        print_error("No founders found")
        return
    
    # Step 3: Founder Enrichment
    print_step(3, "Founder Enrichment & Email Generation")
    
    enriched_founders = []
    for i, founder in enumerate(founders_data, 1):
        full_name = founder.get('name', 'Unknown')
        title = founder.get('title', '')
        email = founder.get('email', '')
        person_id = founder.get('id')
        
        print_info(f"  [{i}] {full_name} - {title}")
        
        # Check if email is available
        if email and email != 'email_not_unlocked@domain.com':
            print_success(f"     Email available: {email}")
        else:
            # Try to enrich
            if person_id:
                enriched = apollo.enrich_person(person_id)
                if enriched and enriched.get('email') and enriched.get('email') != 'email_not_unlocked@domain.com':
                    email = enriched.get('email')
                    print_success(f"     Email enriched: {email}")
                else:
                    print_error(f"     Email enrichment failed")
                    continue
            else:
                print_error(f"     No person ID to enrich")
                continue
        
        # Build founder info
        name_parts = full_name.split(' ', 1) if full_name != 'Unknown' else ['Unknown', '']
        first_name = name_parts[0] if name_parts else 'Unknown'
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        founder_info = {
            "name": full_name,
            "first_name": first_name,
            "last_name": last_name,
            "title": title,
            "email": email,
            "linkedin": founder.get('linkedin_url', '')
        }
        
        # Generate email
        company_info = {
            "name": company_name,
            "domain": domain,
            "industry": industry,
            "location": company_data.get('location', 'Unknown'),
            "employee_count": company_data.get('employee_count', 0),
            "linkedin": company_data.get('linkedin_url', ''),
            "description": company_data.get('description', '')
        }
        
        # Determine owner from list_source
        owner_name = list_source.split('-')[0]
        owner = f"{owner_name}@scopvc.com"
        
        email_content = openai_client.generate_email(
            company_info, founder_info, industry, owner
        )
        founder_info['generated_email'] = email_content
        
        enriched_founders.append(founder_info)
    
    # Final output
    print_header("RESULTS")
    
    if enriched_founders:
        result_status = "enriched"
        print_success(f"Status: {result_status.upper()}")
    else:
        result_status = "failed"
        print_error(f"Status: {result_status.upper()}")
    
    print_info(f"Company: {company_name}")
    print_info(f"Vertical: {industry}")
    print_info(f"Founders found: {len(enriched_founders)}")
    
    if enriched_founders:
        print_info("\nFounders:")
        for i, founder in enumerate(enriched_founders, 1):
            print(f"  [{i}] {founder['first_name']} {founder['last_name']}")
            print(f"      Title: {founder['title']}")
            print(f"      Email: {founder['email']}")
            print(f"      Email preview: {founder['generated_email'][:80]}...")
    
    print()

def main():
    if len(sys.argv) < 2:
        print("Usage: python test.py full <domain> <list_source>")
        print("\nExample:")
        print("  python test.py full exactrx.ai james-test")
        print("  python test.py full besolo.io zi-test")
        return
    
    command = sys.argv[1].lower()
    
    if command == "full" and len(sys.argv) >= 4:
        domain = sys.argv[2]
        list_source = sys.argv[3]
        test_full_pipeline(domain, list_source)
    else:
        print("❌ Invalid command or missing arguments")
        print("Usage: python test.py full <domain> <list_source>")

if __name__ == "__main__":
    main()
