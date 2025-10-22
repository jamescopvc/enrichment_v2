from flask import Flask, request, jsonify
import logging
from enrichment_logic import EnrichmentService

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "message": "Company enrichment API is running"})

@app.route('/enrich', methods=['POST'])
def enrich():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No JSON data provided"}), 400
        
        domain = data.get('domain')
        list_source = data.get('list_source')
        
        if not domain:
            return jsonify({"status": "error", "message": "Domain is required"}), 400
        
        if not list_source:
            return jsonify({"status": "error", "message": "List source is required"}), 400
        
        logger.info(f"Enrichment request: domain={domain}, list_source={list_source}")
        
        enrichment_service = EnrichmentService()
        result = enrichment_service.enrich_company(domain, list_source)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in enrich endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No JSON data provided"}), 400
        
        domain = data.get('domain')
        list_source = data.get('list_source')
        
        if not domain:
            return jsonify({"status": "error", "message": "Domain is required"}), 400
        
        if not list_source:
            return jsonify({"status": "error", "message": "List source is required"}), 400
        
        logger.info(f"Webhook request: domain={domain}, list_source={list_source}")
        
        enrichment_service = EnrichmentService()
        result = enrichment_service.enrich_company(domain, list_source)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in webhook endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
