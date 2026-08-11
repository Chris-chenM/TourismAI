"""Hotel search LangChain tool"""

import json
import logging
from langchain.tools import tool
from app.services.hotel_service import search_hotels

logger = logging.getLogger(__name__)


@tool
async def search_hotel(city: str, max_price: float = 99999) -> str:
    """
    Search hotels in a city. Input city name and max_price (max budget per night in CNY).
    Returns matching hotels with name, address, coordinates, price, star rating.
    """
    logger.info("Hotel search | city=%s max_price=%s", city, max_price)
    results = await search_hotels(city, max_price)
    logger.info("Hotel search returned %d results", len(results))
    return json.dumps(results, ensure_ascii=False, indent=2)


HOTEL_TOOLS = [search_hotel]