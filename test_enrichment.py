#!/usr/bin/env python3
"""
Test script for company enrichment without starting the full app
This allows easy debugging and testing of individual components
"""

import logging
import json
from enrichment_logic import EnrichmentService
from apollo_client import ApolloClient
from openai_client import OpenAIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_apollo_company_search():
    """Test Apollo company search functionality"""
    print("\n=== Testing Apollo Company Search ===")
    
    apollo = ApolloClient()
    
    # Test domains
    test_domains = [
        "openai.com",
        "stripe.com", 
        "usecervo.com",
        "nonexistent-domain-12345.com"
    ]
    
    for domain in test_domains:
        print(f"\nTesting domain: {domain}")
        company = apollo.search_company_by_domain(domain)
        
        if company:
            print(f"✅ Found company: {company.get('name')} (ID: {company.get('id')})")
            print(f"   Industry: {company.get('industry')}")
            print(f"   Location: {company.get('location')}")
            print(f"   Employee Count: {company.get('employee_count')}")
        else:
            print(f"❌ No company found for {domain}")

def test_apollo_founders_search():
    """Test Apollo founders search functionality"""
    print("\n=== Testing Apollo Founders Search ===")
    
    apollo = ApolloClient()
    
    # Test with a known domain
    domain = "usecervo.com"
    print(f"\nTesting founders search for: {domain}")
    
    founders = apollo.search_founders(domain)
    
    if founders:
        print(f"✅ Found {len(founders)} potential founders")
        for i, founder in enumerate(founders[:3]):  # Show first 3
            print(f"   {i+1}. {founder.get('name', 'Unknown')} - {founder.get('title', 'Unknown')}")
    else:
        print(f"❌ No founders found for {domain}")

def test_openai_classification():
    """Test OpenAI industry classification"""
    print("\n=== Testing OpenAI Industry Classification ===")
    
    openai_client = OpenAIClient()
    
    # Test with sample company data
    test_companies = [
        {
            "name": "OpenAI",
            "description": "AI research company focused on artificial general intelligence",
            "industry": "Technology"
        },
        {
            "name": "Stripe",
            "description": "Online payment processing platform for internet businesses",
            "industry": "Financial Services"
        }
    ]
    
    for company in test_companies:
        print(f"\nTesting classification for: {company['name']}")
        industry = openai_client.classify_industry(company)
        print(f"✅ Classified as: {industry}")

def test_openai_email_generation():
    """Test OpenAI email generation"""
    print("\n=== Testing OpenAI Email Generation ===")
    
    openai_client = OpenAIClient()
    
    # Test data
    company_data = {
        "name": "Test Company",
        "location": "San Francisco, CA",
        "industry": "AI Infrastructure"
    }
    
    founder_data = {
        "name": "John Doe",
        "title": "CEO & Founder",
        "email": "john@testcompany.com"
    }
    
    print(f"\nGenerating email for: {founder_data['name']} at {company_data['name']}")
    
    email = openai_client.generate_email(company_data, founder_data, "AI Infrastructure", "james")
    print(f"✅ Generated email:\n{email}")

def test_full_enrichment():
    """Test the complete enrichment process"""
    print("\n=== Testing Full Enrichment Process ===")
    
    enrichment_service = EnrichmentService()
    
    # Test cases
    test_cases = [
        {
            "domain": "usecervo.com",
            "list_source": "james-test-list"
        },
        {
            "domain": "openai.com", 
            "list_source": "zi-test-list"
        },
        {
            "domain": "nonexistent-domain-12345.com",
            "list_source": "james-test-list"
        },
        {
            "domain": "stripe.com",
            "list_source": "invalid-list-source"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- Testing: {test_case['domain']} with list_source: {test_case['list_source']} ---")
        
        result = enrichment_service.enrich_company(
            test_case['domain'], 
            test_case['list_source']
        )
        
        print(f"Status: {result['status']}")
        
        if result['status'] == 'enriched':
            print(f"✅ Company: {result['company']['name']}")
            print(f"   Industry: {result['company']['industry']}")
            print(f"   Founders: {len(result['founders'])}")
            for founder in result['founders']:
                print(f"     - {founder['name']} ({founder['title']})")
                if founder.get('email'):
                    print(f"       Email: {founder['email']}")
        elif result['status'] == 'partial':
            print(f"⚠️  Company: {result['company']['name']} (no founder emails)")
        elif result['status'] == 'failed':
            print(f"❌ Company not found")
        elif result['status'] == 'invalid':
            print(f"❌ Invalid list source")

def test_list_source_validation():
    """Test list source validation logic"""
    print("\n=== Testing List Source Validation ===")
    
    enrichment_service = EnrichmentService()
    
    test_sources = [
        "james-test-list",
        "zi-sales-team",
        "james-venture-capital",
        "zi-portfolio",
        "invalid-source",
        "other-team"
    ]
    
    for source in test_sources:
        is_valid, owner = enrichment_service.validate_list_source(source)
        print(f"Source: {source} -> Valid: {is_valid}, Owner: {owner}")

def main():
    """Run all tests"""
    print("🚀 Starting Company Enrichment API Tests")
    print("=" * 50)
    
    try:
        # Test individual components
        test_apollo_company_search()
        test_apollo_founders_search()
        test_openai_classification()
        test_openai_email_generation()
        test_list_source_validation()
        
        # Test full enrichment process
        test_full_enrichment()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logger.error(f"Test error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
