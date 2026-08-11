"""Train ticket mock data service"""

MOCK_TRAINS = {
    ("Shanghai", "Hangzhou"): [
        {"train_number": "G7312", "from_city": "Shanghai", "to_city": "Hangzhou", "from_station": "Shanghai Hongqiao", "to_station": "Hangzhou East", "departure_time": "08:30", "arrival_time": "09:30", "duration_min": 60, "price": 73},
        {"train_number": "G7324", "from_city": "Shanghai", "to_city": "Hangzhou", "from_station": "Shanghai Hongqiao", "to_station": "Hangzhou East", "departure_time": "10:15", "arrival_time": "11:15", "duration_min": 60, "price": 73},
        {"train_number": "G7348", "from_city": "Shanghai", "to_city": "Hangzhou", "from_station": "Shanghai Hongqiao", "to_station": "Hangzhou East", "departure_time": "14:00", "arrival_time": "15:00", "duration_min": 60, "price": 73},
    ],
    ("Hangzhou", "Shanghai"): [
        {"train_number": "G7311", "from_city": "Hangzhou", "to_city": "Shanghai", "from_station": "Hangzhou East", "to_station": "Shanghai Hongqiao", "departure_time": "07:30", "arrival_time": "08:30", "duration_min": 60, "price": 73},
        {"train_number": "G7335", "from_city": "Hangzhou", "to_city": "Shanghai", "from_station": "Hangzhou East", "to_station": "Shanghai Hongqiao", "departure_time": "16:00", "arrival_time": "17:00", "duration_min": 60, "price": 73},
    ],
    ("Beijing", "Shanghai"): [
        {"train_number": "G1", "from_city": "Beijing", "to_city": "Shanghai", "from_station": "Beijing South", "to_station": "Shanghai Hongqiao", "departure_time": "07:00", "arrival_time": "11:30", "duration_min": 270, "price": 553},
        {"train_number": "G5", "from_city": "Beijing", "to_city": "Shanghai", "from_station": "Beijing South", "to_station": "Shanghai Hongqiao", "departure_time": "14:00", "arrival_time": "18:30", "duration_min": 270, "price": 553},
    ],
    ("Beijing", "Xian"): [
        {"train_number": "G651", "from_city": "Beijing", "to_city": "Xian", "from_station": "Beijing West", "to_station": "Xian North", "departure_time": "07:30", "arrival_time": "12:00", "duration_min": 270, "price": 515},
        {"train_number": "G659", "from_city": "Beijing", "to_city": "Xian", "from_station": "Beijing West", "to_station": "Xian North", "departure_time": "14:00", "arrival_time": "18:30", "duration_min": 270, "price": 515},
    ],
    ("Chengdu", "Xian"): [
        {"train_number": "D1912", "from_city": "Chengdu", "to_city": "Xian", "from_station": "Chengdu East", "to_station": "Xian North", "departure_time": "08:00", "arrival_time": "11:30", "duration_min": 210, "price": 263},
    ],
    ("Nanjing", "Hangzhou"): [
        {"train_number": "G7641", "from_city": "Nanjing", "to_city": "Hangzhou", "from_station": "Nanjing South", "to_station": "Hangzhou East", "departure_time": "09:00", "arrival_time": "10:30", "duration_min": 90, "price": 117},
    ],
}

MOCK_TRAINS_CN = {
    ("上海", "杭州"): MOCK_TRAINS[("Shanghai", "Hangzhou")],
    ("杭州", "上海"): MOCK_TRAINS[("Hangzhou", "Shanghai")],
    ("北京", "上海"): MOCK_TRAINS[("Beijing", "Shanghai")],
    ("北京", "西安"): MOCK_TRAINS[("Beijing", "Xian")],
    ("成都", "西安"): MOCK_TRAINS[("Chengdu", "Xian")],
    ("南京", "杭州"): MOCK_TRAINS[("Nanjing", "Hangzhou")],
}


async def search_trains(from_city: str, to_city: str) -> list[dict]:
    key = (from_city, to_city)
    return MOCK_TRAINS_CN.get(key, MOCK_TRAINS.get(key, []))