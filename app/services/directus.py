import os
import logging
import requests
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

def get_directus_url() -> str:
    url = os.getenv("DIRECTUS_URL")
    if not url:
        logger.error("Directus URL not found in environment variables")
        raise ValueError("DIRECTUS_URL environment variable is not set")
    return url

def get_directus_token() -> str:
    token = os.getenv("DIRECTUS_TOKEN")
    if not token:
        logger.error("Directus token not found in environment variables")
        raise ValueError("DIRECTUS_TOKEN environment variable is not set")
    return token


def make_directus_request(endpoint: str, method: str = "GET", params: Optional[Dict[str, Any]] = None) -> Dict[
    str, Any]:
    base_url = get_directus_url()
    token = get_directus_token()

    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    processed_params = {}
    if params:
        for key, value in params.items():
            if key == "filter" and isinstance(value, dict):
                # JSON encode the filter object
                import json
                processed_params[key] = json.dumps(value)
            else:
                processed_params[key] = value

    try:
        logger.info(f"Making {method} request to Directus API: {url}")

        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=processed_params)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=params)
        else:
            logger.error(f"Unsupported HTTP method: {method}")
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        logger.error(f"Error making request to Directus API: {e}")
        raise


def get_bus_schedule() -> Optional[Dict[str, Any]]:

    try:
        response = make_directus_request(
            endpoint="/items/bus_schedule",
            params={
                "sort": "-date_created",
                "limit": 1,
                "fields": ["id", "date_created", "image", "description"]
            }
        )
        
        if not response or "data" not in response or not response["data"]:
            logger.warning("No bus schedule found in Directus")
            return None
        

        schedule = response["data"][0]
        

        directus_url = get_directus_url()
        image_id = schedule.get("image")
        
        if not image_id:
            logger.warning("Bus schedule has no image")
            return {
                "id": schedule.get("id"),
                "date": schedule.get("date"),
                "description": schedule.get("description")
            }
        

        image_url = f"{directus_url.rstrip('/')}/assets/{image_id}"
        
        return {
            "id": schedule.get("id"),
            "date": schedule.get("date"),
            "description": schedule.get("description"),
            "image_url": image_url
        }
    
    except Exception as e:
        logger.error(f"Error fetching bus schedule from Directus: {e}")
        return None