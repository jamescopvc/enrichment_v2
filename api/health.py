import json

def handler(request):
    """
    Health check endpoint
    """
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "status": "healthy",
            "message": "Company enrichment API is running"
        })
    }
