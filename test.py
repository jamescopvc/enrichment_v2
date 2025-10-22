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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_company_search(domain):
    """Test Step 0: Company search by domain"""
    print(f"\n🔍 Testing Step 0: Company search for {domain}")
    print("=" * 50)
    
    apollo = ApolloClient()
    result = apollo.get_company_by_domain(domain)
    
    if result:
        print(f"✅ Company found: {result.get('name', 'Unknown')}")
        print(f"   Domain: {result.get('primary_domain', 'Unknown')}")
        print(f"   Industry: {result.get('industry', 'Unknown')}")
        print(f"   Location: {result.get('location', 'Unknown')}")
        print(f"   Employee Count: {result.get('employee_count', 'Unknown')}")
        print(f"   LinkedIn: {result.get('linkedin_url', 'Unknown')}")
        return result
    else:
        print("❌ Company not found")
        return None

def test_founder_search(domain):
    """Test Step 1: Founder search by domain"""
    print(f"\n👥 Testing Step 1: Founder search for {domain}")
    print("=" * 50)
    
    apollo = ApolloClient()
    founders = apollo.search_founders(domain)
    
    if founders:
        print(f"✅ Found {len(founders)} founders:")
        for i, founder in enumerate(founders, 1):
            print(f"   {i}. {founder.get('name', 'Unknown')} - {founder.get('title', 'Unknown')}")
            print(f"      Email: {founder.get('email', 'Unknown')}")
            print(f"      LinkedIn: {founder.get('linkedin_url', 'Unknown')}")
        return founders
    else:
        print("❌ No founders found")
        return []

def test_person_enrichment(person_id):
    """Test Step 2: Person enrichment by ID"""
    print(f"\n🔧 Testing Step 2: Person enrichment for ID {person_id}")
    print("=" * 50)
    
    apollo = ApolloClient()
    result = apollo.enrich_person(person_id)
    
    if result:
        print(f"✅ Person enriched: {result.get('name', 'Unknown')}")
        print(f"   Email: {result.get('email', 'Unknown')}")
        print(f"   Title: {result.get('title', 'Unknown')}")
        print(f"   LinkedIn: {result.get('linkedin_url', 'Unknown')}")
        return result
    else:
        print("❌ Person enrichment failed")
        return None

def test_industry_classification(company_data):
    """Test OpenAI industry classification"""
    print(f"\n🤖 Testing Industry Classification")
    print("=" * 50)
    
    openai_client = OpenAIClient()
    industry = openai_client.classify_industry(company_data)
    
    print(f"✅ Classified industry: {industry}")
    return industry

def test_email_generation(company_data, founder_data, industry, owner):
    """Test OpenAI email generation"""
    print(f"\n📧 Testing Email Generation")
    print("=" * 50)
    
    openai_client = OpenAIClient()
    email = openai_client.generate_email(company_data, founder_data, industry, owner)
    
    print(f"✅ Email generated:")
    print("-" * 30)
    print(email)
    print("-" * 30)
    return email

def test_full_pipeline(domain, list_source):
    """Test complete enrichment pipeline"""
    print(f"\n🚀 Testing Full Pipeline: {domain} ({list_source})")
    print("=" * 60)
    
    service = EnrichmentService()
    result = service.enrich_company(domain, list_source)
    
    print(f"✅ Pipeline result:")
    print(json.dumps(result, indent=2))
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python test.py [command] [args]")
        print("\nCommands:")
        print("  company <domain>           - Test company search")
        print("  founders <domain>          - Test founder search")
        print("  enrich <person_id>         - Test person enrichment")
        print("  industry <domain>          - Test industry classification")
        print("  email <domain> <list_source> - Test email generation")
        print("  full <domain> <list_source>   - Test full pipeline")
        print("\nExamples:")
        print("  python test.py company baselinesoftware.com")
        print("  python test.py founders baselinesoftware.com")
        print("  python test.py full baselinesoftware.com james-test")
        return
    
    command = sys.argv[1].lower()
    
    if command == "company" and len(sys.argv) >= 3:
        domain = sys.argv[2]
        test_company_search(domain)
    
    elif command == "founders" and len(sys.argv) >= 3:
        domain = sys.argv[2]
        test_founder_search(domain)
    
    elif command == "enrich" and len(sys.argv) >= 3:
        person_id = sys.argv[2]
        test_person_enrichment(person_id)
    
    elif command == "industry" and len(sys.argv) >= 3:
        domain = sys.argv[2]
        company_data = test_company_search(domain)
        if company_data:
            test_industry_classification(company_data)
    
    elif command == "email" and len(sys.argv) >= 4:
        domain = sys.argv[2]
        list_source = sys.argv[3]
        
        # Get company data
        company_data = test_company_search(domain)
        if not company_data:
            return
        
        # Get founders
        founders = test_founder_search(domain)
        if not founders:
            return
        
        # Classify industry
        industry = test_industry_classification(company_data)
        
        # Test email generation for first founder
        founder = founders[0]
        owner = "james@scopvc.com" if list_source.startswith("james") else "zi@scopvc.com"
        test_email_generation(company_data, founder, industry, owner)
    
    elif command == "full" and len(sys.argv) >= 4:
        domain = sys.argv[2]
        list_source = sys.argv[3]
        test_full_pipeline(domain, list_source)
    
    else:
        print("❌ Invalid command or missing arguments")
        print("Use 'python test.py' to see usage")

if __name__ == "__main__":
    main()
