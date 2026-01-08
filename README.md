# ScOp Company Enrichment API

Flask API that enriches company domains with founder data and generates personalized outreach emails.

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SPECTER_API_KEY=your_key
export OPENAI_API_KEY=your_key

# Run locally
python app.py
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
  "company": { ... },
  "founders": [ ... ]
}
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SPECTER_API_KEY` | Specter API key for company/people enrichment |
| `OPENAI_API_KEY` | OpenAI API key for email generation |

## Deploy to Vercel

```bash
vercel --prod
```

Set environment variables in Vercel dashboard.

