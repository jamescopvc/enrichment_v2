#!/usr/bin/env python3
"""
Test script for specific domains: exactrx.ai and amperefinancial.com
Tests Apollo API integration without requiring OpenAI dependencies
"""

import requests
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Apollo API configuration
APOLLO_API_KEY = 'ltNTfqOJMPcWViTix5tSqg'
APOLLO_BASE_URL = 'https://api.apollo.io/api/v1'

headers = {
    'Cache-Control': 'no-cache',
    'Content-Type': 'application/json',
    'accept': 'application/json',
    'x-api-key': APOLLO_API_KEY
}

def test_company_search(domain):
    """Test Apollo company search for a specific domain"""
    print(f"\n=== Testing Company Search: {domain} ===")
    
    url = f"{APOLLO_BASE_URL}/mixed_companies/search"
    payload = {
        "q_organization_domains": domain
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Apollo API Response Status: {response.status_code}")
        print(f"📊 Raw Response: {json.dumps(data, indent=2)}")
        
        if data.get('organizations') and len(data['organizations']) > 0:
            company = data['organizations'][0]
            print(f"🏢 Company Found:")
            print(f"   Name: {company.get('name', 'Unknown')}")
            print(f"   ID: {company.get('id', 'Unknown')}")
            print(f"   Industry: {company.get('industry', 'Unknown')}")
            print(f"   Location: {company.get('location', 'Unknown')}")
            print(f"   Employee Count: {company.get('employee_count', 'Unknown')}")
            print(f"   LinkedIn: {company.get('linkedin_url', 'Unknown')}")
            print(f"   Description: {company.get('description', 'Unknown')[:200]}...")
            return company
        else:
            print(f"❌ No company found for {domain}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Apollo API Error: {e}")
        return None

def test_founders_search(domain):
    """Test Apollo founders search for a specific domain"""
    print(f"\n=== Testing Founders Search: {domain} ===")
    
    url = f"{APOLLO_BASE_URL}/mixed_people/search"
    payload = {
        "person_titles": ["Co-Founder", "CEO", "CTO"],
        "person_locations": [],
        "person_seniorities": [],
        "q_organization_domains_list": [domain]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Apollo API Response Status: {response.status_code}")
        print(f"📊 Raw Response: {json.dumps(data, indent=2)}")
        
        founders = data.get('people', [])
        print(f"👥 Found {len(founders)} potential founders")
        
        for i, founder in enumerate(founders[:5]):  # Show first 5
            print(f"   {i+1}. {founder.get('name', 'Unknown')} - {founder.get('title', 'Unknown')}")
            print(f"      ID: {founder.get('id', 'Unknown')}")
            print(f"      LinkedIn: {founder.get('linkedin_url', 'Unknown')}")
            print(f"      Email: {founder.get('email', 'Unknown')}")
            print()
        
        return founders
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Apollo API Error: {e}")
        return []

def test_person_enrichment(person_id):
    """Test Apollo person enrichment for a specific person ID"""
    print(f"\n=== Testing Person Enrichment: {person_id} ===")
    
    url = f"{APOLLO_BASE_URL}/people/match"
    payload = {
        "person_id": person_id
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Apollo API Response Status: {response.status_code}")
        print(f"📊 Raw Response: {json.dumps(data, indent=2)}")
        
        person = data.get('person')
        if person:
            print(f"👤 Person Details:")
            print(f"   Name: {person.get('name', 'Unknown')}")
            print(f"   Title: {person.get('title', 'Unknown')}")
            print(f"   Email: {person.get('email', 'Unknown')}")
            print(f"   LinkedIn: {person.get('linkedin_url', 'Unknown')}")
            print(f"   Company: {person.get('organization', {}).get('name', 'Unknown')}")
            return person
        else:
            print(f"❌ No person details found for ID: {person_id}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Apollo API Error: {e}")
        return None

def main():
    """Test specific domains"""
    print("🚀 Testing Company Enrichment for Specific Domains")
    print("=" * 60)
    
    test_domains = ["exactrx.ai", "amperefinancial.com"]
    
    for domain in test_domains:
        print(f"\n{'='*60}")
        print(f"🎯 TESTING DOMAIN: {domain}")
        print(f"{'='*60}")
        
        # Test company search
        company = test_company_search(domain)
        
        if company:
            # Test founders search
            founders = test_founders_search(domain)
            
            # Test person enrichment for first founder if available
            if founders and len(founders) > 0:
                first_founder = founders[0]
                founder_id = first_founder.get('id')
                if founder_id:
                    test_person_enrichment(founder_id)
        
        print(f"\n{'='*60}")
        print(f"✅ COMPLETED TESTING: {domain}")
        print(f"{'='*60}")

if __name__ == "__main__":
    main()
