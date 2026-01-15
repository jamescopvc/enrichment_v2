import json
import logging
import re
from typing import Dict, Any, Optional, List
from google import genai
from google.genai import types
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for Gemini API with Google Search grounding for investor lookups."""
    
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = "gemini-2.5-flash"  # Using stable model with search grounding support
        
        # Configure grounding tool
        self.grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )
        
        self.config = types.GenerateContentConfig(
            tools=[self.grounding_tool]
        )
    
    def _extract_json(self, text: str) -> str:
        """
        Extract JSON from a response that may contain markdown code blocks and/or preamble text.
        """
        # First, try to find JSON in a code block
        code_block_match = re.search(r'```(?:json)?\s*\n?([\s\S]*?)\n?```', text)
        if code_block_match:
            return code_block_match.group(1).strip()
        
        # If no code block, try to find raw JSON (starts with { and ends with })
        json_match = re.search(r'(\{[\s\S]*\})', text)
        if json_match:
            return json_match.group(1).strip()
        
        # Fallback: return original text stripped
        return text.strip()
    
    def resolve_investor_domain(self, investor_name: str) -> Dict[str, Any]:
        """
        Resolve an investor/VC firm name to its official website domain.
        Uses Google Search grounding for accuracy.
        
        Args:
            investor_name: The name of the investor/VC firm (e.g., "Entrada Ventures")
            
        Returns:
            Dict with keys:
                - name: Official name of the firm
                - domain: Website domain (e.g., "entradaventures.com")
                - confidence: "high", "medium", or "low"
                - sources: List of source URLs used for grounding
                - error: Error message if lookup failed
        """
        prompt = f"""Find the official website domain for the venture capital or investment firm named "{investor_name}".

IMPORTANT REQUIREMENTS:
1. This is a VENTURE CAPITAL, PRIVATE EQUITY, or INVESTMENT firm - not a regular company
2. I need the PRIMARY website domain (e.g., "sequoiacap.com" not "sequoia.com")
3. Verify this is actually an investment firm, not a company with a similar name

Return your response as valid JSON with this exact structure:
{{
    "official_name": "The official/full name of the investment firm",
    "domain": "example.com",
    "confidence": "high/medium/low",
    "reasoning": "Brief explanation of how you verified this"
}}

CONFIDENCE LEVELS:
- "high": Found official website with clear VC/investment firm branding
- "medium": Found a likely match but some uncertainty
- "low": Could not verify this is a VC firm or domain is uncertain

If you cannot find a legitimate VC/investment firm with this name, return:
{{
    "official_name": null,
    "domain": null,
    "confidence": "low",
    "reasoning": "Could not find a VC/investment firm with this name"
}}

Return ONLY the JSON object, no other text."""

        try:
            logger.info(f"Resolving investor domain for: {investor_name}")
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=self.config
            )
            
            # Extract sources from grounding metadata
            sources = []
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                    metadata = candidate.grounding_metadata
                    if hasattr(metadata, 'grounding_chunks') and metadata.grounding_chunks:
                        for chunk in metadata.grounding_chunks:
                            if hasattr(chunk, 'web') and chunk.web:
                                sources.append({
                                    'uri': chunk.web.uri if hasattr(chunk.web, 'uri') else None,
                                    'title': chunk.web.title if hasattr(chunk.web, 'title') else None
                                })
            
            # Parse the JSON response
            response_text = response.text.strip()
            json_text = self._extract_json(response_text)
            
            try:
                result = json.loads(json_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini response as JSON: {e}")
                logger.error(f"Response text: {response_text}")
                return {
                    'name': investor_name,
                    'domain': None,
                    'confidence': 'low',
                    'sources': sources,
                    'error': f'Failed to parse response: {e}'
                }
            
            # Normalize the result
            return {
                'name': result.get('official_name') or investor_name,
                'domain': result.get('domain'),
                'confidence': result.get('confidence', 'low'),
                'reasoning': result.get('reasoning', ''),
                'sources': sources,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Gemini API error for investor lookup: {e}")
            return {
                'name': investor_name,
                'domain': None,
                'confidence': 'low',
                'sources': [],
                'error': str(e)
            }
    
    def resolve_multiple_investors(self, investor_names: List[str]) -> List[Dict[str, Any]]:
        """
        Resolve multiple investor names to domains.
        
        Args:
            investor_names: List of investor/VC firm names
            
        Returns:
            List of resolution results
        """
        results = []
        for name in investor_names:
            result = self.resolve_investor_domain(name)
            results.append(result)
        return results
    
    def filter_vc_investors(self, investor_names: List[str]) -> Dict[str, Any]:
        """
        Filter a list of investors to only include VC funds and accelerators.
        Excludes: government entities, institutional investors, individual angels.
        
        Args:
            investor_names: List of investor names from funding data
            
        Returns:
            Dict with:
                - vc_funds: List of VC fund names
                - accelerators: List of accelerator names
                - excluded: List of excluded investors with reasons
        """
        if not investor_names:
            return {'vc_funds': [], 'accelerators': [], 'excluded': []}
        
        investors_list = '\n'.join(f'- {name}' for name in investor_names)
        
        prompt = f"""Classify each investor in this list and filter to ONLY VC funds and accelerators.

INVESTOR LIST:
{investors_list}

CLASSIFICATION RULES:
1. VC FUNDS (INCLUDE): Venture capital firms, private equity firms focused on startups, seed funds, growth equity firms
2. ACCELERATORS (INCLUDE): Startup accelerators, incubators, venture studios (e.g., Y Combinator, Techstars, 500 Startups)
3. EXCLUDE - Government/Institutional: Government agencies, ministries, public institutions, grants programs (e.g., "European Commission", "BMWK", any Ministry)
4. EXCLUDE - Individual Angels: Names of individual people (e.g., "David Golan", "Ina Schlie", "John Smith")
5. EXCLUDE - Corporate/Strategic: Corporate venture arms should be INCLUDED, but pure corporate strategic investments without a dedicated fund should be excluded

If you're unsure about any investor, use web search to verify what type of entity they are.

Return your response as valid JSON:
{{
    "vc_funds": [
        {{"name": "Fund Name", "type": "vc_fund"}}
    ],
    "accelerators": [
        {{"name": "Accelerator Name", "type": "accelerator"}}
    ],
    "excluded": [
        {{"name": "Excluded Name", "type": "government|angel|institutional|unknown", "reason": "Brief reason"}}
    ]
}}

Return ONLY the JSON object, no other text."""

        # Use config with search grounding for verification
        config_with_thinking = types.GenerateContentConfig(
            tools=[self.grounding_tool],
            thinking_config=types.ThinkingConfig(
                thinking_budget=2048  # Enable reasoning for better classification
            )
        )

        try:
            logger.info(f"Filtering {len(investor_names)} investors for VC funds and accelerators")
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config_with_thinking
            )
            
            # Parse the JSON response
            response_text = response.text.strip()
            json_text = self._extract_json(response_text)
            
            try:
                result = json.loads(json_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini response as JSON: {e}")
                logger.error(f"Response text: {response_text}")
                return {
                    'vc_funds': [],
                    'accelerators': [],
                    'excluded': [],
                    'error': f'Failed to parse response: {e}',
                    'raw_response': response_text
                }
            
            # Extract just the names for convenience
            vc_fund_names = [f['name'] for f in result.get('vc_funds', [])]
            accelerator_names = [a['name'] for a in result.get('accelerators', [])]
            
            logger.info(f"Filtered to {len(vc_fund_names)} VC funds and {len(accelerator_names)} accelerators")
            
            return {
                'vc_funds': result.get('vc_funds', []),
                'accelerators': result.get('accelerators', []),
                'excluded': result.get('excluded', []),
                'vc_fund_names': vc_fund_names,
                'accelerator_names': accelerator_names,
                'all_included_names': vc_fund_names + accelerator_names,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Gemini API error for investor filtering: {e}")
            return {
                'vc_funds': [],
                'accelerators': [],
                'excluded': [],
                'error': str(e)
            }
    
    def rank_top_investors(
        self, 
        investor_names: List[str], 
        company_name: str = None,
        company_context: str = None,
        top_n: int = 3
    ) -> Dict[str, Any]:
        """
        Select the top N most institutional/lead/professional investors from a list.
        Prioritizes: lead investors, well-known VCs, institutional reputation.
        
        Args:
            investor_names: List of investor names (already filtered to VCs/accelerators)
            company_name: Optional name of the company for context
            company_context: Optional additional context (industry, stage, etc.)
            top_n: Number of top investors to return (default 3)
            
        Returns:
            Dict with:
                - top_investors: Ranked list of top N investors with reasoning
                - all_ranked: Full ranked list with scores
        """
        if not investor_names:
            return {'top_investors': [], 'all_ranked': [], 'error': None}
        
        # Pre-filter: Remove Y Combinator (they won't respond to outreach)
        filtered_names = [name for name in investor_names 
                         if 'y combinator' not in name.lower() and name.lower() != 'yc']
        
        if not filtered_names:
            return {'top_investors': [], 'all_ranked': [], 'error': None}
        
        if len(filtered_names) <= top_n:
            # If we have fewer investors than requested, return all of them
            return {
                'top_investors': [{'name': name, 'rank': i+1, 'reasoning': 'Available investor'} 
                                  for i, name in enumerate(filtered_names)],
                'all_ranked': filtered_names,
                'top_names': filtered_names,
                'error': None
            }
        
        investors_list = '\n'.join(f'- {name}' for name in filtered_names)
        
        context_str = ""
        if company_name:
            context_str += f"\nCOMPANY: {company_name}"
        if company_context:
            context_str += f"\nCONTEXT: {company_context}"
        
        prompt = f"""Rank these investors and select the TOP {top_n} most institutional, reputable, or likely lead investors.
{context_str}
INVESTORS TO RANK:
{investors_list}

RANKING CRITERIA (in order of importance):
1. LEAD INVESTOR LIKELIHOOD: Larger, more established funds that typically lead rounds
2. INSTITUTIONAL REPUTATION: Well-known, reputable VC firms with strong track records
3. ACTIVE & PROFESSIONAL: Funds known for being active, hands-on investors
4. RELEVANCE: If company context provided, prioritize investors with relevant sector expertise

Use web search to verify the reputation and status of these investors if needed.

IMPORTANT RULES:
- DEDUPLICATE: If multiple investors are the same organization or sub-programs of the same firm (e.g., "Dreamit Ventures" and "Dreamit Urbantech" are the same firm), only include ONE of them (prefer the parent/main entity)
- Larger, more established funds should rank above smaller/newer funds
- Angel groups and syndicates rank lower than institutional VCs
- Regional/local funds rank lower than national/global funds (unless highly relevant)
- Top-tier accelerators like Techstars should rank highly

Return your response as valid JSON:
{{
    "top_investors": [
        {{
            "name": "Investor Name",
            "rank": 1,
            "reasoning": "Why this investor ranks highly",
            "reputation_tier": "tier1/tier2/tier3"
        }}
    ],
    "all_ranked": [
        {{
            "name": "Investor Name",
            "rank": 1,
            "score": 95,
            "reasoning": "Brief explanation"
        }}
    ]
}}

Return ONLY the JSON object, no other text."""

        # Use config with search grounding and reasoning
        config_with_thinking = types.GenerateContentConfig(
            tools=[self.grounding_tool],
            thinking_config=types.ThinkingConfig(
                thinking_budget=4096  # More reasoning for ranking decisions
            )
        )

        try:
            logger.info(f"Ranking {len(investor_names)} investors to find top {top_n}")
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config_with_thinking
            )
            
            # Parse the JSON response
            response_text = response.text.strip()
            
            # Extract JSON from response - handle markdown code blocks and preamble text
            json_text = self._extract_json(response_text)
            
            try:
                result = json.loads(json_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini response as JSON: {e}")
                logger.error(f"Response text: {response_text}")
                return {
                    'top_investors': [],
                    'all_ranked': [],
                    'error': f'Failed to parse response: {e}',
                    'raw_response': response_text
                }
            
            top_investors = result.get('top_investors', [])[:top_n]
            top_names = [inv['name'] for inv in top_investors]
            
            logger.info(f"Top {top_n} investors: {top_names}")
            
            return {
                'top_investors': top_investors,
                'top_names': top_names,
                'all_ranked': result.get('all_ranked', []),
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Gemini API error for investor ranking: {e}")
            return {
                'top_investors': [],
                'all_ranked': [],
                'error': str(e)
            }


# Convenience function for direct usage
def resolve_investor_domain(investor_name: str) -> Dict[str, Any]:
    """
    Resolve an investor/VC firm name to its official website domain.
    
    Args:
        investor_name: The name of the investor/VC firm
        
    Returns:
        Dict with name, domain, confidence, sources, and error fields
    """
    client = GeminiClient()
    return client.resolve_investor_domain(investor_name)


def resolve_multiple_investors(investor_names: List[str]) -> List[Dict[str, Any]]:
    """
    Resolve multiple investor names to domains.
    
    Args:
        investor_names: List of investor/VC firm names
        
    Returns:
        List of resolution results
    """
    client = GeminiClient()
    return client.resolve_multiple_investors(investor_names)


def filter_vc_investors(investor_names: List[str]) -> Dict[str, Any]:
    """
    Filter a list of investors to only include VC funds and accelerators.
    Excludes: government entities, institutional investors, individual angels.
    
    Args:
        investor_names: List of investor names from funding data
        
    Returns:
        Dict with vc_funds, accelerators, excluded lists, and convenience fields
    """
    client = GeminiClient()
    return client.filter_vc_investors(investor_names)


def rank_top_investors(
    investor_names: List[str],
    company_name: str = None,
    company_context: str = None,
    top_n: int = 3
) -> Dict[str, Any]:
    """
    Select the top N most institutional/lead/professional investors from a list.
    Automatically excludes Y Combinator and deduplicates related entities.
    
    Args:
        investor_names: List of investor names (already filtered to VCs/accelerators)
        company_name: Optional name of the company for context
        company_context: Optional additional context (industry, stage, etc.)
        top_n: Number of top investors to return (default 3)
        
    Returns:
        Dict with top_investors, top_names, all_ranked, and error fields
    """
    client = GeminiClient()
    return client.rank_top_investors(investor_names, company_name, company_context, top_n)
