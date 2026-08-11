"""Train ticket search LangChain tool"""

import json
import logging
from langchain.tools import tool
from app.services.train_service import search_trains

logger = logging.getLogger(__name__)


@tool
async def search_train(from_city: str, to_city: str) -> str:
    """
    Search train tickets between two cities.
    Input from_city (departure city) and to_city (arrival city).
    Returns train list with number, stations, times, duration, price.
    """
    logger.info("Train search | %s -> %s", from_city, to_city)
    results = await search_trains(from_city, to_city)
    logger.info("Train search returned %d results", len(results))
    return json.dumps(results, ensure_ascii=False, indent=2)


TRAIN_TOOLS = [search_train]