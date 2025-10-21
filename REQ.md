# Simple Company Enrichment API - Requirements

## Business Need
Take a company domain and return enriched company data with founder information for sales outreach.

## Input
```json
{
  "domain": "company.com",
  "list_source": "sales-team-1"
}
```

## Output
```json
{
  "status": "enriched",
  "company": {
    "name": "Company Name",
    "domain": "company.com",
    "industry": "Technology",
    "location": "San Francisco, CA",
    "employee_count": 150,
    "linkedin": "https://linkedin.com/company/company"
  },
  "founders": [
    {
      "name": "John Doe",
      "title": "CEO & Founder",
      "email": "john@company.com",
      "linkedin": "https://linkedin.com/in/johndoe"
    }
  ]
}
```

## Apollo API Endpoints Used

### 1. Company Search
- **Endpoint**: `POST /api/v1/mixed_companies/search`
- **Purpose**: Find company by domain
- **Input**: `{"q_organization_domains": "company.com"}`
- **Output**: Company data with ID

### 2. People Search  
- **Endpoint**: `POST /api/v1/mixed_people/search`
- **Purpose**: Find founders at company
- **Input**: `{"q_organization_ids": [company_id], "person_seniorities": ["founder"]}`
- **Output**: List of founder IDs

### 3. Person Enrichment
- **Endpoint**: `POST /api/v1/people/match`
- **Purpose**: Get detailed person info including email
- **Input**: `{"person_id": "founder_id"}`
- **Output**: Person details with contact info

## Core Logic
1. Search for company by domain using Apollo
2. Get founders/CEOs from that company
3. Enrich each founder with contact details
4. Return company + founders data

## Error Handling
- If company not found → return "failed" status
- If no founders found → return company data only
- If Apollo API fails → return "partial" status

## Simple Implementation
- Single Python file with 3 functions
- Use Apollo API directly
- No complex caching or fallbacks
- Basic error handling
- Return structured JSON

## Business Logic

### List Source Validation
- Only process requests from authorized list sources
- Valid sources: Any list source containing "james" or "zi"
- Invalid sources return "invalid" status (don't process)

### Owner Assignment
- List source containing "james" → assign to `james@scopvc.com`
- List source containing "zi" → assign to `zi@scopvc.com`
- Other sources → no assignment

### Status Determination
- **"enriched"**: Company found + founders with emails
- **"partial"**: Company found but no founder emails
- **"failed"**: No company found
- **"invalid"**: Unauthorized list source

## Custom AI Email Generation

### Two-Stage Process
1. **Company Analysis**: AI analyzes company data to determine vertical and location
2. **Email Generation**: AI generates personalized email using ScOp's template system

### Base Template
```
Hi [FirstName],

I just came across you guys and wanted to introduce our fund, ScOp Venture Capital - our team all comes from operating backgrounds in software, and we lead pre-seed through Series A rounds in vertical software and AI. 

[Company Name] looks really interesting, I would love to learn more about the business and what you've built.

Any times work to chat in the next few weeks? [Calendly Link]

All the best!

[Sender Name]
```

### Vertical-Specific Templates
- **Financial Services**: "We have experience with companies in financial services - our portfolio company Rogo raised a $50m Series B from Thrive building a full AI suite for banks and large financial institutions."
- **Construction**: "We have deep experience and network in construction - our partner Kevin wrote the first check to Procore, and we have the CEO and lots of early Procore employees as LPs."
- **Proptech**: "We have strong experience in proptech, and have the founders of Appfolio and Procore as LPs."
- **AI Infrastructure**: "Our partners Kevin and Ivan built and sold the knowledge graph software that powered Amazon Alexa, and we have founders of MongoDB, Twilio, DoubleClick, and more as LPs."
- **HealthTech**: "We have some experience in healthcare - our porfolio includes a patient communications company, an RCM platform, and a consumer health tracking app."
- **Vertical SaaS**: "Our partner Kevin founded DoubleClick (sold to Google), and Graphiq (sold to Amazon) - we have the founders of Procore, Appfolio, MongoDB, Twilio, and more as LPs."

### Location Personalization
- **New York**: "We have several portcos in New York as well (Rogo, Promptlayer, Pangram Labs, SuiteOp)."
- **Southern California**: "We're based in Santa Barbara and have pretty good local coverage and network throughout SoCal."

### Owner-Specific Calendly Links
- **James**: https://calendly.com/james-scopvc/30min
- **Zi**: https://calendly.com/zi-scopvc/zoom-w-zi-scop-venture-capital

## Success Criteria
- Takes domain input
- Returns company + founder data
- Handles errors gracefully
- Works for common domains (OpenAI, Stripe, etc.)
- Generates personalized email templates
- Validates list sources correctly
