"""高德地图 HTTP 客户端，支持 Mock 模式"""

import httpx
from app.core.config import settings

AMAP_BASE = "https://restapi.amap.com/v3"

# Mock 数据：杭州景点（含独立经纬度）
MOCK_POI = {
    "杭州": [
        {"name": "西湖", "address": "杭州市西湖区龙井路1号", "longitude": 120.148, "latitude": 30.238},
        {"name": "灵隐寺", "address": "杭州市西湖区灵隐路法云弄1号", "longitude": 120.105, "latitude": 30.242},
        {"name": "雷峰塔", "address": "杭州市西湖区南山路15号", "longitude": 120.155, "latitude": 30.231},
        {"name": "河坊街", "address": "杭州市上城区河坊街", "longitude": 120.172, "latitude": 30.240},
        {"name": "宋城", "address": "杭州市西湖区之江路148号", "longitude": 120.095, "latitude": 30.175},
        {"name": "浙江省博物馆", "address": "杭州市西湖区孤山路25号", "longitude": 120.145, "latitude": 30.248},
        {"name": "良渚古城遗址", "address": "杭州市余杭区良渚街道", "longitude": 120.025, "latitude": 30.395},
        {"name": "京杭大运河", "address": "杭州市拱墅区运河文化广场", "longitude": 120.168, "latitude": 30.320},
        {"name": "胡雪岩故居", "address": "杭州市上城区元宝街18号", "longitude": 120.178, "latitude": 30.243},
        {"name": "南宋御街", "address": "杭州市上城区中山中路", "longitude": 120.170, "latitude": 30.245},
    ]
}

MOCK_GEOCODE = {
    "西湖": (120.148, 30.238),
    "灵隐寺": (120.105, 30.242),
    "雷峰塔": (120.155, 30.231),
    "河坊街": (120.172, 30.240),
    "宋城": (120.095, 30.175),
}

MOCK_ROUTE = {
    "distance": 8500,
    "duration": 35,
    "mode": "公交/地铁",
}


class AmapClient:
    """高德地图 API 客户端"""

    def __init__(self):
        self.key = settings.amap_key

    async def search_poi(self, keywords: str, city: str, types: str = "") -> list[dict]:
        """搜索兴趣点（景点、餐饮等），返回含独立经纬度的结果"""
        if settings.mock_amap:
            city_data = MOCK_POI.get(city, MOCK_POI.get("杭州", []))
            results = [p for p in city_data if keywords in p["name"] or not keywords]
            return results[:5] if results else city_data[:5]

        params = {"key": self.key, "keywords": keywords, "city": city, "offset": "10"}
        if types:
            params["types"] = types
        raw = await self._get("/place/text", params, "pois")
        return [
            {
                "name": p.get("name", ""),
                "address": p.get("address", ""),
                "longitude": float(p.get("location", "0,0").split(",")[0]),
                "latitude": float(p.get("location", "0,0").split(",")[1]),
            }
            for p in raw
        ]

    async def geocode(self, address: str, city: str = "") -> dict:
        """地址转经纬度"""
        if settings.mock_amap:
            lng, lat = MOCK_GEOCODE.get(address, (120.148, 30.238))
            return {"address": address, "longitude": lng, "latitude": lat}

        params = {"key": self.key, "address": address}
        if city:
            params["city"] = city
        results = await self._get("/geocode/geo", params, "geocodes")
        if results:
            loc = results[0].get("location", "0,0")
            parts = loc.split(",")
            return {"address": address, "longitude": float(parts[0]), "latitude": float(parts[1])}
        return {"address": address, "longitude": 0.0, "latitude": 0.0}

    async def route_plan(
        self, origin: str, destination: str, city: str, mode: str = "transit"
    ) -> dict:
        """路线规划"""
        if settings.mock_amap:
            return {**MOCK_ROUTE, "origin": origin, "destination": destination}

        origin_loc = await self.geocode(origin, city)
        dest_loc = await self.geocode(destination, city)

        if mode == "transit":
            url = "/direction/transit/integrated"
        elif mode == "driving":
            url = "/direction/driving"
        else:
            url = "/direction/walking"

        params = {
            "key": self.key,
            "origin": f"{origin_loc['longitude']},{origin_loc['latitude']}",
            "destination": f"{dest_loc['longitude']},{dest_loc['latitude']}",
            "city": city,
        }
        routes = await self._get(url, params, "route")
        if routes and routes[0]:
            route = routes[0]
            return {
                "origin": origin,
                "destination": destination,
                "distance": int(route.get("distance", 0)),
                "duration": int(route.get("duration", 0)) // 60,
            }
        return {"origin": origin, "destination": destination, "distance": 0, "duration": 0}

    async def _get(self, path: str, params: dict, result_key: str) -> list[dict]:
        """通用 GET 请求"""
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{AMAP_BASE}{path}", params=params)
            resp.raise_for_status()
            data = resp.json()
            if data.get("status") == "1":
                return data.get(result_key, [])
            return []


# 全局单例
amap_client = AmapClient()
