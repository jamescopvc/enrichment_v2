import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
APOLLO_API_KEY = os.getenv('APOLLO_API_KEY', 'ltNTfqOJMPcWViTix5tSqg')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Apollo API Configuration
APOLLO_BASE_URL = 'https://api.apollo.io/api/v1'

# Valid list sources
VALID_LIST_SOURCES = ['james', 'zi']

# Owner assignments
OWNER_ASSIGNMENTS = {
    'james': 'james@scopvc.com',
    'zi': 'zi@scopvc.com'
}

# Calendly links
CALENDLY_LINKS = {
    'james': 'https://calendly.com/james-scopvc/30min',
    'zi': 'https://calendly.com/zi-scopvc/zoom-w-zi-scop-venture-capital'
}
