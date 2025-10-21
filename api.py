import json
import logging
from flask import Flask, request, jsonify
from enrichment_logic import EnrichmentService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
enrichment_service = EnrichmentService()

@app.route('/enrich', methods=['POST'])
def enrich_company():
    """
    Main API endpoint for company enrichment
    """
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
        
        domain = data.get('domain')
        list_source = data.get('list_source')
        
        if not domain:
            return jsonify({
                "status": "error",
                "message": "Domain is required"
            }), 400
        
        if not list_source:
            return jsonify({
                "status": "error",
                "message": "List source is required"
            }), 400
        
        logger.info(f"Received enrichment request: domain={domain}, list_source={list_source}")
        
        # Perform enrichment
        result = enrichment_service.enrich_company(domain, list_source)
        
        logger.info(f"Enrichment result: {result['status']}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in enrich_company endpoint: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Webhook endpoint for external integrations
    """
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
        
        domain = data.get('domain')
        list_source = data.get('list_source')
        
        if not domain:
            return jsonify({
                "status": "error",
                "message": "Domain is required"
            }), 400
        
        if not list_source:
            return jsonify({
                "status": "error",
                "message": "List source is required"
            }), 400
        
        logger.info(f"Received webhook request: domain={domain}, list_source={list_source}")
        
        # Perform enrichment
        result = enrichment_service.enrich_company(domain, list_source)
        
        logger.info(f"Webhook result: {result['status']}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in webhook endpoint: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        "status": "healthy",
        "message": "Company enrichment API is running"
    })

# Vercel handler
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
