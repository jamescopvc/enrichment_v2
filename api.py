from http.server import BaseHTTPRequestHandler
import json
import logging
from enrichment_logic import EnrichmentService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "healthy", "message": "Company enrichment API is running"}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "error", "message": "Endpoint not found"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        if self.path == '/enrich':
            self.handle_enrich()
        elif self.path == '/webhook':
            self.handle_webhook()
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "error", "message": "Endpoint not found"}
            self.wfile.write(json.dumps(response).encode())
    
    def handle_enrich(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            domain = data.get('domain')
            list_source = data.get('list_source')
            
            if not domain:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"status": "error", "message": "Domain is required"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            if not list_source:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"status": "error", "message": "List source is required"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Real Apollo API integration
            logger.info(f"Enrichment request: domain={domain}, list_source={list_source}")
            
            try:
                enrichment_service = EnrichmentService()
                result = enrichment_service.enrich_company(domain, list_source)
            except Exception as e:
                logger.error(f"Enrichment error: {e}")
                result = {
                    "status": "error",
                    "message": f"Enrichment service failed: {str(e)}"
                }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "error", "message": "Internal server error"}
            self.wfile.write(json.dumps(response).encode())
    
    def handle_webhook(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            domain = data.get('domain')
            list_source = data.get('list_source')
            
            if not domain:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"status": "error", "message": "Domain is required"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            if not list_source:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"status": "error", "message": "List source is required"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Real Apollo API integration
            logger.info(f"Webhook request: domain={domain}, list_source={list_source}")
            
            try:
                enrichment_service = EnrichmentService()
                result = enrichment_service.enrich_company(domain, list_source)
            except Exception as e:
                logger.error(f"Webhook enrichment error: {e}")
                result = {
                    "status": "error",
                    "message": f"Enrichment service failed: {str(e)}"
                }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "error", "message": "Internal server error"}
            self.wfile.write(json.dumps(response).encode())