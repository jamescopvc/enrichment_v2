# Company Enrichment API - Requirements

## Business Need
Take a company domain and return enriched company data with founder information for sales outreach.

## Input
```json
{
  "domain": "company.com",
  "list_source": "james-list"
}
```

## Output
```json
{
  "status": "enriched",
  "owner": "james@scopvc.com",
  "company": {
    "name": "Company Name",
    "domain": "company.com",
    "industry": "Vertical SaaS",
    "location": "San Francisco, CA",
    "employee_count": 150,
    "linkedin": "https://linkedin.com/company/example"
  },
  "founders": [
    {
      "name": "John Doe",
      "first_name": "John",
      "last_name": "Doe",
      "title": "CEO & Founder",
      "email": "john@company.com",
      "linkedin": "https://linkedin.com/in/johndoe",
      "generated_email": "Hi John,\n\n..."
    }
  ]
}
```

## Specter API Endpoints

### 1. Company Enrichment
- **Endpoint**: `POST /companies`
- **Base URL**: `https://app.tryspecter.com/api/v1`
- **Input**: `{"domain": "company.com"}`
- **Output**: Company data with `founder_info` array

### 2. Person Details
- **Endpoint**: `GET /people/{personId}`
- **Input**: Person ID from `founder_info.specter_person_id`
- **Output**: Full person profile

### 3. Person Email
- **Endpoint**: `GET /people/{personId}/email`
- **Input**: Person ID, optional `type` (professional/personal)
- **Output**: Email address

## Core Logic
1. Enrich company by domain (returns company + founder IDs)
2. For each founder: fetch person details, then fetch email
3. Generate personalized outreach email using OpenAI
4. Return enriched data

## Status Codes
- **"enriched"**: Company found + founders with emails
- **"partial"**: Company found but missing founder emails
- **"failed"**: Company not found or invalid list source

## Team Configuration

### Valid List Sources
- james, zi, jeff

### Owner Assignments
| Source | Owner |
|--------|-------|
| james | james@scopvc.com |
| zi | zi@scopvc.com |
| jeff | jeff@scopvc.com |

### Calendly Links
| Owner | Link |
|-------|------|
| James | https://calendly.com/james-scopvc/30min |
| Zi | https://calendly.com/zi-scopvc/zoom-w-zi-scop-venture-capital |
| Jeff | https://calendly.com/jeff-scopvc/zoom-w-jeff-scop-venture-capital |

## Email Personalization

### Vertical-Specific Content
- **Financial Services**: Rogo portfolio company reference
- **Construction**: Procore network reference
- **Proptech**: Appfolio/Procore LP reference
- **AI Infrastructure**: Graphiq/Amazon Alexa reference
- **HealthTech**: Healthcare portfolio reference
- **Vertical SaaS**: DoubleClick/Graphiq reference

### Location-Specific Content
- **New York**: NYC portfolio companies
- **Southern California**: Santa Barbara presence
