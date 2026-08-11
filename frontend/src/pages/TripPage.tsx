import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import MapView from "../components/MapView";
import Timeline from "../components/Timeline";
import { useTripStore } from "../store/tripStore";
import { fetchPlan } from "../api/trip";
import type { PlanResponse } from "../types/trip";

export default function TripPage() {
  const trip = useTripStore((s) => s.trip);
  const setTrip = useTripStore((s) => s.setTrip);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const planId = searchParams.get("plan_id");
  const [loadingHistory, setLoadingHistory] = useState(!!planId);

  /* 从历史记录加载 */
  useEffect(() => {
    if (!planId) return;
    fetchPlan(planId)
      .then((detail) => {
        if (detail.itinerary) {
          // PlanDetail.itinerary 里的结构可能和 PlanResponse 一致（含 days_plan/hotels/trains）
          const it = detail.itinerary as PlanResponse;
          setTrip({
            destination: detail.destination,
            days: detail.days,
            itinerary: it.days_plan || it.itinerary,
            days_plan: it.days_plan,
            hotels: it.hotels,
            trains: it.trains,
          });
        }
      })
      .catch(() => navigate("/", { replace: true }))
      .finally(() => setLoadingHistory(false));
  }, [planId, setTrip, navigate]);

  /* 无数据则回首页 */
  useEffect(() => {
    if (!planId && !trip) navigate("/", { replace: true });
  }, [trip, planId, navigate]);

  if (loadingHistory) {
    return (
      <div className="h-screen flex items-center justify-center text-gray-400">
        加载中…
      </div>
    );
  }

  if (!trip) return null;

  return (
    <div className="h-screen flex flex-col">
      {/* 顶部栏 */}
      <header className="h-14 shrink-0 bg-white border-b border-gray-100 flex items-center px-4 gap-4">
        <button
          onClick={() => navigate("/")}
          className="text-sm text-gray-500 hover:text-indigo-500 transition-colors cursor-pointer"
        >
          ← 重新规划
        </button>
        <h2 className="text-base font-semibold text-gray-700">
          {trip.destination} · {trip.days} 日游
        </h2>
        <div className="ml-auto">
          <button
            onClick={() => navigate("/history")}
            className="text-sm text-gray-400 hover:text-indigo-500 transition-colors cursor-pointer"
          >
            📋 历史记录
          </button>
        </div>
      </header>

      {/* 主体：左地图 + 右时间线 */}
      <main className="flex-1 flex overflow-hidden">
        <div className="flex-1 min-w-0">
          <MapView />
        </div>
        <aside className="w-[360px] shrink-0 bg-white border-l border-gray-100 p-4">
          <Timeline />
          {/* 酒店 / 火车票展示 */}
          {(trip.hotels && trip.hotels.length > 0) && (
            <div className="mt-6 border-t border-gray-100 pt-4">
              <h3 className="text-sm font-semibold text-gray-600 mb-2">🏨 推荐酒店</h3>
              {trip.hotels.map((h, i) => (
                <div key={i} className="text-xs text-gray-500 mb-1">
                  <span className="font-medium text-gray-700">{h.name}</span>
                  {" "}?{h.star} · ￥{h.price_per_night}/晚
                </div>
              ))}
            </div>
          )}
          {(trip.trains && trip.trains.length > 0) && (
            <div className="mt-4 border-t border-gray-100 pt-4">
              <h3 className="text-sm font-semibold text-gray-600 mb-2">🚄 火车票</h3>
              {trip.trains.map((t, i) => (
                <div key={i} className="text-xs text-gray-500 mb-1">
                  <span className="font-medium text-gray-700">{t.train_number}</span>
                  {" "}{t.from_city} → {t.to_city} · {t.departure_time}-{t.arrival_time} · ￥{t.price}
                </div>
              ))}
            </div>
          )}
        </aside>
      </main>
    </div>
  );
}
