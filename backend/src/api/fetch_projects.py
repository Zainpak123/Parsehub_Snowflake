"""
Fetch and cache ParseHub projects
"""
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

# In-memory cache with TTL
_project_cache: Dict[str, Dict] = {}

CACHE_TTL = 300  # 5 minutes


def clean_cache():
    """Remove expired cache entries"""
    now = datetime.now()
    expired_keys = [
        key for key, data in _project_cache.items()
        if now > data['expiry']
    ]
    for key in expired_keys:
        del _project_cache[key]


def fetch_all_projects(api_key: str) -> List[Dict]:
    """
    Fetch all projects from ParseHub API with pagination
    
    Args:
        api_key: ParseHub API key
        
    Returns:
        List of all projects
    """
    try:
        base_url = os.getenv('PARSEHUB_API_SITE', 'https://www.parsehub.com/api/v2')
        all_projects = []
        offset = 0
        limit = 20  # ParseHub returns 20 projects per page

        while True:
            response = requests.get(
                f"{base_url}/projects",
                params={'api_key': api_key, 'offset': offset},
                timeout=10
            )

            if response.status_code != 200:
                logger.error(f"API error: {response.status_code}")
                break

            data = response.json()
            projects = data.get('projects', [])

            if not projects:
                break

            all_projects.extend(projects)

            # Check if there are more projects
            total_projects = data.get('total_projects', 0)
            if len(all_projects) >= total_projects:
                break

            offset += limit
            import time
            time.sleep(0.5)  # Rate limiting

        logger.info(f"Fetched {len(all_projects)} projects from ParseHub API")
        return all_projects

    except Exception as e:
        logger.error(f"Error fetching projects: {e}")
        return []


def get_all_projects_with_cache(api_key: str) -> List[Dict]:
    """
    Get all projects with caching (5-minute TTL)
    
    Args:
        api_key: ParseHub API key
        
    Returns:
        List of all projects (from cache if fresh, otherwise fetched)
    """
    clean_cache()
    
    if api_key in _project_cache:
        cache_entry = _project_cache[api_key]
        if datetime.now() < cache_entry['expiry']:
            logger.info("Returning projects from cache")
            return cache_entry['projects']
        else:
            del _project_cache[api_key]
    
    # Fetch fresh projects
    projects = fetch_all_projects(api_key)
    
    # Store in cache
    _project_cache[api_key] = {
        'projects': projects,
        'expiry': datetime.now() + timedelta(seconds=CACHE_TTL)
    }
    
    logger.info(f"Cached {len(projects)} projects for next 5 minutes")
    return projects
