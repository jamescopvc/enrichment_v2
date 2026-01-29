# ScOp Company Enrichment API

Flask API that enriches company domains with founder data, investor information, and generates personalized outreach emails.

## Architecture

### Primary Flow (Specter)
1. **Company Lookup** → Specter `/companies` by domain
2. **Founder Enrichment** → Specter `/people/{id}` for each founder
3. **Email Lookup** → Specter `/people/{id}/email`
4. **Investor Processing** → Gemini AI to filter VCs, rank top 3, resolve domains

### Fallback Flow (Apollo)
Triggers when Specter doesn't find company OR has no founders:
1. **Founder Search** → Apollo `/mixed_people/api_search` by domain + titles
2. **Founder Enrichment** → Apollo `/people/match` by ID (gets LinkedIn, email)
3. **Email Fallback** → If Apollo has no email but has LinkedIn, try Specter via LinkedIn

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (or use .env file)
export SPECTER_API_KEY=your_key
export OPENAI_API_KEY=your_key
export APOLLO_API_KEY=your_key
export GEMINI_API_KEY=your_key

# Run locally
python app.py
```

## Testing

```bash
# Test enrichment pipeline
python test.py full <domain> <list_source>

# Examples
python test.py full buildern.com jeff-list-jan
python test.py full exactrx.ai james-test
```

## Endpoints

### Health Check
```
GET /health
```

### Enrich Company
```
POST /enrich
POST /webhook
```

**Request:**
```json
{
  "domain": "example.com",
  "list_source": "james-list"
}
```

**Response:**
```json
{
  "status": "enriched",
  "owner": "james@scopvc.com",
  "company": {
    "name": "Example Inc",
    "domain": "example.com",
    "industry": "AI Infrastructure",
    "location": "San Francisco, North America"
  },
  "founders": [
    {
      "name": "John Doe",
      "first_name": "John",
      "last_name": "Doe",
      "title": "CEO",
      "email": "john@example.com",
      "linkedin": "https://linkedin.com/in/johndoe",
      "generated_email": "Hi John, ..."
    }
  ],
  "investor_1_name": "Sequoia Capital",
  "investor_1_domain": "sequoiacap.com",
  "investor_2_name": "a]6z",
  "investor_2_domain": "a16z.com",
  "investor_3_name": "",
  "investor_3_domain": ""
}
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SPECTER_API_KEY` | Specter API key for company/people enrichment (primary) |
| `APOLLO_API_KEY` | Apollo API key for fallback founder/email lookup |
| `OPENAI_API_KEY` | OpenAI API key for industry classification & email generation |
| `GEMINI_API_KEY` | Google Gemini API key for investor filtering & domain resolution |

## Valid List Sources

- `james` → james@scopvc.com
- `zi` → zi@scopvc.com  
- `jeff` → jeff@scopvc.com

## Deploy to Vercel

```bash
vercel --prod
```

Set environment variables in Vercel dashboard.
