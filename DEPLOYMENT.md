# Vercel Deployment Guide

## 🚀 **Fixed Vercel Deployment Issues**

### **Problem**: Function Invocation Failed
The original Flask app wasn't compatible with Vercel's serverless environment.

### **Solution**: Converted to Vercel-Compatible Format

## 📁 **Updated File Structure**

```
enrichment_v2/
├── api.py                 # ✅ Vercel-compatible serverless handler
├── vercel.json           # ✅ Updated Vercel configuration
├── requirements.txt      # ✅ Python dependencies
├── apollo_client.py      # ✅ Apollo API integration
├── openai_client.py      # ✅ OpenAI integration
├── enrichment_logic.py   # ✅ Core business logic
├── config.py             # ✅ Configuration
└── test_vercel.py        # ✅ Deployment test
```

## 🔧 **Key Changes Made**

### 1. **Converted Flask to Serverless Handler**
- Removed Flask dependency for Vercel
- Created `handler(request)` function
- Proper request/response format for Vercel

### 2. **Updated vercel.json**
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/api.py"
    }
  ],
  "env": {
    "APOLLO_API_KEY": "@apollo-api-key",
    "OPENAI_API_KEY": "@openai-api-key"
  }
}
```

### 3. **Serverless Handler Format**
```python
def handler(request):
    method = request.get('method', 'GET')
    path = request.get('path', '/')
    body = request.get('body', '{}')
    
    # Route to appropriate handler
    if path == '/enrich' and method == 'POST':
        return handle_enrich(data)
    # ... other routes
```

## 🌐 **API Endpoints**

### **POST /enrich**
- **Purpose**: Main company enrichment endpoint
- **Input**: `{"domain": "company.com", "list_source": "james-sales"}`
- **Output**: Enriched company data with founders

### **POST /webhook**
- **Purpose**: Webhook for external integrations
- **Input**: Same as /enrich
- **Output**: Same as /enrich

### **GET /health**
- **Purpose**: Health check endpoint
- **Output**: `{"status": "healthy", "message": "API is running"}`

## 🔑 **Environment Variables Required**

Set these in your Vercel dashboard:

```
APOLLO_API_KEY=ltNTfqOJMPcWViTix5tSqg
OPENAI_API_KEY=your_openai_api_key_here
```

## 🚀 **Deployment Steps**

1. **Connect GitHub Repository**
   - Go to Vercel dashboard
   - Import from GitHub: `jamescopvc/enrichment_v2`

2. **Set Environment Variables**
   - Add `APOLLO_API_KEY` and `OPENAI_API_KEY`
   - Use Vercel's environment variable interface

3. **Deploy**
   - Vercel will automatically deploy from GitHub
   - Check deployment logs for any issues

## 🧪 **Testing Deployment**

### **Health Check**
```bash
curl https://your-vercel-url.vercel.app/health
```

### **Enrichment Test**
```bash
curl -X POST https://your-vercel-url.vercel.app/enrich \
  -H "Content-Type: application/json" \
  -d '{"domain": "exactrx.ai", "list_source": "james-test"}'
```

### **Webhook Test**
```bash
curl -X POST https://your-vercel-url.vercel.app/webhook \
  -H "Content-Type: application/json" \
  -d '{"domain": "amperefinancial.com", "list_source": "zi-test"}'
```

## 🐛 **Common Issues & Solutions**

### **Issue**: Function Invocation Failed
- **Cause**: Flask app not compatible with Vercel
- **Solution**: ✅ Converted to serverless handler format

### **Issue**: Missing Dependencies
- **Cause**: OpenAI/other packages not installed
- **Solution**: ✅ Added to requirements.txt

### **Issue**: Environment Variables
- **Cause**: API keys not set in Vercel
- **Solution**: ✅ Set in Vercel dashboard

## 📊 **Expected Response Format**

```json
{
  "status": "enriched",
  "company": {
    "name": "Company Name",
    "domain": "company.com",
    "industry": "AI Infrastructure",
    "location": "San Francisco, CA",
    "employee_count": 150,
    "linkedin": "https://linkedin.com/company/company"
  },
  "founders": [
    {
      "name": "John Doe",
      "title": "CEO & Founder",
      "email": "john@company.com",
      "linkedin": "https://linkedin.com/in/johndoe",
      "generated_email": "Hi John,\n\nI just came across..."
    }
  ],
  "owner": "james@scopvc.com"
}
```

## ✅ **Deployment Status**

- **GitHub Repository**: ✅ Connected
- **Vercel Configuration**: ✅ Updated
- **Serverless Handler**: ✅ Implemented
- **Environment Variables**: ⏳ Set in Vercel Dashboard
- **Dependencies**: ✅ Listed in requirements.txt
- **API Endpoints**: ✅ Ready for testing

The deployment should now work correctly! 🎉
