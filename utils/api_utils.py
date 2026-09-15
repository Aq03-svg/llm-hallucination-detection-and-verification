import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
import requests
from config.settings import settings
from utils.logger import logger

class APIClient:
    """Utilities for making API calls with retry logic and error handling."""
    
    @staticmethod
    def get(url: str, params: Optional[Dict] = None, timeout: int = 10) -> Optional[Dict]:
        """Make a GET request with error handling."""
        try:
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {url}: {e}")
            return None
    
    @staticmethod
    async def async_get(url: str, params: Optional[Dict] = None, timeout: int = 10) -> Optional[Dict]:
        """Make an async GET request."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=timeout) as response:
                    response.raise_for_status()
                    return await response.json()
        except asyncio.TimeoutError:
            logger.error(f"API request timeout for {url}")
            return None
        except Exception as e:
            logger.error(f"API request failed for {url}: {e}")
            return None
    
    @staticmethod
    async def async_get_batch(urls: List[str], timeout: int = 10) -> List[Optional[Dict]]:
        """Make multiple async GET requests concurrently."""
        tasks = [APIClient.async_get(url, timeout=timeout) for url in urls]
        return await asyncio.gather(*tasks)

class WikipediaAPI:
    """Wikipedia API wrapper for fact verification."""
    
    @staticmethod
    def search(query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search Wikipedia for relevant articles."""
        try:
            url = "https://en.wikipedia.org/w/api.php"
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': query,
                'format': 'json',
                'srlimit': limit
            }
            result = APIClient.get(url, params, timeout=settings.WIKIPEDIA_API_TIMEOUT)
            if result and 'query' in result:
                return result['query']['search']
            return []
        except Exception as e:
            logger.error(f"Wikipedia search failed: {e}")
            return []
    
    @staticmethod
    def get_content(title: str) -> Optional[str]:
        """Get Wikipedia article content."""
        try:
            url = "https://en.wikipedia.org/w/api.php"
            params = {
                'action': 'query',
                'titles': title,
                'prop': 'extracts',
                'explaintext': True,
                'format': 'json'
            }
            result = APIClient.get(url, params, timeout=settings.WIKIPEDIA_API_TIMEOUT)
            if result and 'query' in result:
                pages = result['query']['pages']
                for page in pages.values():
                    if 'extract' in page:
                        return page['extract']
            return None
        except Exception as e:
            logger.error(f"Wikipedia content retrieval failed: {e}")
            return None

class GitHubAPI:
    """GitHub API wrapper for code verification."""
    
    HEADERS = {
        'Accept': 'application/vnd.github.v3+json'
    }
    
    @staticmethod
    def search_repositories(query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for repositories on GitHub."""
        try:
            url = "https://api.github.com/search/repositories"
            params = {
                'q': query,
                'per_page': limit
            }
            result = APIClient.get(url, params, timeout=settings.GITHUB_API_TIMEOUT)
            if result and 'items' in result:
                return result['items']
            return []
        except Exception as e:
            logger.error(f"GitHub search failed: {e}")
            return []
    
    @staticmethod
    def get_repository(owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """Get repository information."""
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}"
            return APIClient.get(url, timeout=settings.GITHUB_API_TIMEOUT)
        except Exception as e:
            logger.error(f"Failed to get repository info: {e}")
            return None
    
    @staticmethod
    def search_code(query: str, repo: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for code in GitHub."""
        try:
            url = "https://api.github.com/search/code"
            q = query
            if repo:
                q += f" repo:{repo}"
            params = {
                'q': q,
                'per_page': limit
            }
            result = APIClient.get(url, params, timeout=settings.GITHUB_API_TIMEOUT)
            if result and 'items' in result:
                return result['items']
            return []
        except Exception as e:
            logger.error(f"GitHub code search failed: {e}")
            return []
