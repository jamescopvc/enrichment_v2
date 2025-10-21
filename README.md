# Company Enrichment API

A Python API that enriches company data with founder information for sales outreach, using Apollo API and OpenAI for intelligent email generation.

## Features

- **Company Search**: Find companies by domain using Apollo API
- **Founder Detection**: Identify founders, CEOs, and CTOs at companies
- **AI-Powered Email Generation**: Generate personalized outreach emails using OpenAI
- **Industry Classification**: Automatically classify company verticals
- **List Source Validation**: Secure access control based on list sources
- **Comprehensive Logging**: Detailed logs for debugging and monitoring

## Project Structure

```
enrichment_v2/
├── api.py                 # Main Flask API endpoints
├── apollo_client.py       # Apollo API integration
├── openai_client.py       # OpenAI integration for AI features
├── enrichment_logic.py   # Core business logic
├── config.py             # Configuration and constants
├── test_enrichment.py    # Test suite for debugging
├── requirements.txt      # Python dependencies
├── vercel.json          # Vercel deployment config
└── README.md            # This file
```

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Create a `.env` file with:
   ```
   APOLLO_API_KEY=your_apollo_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Testing Without Starting the App

Run the comprehensive test suite to debug individual components:

```bash
python test_enrichment.py
```

This will test:
- Apollo API company search
- Apollo API founders search  
- OpenAI industry classification
- OpenAI email generation
- List source validation
- Full enrichment process

## API Endpoints

### POST /enrich
Main enrichment endpoint.

**Input**:
```json
{
  "domain": "company.com",
  "list_source": "james-sales-team"
}
```

**Output**:
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

### POST /webhook
Webhook endpoint for external integrations.

### GET /health
Health check endpoint.

## Status Codes

- **"enriched"**: Company found + founders with emails
- **"partial"**: Company found but no founder emails  
- **"failed"**: No company found
- **"invalid"**: Unauthorized list source

## List Source Validation

Only authorized list sources are processed:
- Sources containing "james" → assigned to `james@scopvc.com`
- Sources containing "zi" → assigned to `zi@scopvc.com`
- Other sources → rejected with "invalid" status

## AI Email Generation

The system generates personalized emails using:
- Company industry classification
- Location-specific content
- Industry-specific portfolio examples
- Owner-specific Calendly links

## Deployment

### Vercel Deployment

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Deploy**:
   ```bash
   vercel --prod
   ```

3. **Set Environment Variables**:
   ```bash
   vercel env add APOLLO_API_KEY
   vercel env add OPENAI_API_KEY
   ```

## Apollo API Integration

Uses the provided Apollo endpoint for founder search:
```bash
curl --request POST \
     --url 'https://api.apollo.io/api/v1/mixed_people/search?person_titles[]=Co-Founder&person_titles[]=CEO&person_titles[]=CTO&person_locations[]=&person_seniorities[]=&q_organization_domains_list[]=usecervo.com' \
     --header 'x-api-key: ltNTfqOJMPcWViTix5tSqg'
```

## Logging

Comprehensive logging is enabled for:
- API requests and responses
- Company and founder searches
- AI classification and email generation
- Error handling and debugging

## Error Handling

- Graceful handling of Apollo API failures
- OpenAI API error recovery
- Invalid input validation
- Comprehensive error logging
