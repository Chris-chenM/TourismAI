/* 行程数据类型 —— 所有组件的唯一数据来源 */

export interface PlanResponse {
  destination: string;
  days: number;
  itinerary: DayPlan[];
  days_plan?: DayPlan[];
  hotels?: HotelInfo[];
  trains?: TrainInfo[];
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

export interface HotelInfo {
  name: string;
  address: string;
  longitude: number;
  latitude: number;
  price_per_night: number;
  star: number;
}

export interface TrainInfo {
  train_number: string;
  from_city: string;
  to_city: string;
  from_station: string;
  to_station: string;
  departure_time: string;
  arrival_time: string;
  duration_min: number;
  price: number;
}

/* 历史列表摘要 */
export interface PlanSummary {
  id: string;
  destination: string;
  days: number;
  budget: number;
  interests: string;
  status: string;
  created_at: string;
}

/* 计划详情（含 events） */
export interface AgentEvent {
  id: string;
  phase: string;
  message: string;
  created_at: string;
}

export interface PlanDetail {
  id: string;
  visitor_id: string;
  destination: string;
  days: number;
  budget: number;
  interests: string;
  status: string;
  itinerary: PlanResponse | null;
  events: AgentEvent[];
  created_at: string;
}
