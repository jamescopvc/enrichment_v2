import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
SPECTER_API_KEY = os.getenv('SPECTER_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
APOLLO_API_KEY = os.getenv('APOLLO_API_KEY')

# Specter API Configuration
SPECTER_BASE_URL = 'https://app.tryspecter.com/api/v1'

# Apollo API Configuration (fallback for email lookup)
APOLLO_BASE_URL = 'https://api.apollo.io/api/v1'

# Valid list sources
VALID_LIST_SOURCES = ['james', 'zi', 'jeff']

# Owner assignments
OWNER_ASSIGNMENTS = {
    'james': 'james@scopvc.com',
    'zi': 'zi@scopvc.com',
    'jeff': 'jeff@scopvc.com'
}

# Calendly links
CALENDLY_LINKS = {
    'james': 'https://calendly.com/james-scopvc/30min',
    'zi': 'https://calendly.com/zi-scopvc/zoom-w-zi-scop-venture-capital',
    'jeff': 'https://calendly.com/jeff-scopvc/zoom-w-jeff-scop-venture-capital'
}
