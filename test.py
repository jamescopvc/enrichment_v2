#!/usr/bin/env python3
"""
Simple CLI test tool for Company Enrichment API
Usage: python test.py [command] [args]
"""

import sys
import logging
from enrichment_logic import EnrichmentService

# Configure logging to show enrichment steps
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

# Suppress noisy external loggers
logging.getLogger('openai').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)

def print_header(text):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

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
    """Test complete enrichment pipeline using EnrichmentService (Specter-based)"""
    print_header(f"Testing: {domain} ({list_source})")
    print_info("Using Specter API (production flow)")
    print()
    
    # Use the actual EnrichmentService (same as production)
    service = EnrichmentService()
    result = service.enrich_company(domain, list_source)
    
    # Display results
    print_header("RESULTS")
    
    status = result.get('status', 'unknown')
    if status == 'enriched':
        print_success(f"Status: {status.upper()}")
    elif status == 'partial':
        print_info(f"Status: {status.upper()}")
    else:
        print_error(f"Status: {status.upper()}")
    
    if result.get('message'):
        print_info(f"Message: {result['message']}")
    
    company = result.get('company', {})
    if company:
        print_info(f"Company: {company.get('name', 'Unknown')}")
        print_info(f"Industry: {company.get('industry', 'Unknown')}")
        print_info(f"Location: {company.get('location', 'Unknown')}")
    
    print_info(f"Owner: {result.get('owner', 'Unknown')}")
    
    founders = result.get('founders', [])
    print_info(f"Founders found: {len(founders)}")
    
    if founders:
        print_info("\nFounders:")
        for i, founder in enumerate(founders, 1):
            print(f"  [{i}] {founder.get('first_name', '')} {founder.get('last_name', '')}")
            print(f"      Title: {founder.get('title', 'N/A')}")
            print(f"      Email: {founder.get('email', 'N/A')}")
            print(f"      LinkedIn: {founder.get('linkedin', 'N/A')}")
            if founder.get('generated_email'):
                preview = founder['generated_email'][:80].replace('\n', ' ')
                print(f"      Email preview: {preview}...")
    
    # Show investors
    investors = []
    for i in range(1, 4):
        name = result.get(f'investor_{i}_name', '')
        domain = result.get(f'investor_{i}_domain', '')
        if name:
            investors.append({'name': name, 'domain': domain})
    
    if investors:
        print_info(f"\nTop Investors ({len(investors)}):")
        for i, inv in enumerate(investors, 1):
            print(f"  [{i}] {inv['name']} -> {inv['domain'] or 'no domain'}")
    
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
