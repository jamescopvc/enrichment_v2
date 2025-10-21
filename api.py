import json
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handler(request):
    """Vercel serverless handler"""
    try:
        # Get request details
        method = request.get('method', 'GET')
        path = request.get('path', '/')
        body = request.get('body', '{}')
        
        # Parse JSON body
        try:
            data = json.loads(body) if body else {}
        except:
            data = {}
        
        # Route requests
        if path == '/enrich' and method == 'POST':
            return handle_enrich(data)
        elif path == '/webhook' and method == 'POST':
            return handle_webhook(data)
        elif path == '/health' and method == 'GET':
            return handle_health()
        else:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"status": "error", "message": "Endpoint not found"})
            }
            
    except Exception as e:
        logger.error(f"Handler error: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"status": "error", "message": "Internal server error"})
        }

def handle_enrich(data):
    """Handle enrichment requests"""
    try:
        if not data:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"status": "error", "message": "No JSON data provided"})
            }
        
        domain = data.get('domain')
        list_source = data.get('list_source')
        
        if not domain:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"status": "error", "message": "Domain is required"})
            }
        
        if not list_source:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"status": "error", "message": "List source is required"})
            }
        
        logger.info(f"Enrichment request: domain={domain}, list_source={list_source}")
        
        # Mock response for testing
        result = {
            "status": "enriched",
            "company": {
                "name": "Test Company",
                "domain": domain,
                "industry": "Technology",
                "location": "San Francisco, CA",
                "employee_count": 100,
                "linkedin": "https://linkedin.com/company/test"
            },
            "founders": [
                {
                    "name": "Test Founder",
                    "title": "CEO & Founder",
                    "email": "founder@test.com",
                    "linkedin": "https://linkedin.com/in/test"
                }
            ],
            "owner": "james@scopvc.com"
        }
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Enrich error: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"status": "error", "message": "Internal server error"})
        }

def handle_webhook(data):
    """Handle webhook requests"""
    try:
        if not data:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"status": "error", "message": "No JSON data provided"})
            }
        
        domain = data.get('domain')
        list_source = data.get('list_source')
        
        if not domain:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"status": "error", "message": "Domain is required"})
            }
        
        if not list_source:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"status": "error", "message": "List source is required"})
            }
        
        logger.info(f"Webhook request: domain={domain}, list_source={list_source}")
        
        # Mock response for testing
        result = {
            "status": "enriched",
            "company": {
                "name": "Test Company",
                "domain": domain,
                "industry": "Technology",
                "location": "San Francisco, CA",
                "employee_count": 100,
                "linkedin": "https://linkedin.com/company/test"
            },
            "founders": [
                {
                    "name": "Test Founder",
                    "title": "CEO & Founder",
                    "email": "founder@test.com",
                    "linkedin": "https://linkedin.com/in/test"
                }
            ],
            "owner": "zi@scopvc.com"
        }
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"status": "error", "message": "Internal server error"})
        }

def handle_health():
    """Handle health check requests"""
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"status": "healthy", "message": "Company enrichment API is running"})
    }