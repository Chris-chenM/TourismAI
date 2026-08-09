import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import MapView from "../components/MapView";
import Timeline from "../components/Timeline";
import { useTripStore } from "../store/tripStore";

export default function TripPage() {
  const trip = useTripStore((s) => s.trip);
  const navigate = useNavigate();

  /* 无数据则回首页 */
  useEffect(() => {
    if (!trip) navigate("/", { replace: true });
  }, [trip, navigate]);

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
      </header>

      {/* 主体：左地图 + 右时间线 */}
      <main className="flex-1 flex overflow-hidden">
        <div className="flex-1 min-w-0">
          <MapView />
        </div>
        <aside className="w-[360px] shrink-0 bg-white border-l border-gray-100 p-4">
          <Timeline />
        </aside>
      </main>
    </div>
  );
}
