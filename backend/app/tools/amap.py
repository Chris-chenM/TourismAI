"""高德地图 LangChain 工具：景点搜索 / 地理编码 / 路线规划"""

import json
from langchain.tools import tool
from app.services.amap_client import amap_client


@tool
async def search_poi(keywords: str, city: str) -> str:
    """
    搜索城市中的景点、餐厅等兴趣点。
    输入 keywords（搜索关键词，如"历史文化景点"）和 city（城市名，如"杭州"），
    返回匹配的兴趣点列表（名称、地址、经度、纬度）。
    """
    print(f"[Tool] 调用高德搜索 | 城市={city} 关键词={keywords}")
    results = await amap_client.search_poi(keywords, city)
    print(f"[Tool] 高德搜索返回 {len(results)} 条结果")
    for r in results[:3]:
        print(f"  - {r['name']} ({r['longitude']}, {r['latitude']})")
    return json.dumps(results, ensure_ascii=False, indent=2)


@tool
async def geocode(address: str, city: str = "") -> str:
    """
    将地址转换为经纬度坐标。
    输入 address（地点名称，如"西湖"）和 city（可选，城市名），
    返回该地址的经度和纬度。
    """
    print(f"[Tool] 调用地理编码 | 地址={address} 城市={city}")
    result = await amap_client.geocode(address, city)
    print(f"[Tool] 地理编码结果 | {address} → ({result['longitude']}, {result['latitude']})")
    return json.dumps(result, ensure_ascii=False)


@tool
async def route_plan(origin: str, destination: str, city: str) -> str:
    """
    规划两个地点之间的交通路线。
    输入 origin（起点）、destination（终点）、city（城市名），
    返回距离（米）、耗时（分钟）、交通方式。
    """
    print(f"[Tool] 调用路线规划 | {origin} → {destination}")
    result = await amap_client.route_plan(origin, destination, city)
    print(f"[Tool] 路线规划结果 | 距离={result['distance']}m 耗时={result['duration']}min")
    return json.dumps(result, ensure_ascii=False)


# 工具集合
AMAP_TOOLS = [search_poi, geocode, route_plan]
