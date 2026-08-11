"""Hotel mock data service"""

MOCK_HOTELS = {
    "Hangzhou": [
        {"name": "Atour Hotel West Lake", "address": "258 Yan'an Rd, Shangcheng, Hangzhou", "longitude": 120.168, "latitude": 30.249, "price_per_night": 350, "star": 4},
        {"name": "Four Seasons Hangzhou", "address": "5 Lingyin Rd, Xihu, Hangzhou", "longitude": 120.130, "latitude": 30.235, "price_per_night": 2500, "star": 5},
        {"name": "JI Hotel West Lake", "address": "150 Baochu Rd, Xihu, Hangzhou", "longitude": 120.152, "latitude": 30.260, "price_per_night": 280, "star": 3},
        {"name": "Home Inn Wulin Square", "address": "300 Wulin Rd, Gongshu, Hangzhou", "longitude": 120.168, "latitude": 30.272, "price_per_night": 180, "star": 2},
        {"name": "Shangri-La Hangzhou", "address": "78 Beishan Rd, Xihu, Hangzhou", "longitude": 120.142, "latitude": 30.255, "price_per_night": 1200, "star": 5},
    ],
    "Beijing": [
        {"name": "Hilton Beijing Wangfujing", "address": "8 Wangfujing St, Dongcheng, Beijing", "longitude": 116.414, "latitude": 39.916, "price_per_night": 900, "star": 5},
        {"name": "JI Hotel Tiananmen", "address": "88 Qianmen St, Dongcheng, Beijing", "longitude": 116.398, "latitude": 39.900, "price_per_night": 380, "star": 3},
        {"name": "Home Inn Nanluoguxiang", "address": "30 Nanluoguxiang, Dongcheng, Beijing", "longitude": 116.405, "latitude": 39.938, "price_per_night": 220, "star": 2},
        {"name": "China World Hotel Beijing", "address": "1 Jianguomen Outer St, Chaoyang, Beijing", "longitude": 116.462, "latitude": 39.910, "price_per_night": 1500, "star": 5},
    ],
    "Shanghai": [
        {"name": "Waldorf Astoria Shanghai", "address": "2 East Zhongshan 1st Rd, Huangpu, Shanghai", "longitude": 121.492, "latitude": 31.240, "price_per_night": 2000, "star": 5},
        {"name": "JI Hotel Nanjing Road", "address": "300 East Nanjing Rd, Huangpu, Shanghai", "longitude": 121.482, "latitude": 31.238, "price_per_night": 350, "star": 3},
        {"name": "Home Inn Jing'an Temple", "address": "1600 West Nanjing Rd, Jing'an, Shanghai", "longitude": 121.450, "latitude": 31.226, "price_per_night": 200, "star": 2},
    ],
    "Chengdu": [
        {"name": "The Temple House Chengdu", "address": "81 Bitieshi St, Jinjiang, Chengdu", "longitude": 104.084, "latitude": 30.655, "price_per_night": 1500, "star": 5},
        {"name": "JI Hotel Chunxi Road", "address": "99 Chunxi Rd, Jinjiang, Chengdu", "longitude": 104.083, "latitude": 30.657, "price_per_night": 280, "star": 3},
    ],
    "Xian": [
        {"name": "Sofitel Legend Xian", "address": "319 Dongxin St, Xincheng, Xian", "longitude": 108.952, "latitude": 34.267, "price_per_night": 800, "star": 5},
        {"name": "JI Hotel Bell Tower", "address": "200 East St, Beilin, Xian", "longitude": 108.950, "latitude": 34.263, "price_per_night": 260, "star": 3},
    ],
    "Nanjing": [
        {"name": "Jinling Hotel Nanjing", "address": "2 Hanzhong Rd, Gulou, Nanjing", "longitude": 118.782, "latitude": 32.045, "price_per_night": 700, "star": 5},
        {"name": "JI Hotel Fuzimiao", "address": "100 Jiankang Rd, Qinhuai, Nanjing", "longitude": 118.792, "latitude": 32.020, "price_per_night": 300, "star": 3},
    ],
}

MOCK_HOTELS_CN = {
    "杭州": MOCK_HOTELS["Hangzhou"],
    "北京": MOCK_HOTELS["Beijing"],
    "上海": MOCK_HOTELS["Shanghai"],
    "成都": MOCK_HOTELS["Chengdu"],
    "西安": MOCK_HOTELS["Xian"],
    "南京": MOCK_HOTELS["Nanjing"],
}


async def search_hotels(city: str, max_price: float | None = None) -> list[dict]:
    hotels = MOCK_HOTELS_CN.get(city, MOCK_HOTELS.get(city, []))
    if max_price is not None:
        hotels = [h for h in hotels if h["price_per_night"] <= max_price]
    return hotels