import json
import logging
from enrichment_logic import EnrichmentService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def handler(request):
    """
    Webhook endpoint for external integrations
    """
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
