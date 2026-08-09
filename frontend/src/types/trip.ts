/* 行程数据类型 —— 所有组件的唯一数据来源 */

export interface PlanResponse {
  destination: string;
  days: number;
  itinerary: DayPlan[];
}

export interface DayPlan {
  day: number;
  activities: Activity[];
}

export interface Activity {
  name: string;
  location: string;
  longitude: number;
  latitude: number;
  start_time: string;
  duration: number;    // 分钟
  transport: string;
  description: string;
}
