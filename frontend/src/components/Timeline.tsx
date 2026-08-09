import { useTripStore } from "../store/tripStore";

export default function Timeline() {
  const trip = useTripStore((s) => s.trip);
  const selectedDay = useTripStore((s) => s.selectedDay);
  const setSelectedDay = useTripStore((s) => s.setSelectedDay);
  const setSelectedPOI = useTripStore((s) => s.setSelectedPOI);

  if (!trip?.itinerary) {
    return <p className="text-gray-400 text-center py-8">暂无行程数据</p>;
  }

  return (
    <div className="space-y-4 overflow-y-auto max-h-[calc(100vh-80px)] pr-2">
      {trip.itinerary.map((day) => (
        <div
          key={day.day}
          className={`rounded-xl border-2 transition-colors cursor-pointer ${
            selectedDay === day.day
              ? "border-indigo-400 bg-indigo-50"
              : "border-gray-100 bg-white hover:border-gray-200"
          }`}
          onClick={() => setSelectedDay(day.day)}
        >
          <div className="px-5 py-3 border-b border-gray-100">
            <span className="text-base font-semibold text-gray-800">📅 第 {day.day} 天</span>
            <span className="text-xs text-gray-400 ml-2">
              {day.activities.length} 个景点
            </span>
          </div>
          <div className="px-5 py-2">
            {day.activities.map((act, i) => {
              const durH = Math.floor(act.duration / 60);
              const durM = act.duration % 60;
              const durText = durH > 0 ? `${durH}小时${durM > 0 ? durM + "分" : ""}` : `${durM}分钟`;

              return (
                <div
                  key={i}
                  className="flex gap-3 py-2.5 border-b border-gray-50 last:border-0 cursor-pointer hover:bg-gray-50 rounded -mx-2 px-2 transition-colors"
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedPOI([act.longitude, act.latitude]);
                  }}
                >
                  {/* 时间列 */}
                  <div className="w-20 shrink-0 text-right">
                    <div className="text-sm font-medium text-gray-700">{act.start_time}</div>
                    <div className="text-xs text-gray-400">{durText}</div>
                  </div>

                  {/* 竖线 */}
                  <div className="flex flex-col items-center">
                    <div className="w-2.5 h-2.5 rounded-full bg-indigo-400 mt-1 shrink-0" />
                    {i < day.activities.length - 1 && (
                      <div className="w-0.5 flex-1 bg-gray-200 my-0.5" />
                    )}
                  </div>

                  {/* 内容 */}
                  <div className="flex-1 min-w-0 pb-1">
                    <div className="text-sm font-medium text-gray-800">{act.name}</div>
                    {act.description && (
                      <div className="text-xs text-gray-400 mt-0.5 line-clamp-1">{act.description}</div>
                    )}
                    <div className="text-xs text-gray-400 mt-0.5">
                      🚶 {act.transport} · 📍 {act.longitude.toFixed(2)}, {act.latitude.toFixed(2)}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
