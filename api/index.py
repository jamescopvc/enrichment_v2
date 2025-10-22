import json
import logging
import sys
import os

# Add parent directory to path so we can import enrichment_logic
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enrichment_logic import EnrichmentService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def handler(request):
    """
    Main API handler for Vercel
    """
    try:
        # Get the path to determine which endpoint to call
        path = request.get('path', '')
        method = request.get('method', 'GET')
        
        # Route to appropriate handler
        if path == '/enrich' and method == 'POST':
            return handle_enrich(request)
        elif path == '/webhook' and method == 'POST':
            return handle_webhook(request)
        elif path == '/health' and method == 'GET':
            return handle_health(request)
        else:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "status": "error",
                    "message": "Endpoint not found"
                })
            }
            
    except Exception as e:
        logger.error(f"Error in main handler: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "status": "error",
                "message": "Internal server error"
            })
        }

def handle_enrich(request):
    """Handle enrichment requests"""
    try:
        # Parse request data
        data = request.get_json() if hasattr(request, 'get_json') else json.loads(request.get('body', '{}'))
        if not data:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "status": "error",
                    "message": "No JSON data provided"
                })
            }
        
        domain = data.get('domain')
        list_source = data.get('list_source')
        
        if not domain:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "status": "error",
                    "message": "Domain is required"
                })
            }
        
        if not list_source:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "status": "error",
                    "message": "List source is required"
                })
            }
        
        logger.info(f"Received enrichment request: domain={domain}, list_source={list_source}")
        
        # Initialize enrichment service
        enrichment_service = EnrichmentService()
        
        # Perform enrichment
        result = enrichment_service.enrich_company(domain, list_source)
        
        logger.info(f"Enrichment result: {result['status']}")
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Error in enrich_company endpoint: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "status": "error",
                "message": "Internal server error"
            })
        }

def handle_webhook(request):
    """Handle webhook requests"""
    try:
        # Parse request data
        data = request.get_json() if hasattr(request, 'get_json') else json.loads(request.get('body', '{}'))
        if not data:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "status": "error",
                    "message": "No JSON data provided"
                })
            }
        
        domain = data.get('domain')
        list_source = data.get('list_source')
        
        if not domain:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "status": "error",
                    "message": "Domain is required"
                })
            }
        
        if not list_source:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "status": "error",
                    "message": "List source is required"
                })
            }
        
        logger.info(f"Received webhook request: domain={domain}, list_source={list_source}")
        
        # Initialize enrichment service
        enrichment_service = EnrichmentService()
        
        # Perform enrichment
        result = enrichment_service.enrich_company(domain, list_source)
        
        logger.info(f"Webhook result: {result['status']}")
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Error in webhook endpoint: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "status": "error",
                "message": "Internal server error"
            })
        }

def handle_health(request):
    """Handle health check requests"""
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "status": "healthy",
            "message": "Company enrichment API is running"
        })
    }
