import { useEffect, useRef } from "react";
import { useTripStore } from "../store/tripStore";
import { useMap } from "../hooks/useMap";

const DAY_COLORS = ["#4f46e5", "#059669", "#d97706", "#dc2626", "#7c3aed"];

export default function MapView() {
  const trip = useTripStore((s) => s.trip);
  const selectedDay = useTripStore((s) => s.selectedDay);
  const setSelectedDay = useTripStore((s) => s.setSelectedDay);
  const setSelectedPOI = useTripStore((s) => s.setSelectedPOI);

  const { containerRef, map: mapRef, loaded } = useMap();
  const map = mapRef.current;
  const markersRef = useRef<any[]>([]);
  const polylinesRef = useRef<any[]>([]);

  function clearOverlays() {
    markersRef.current.forEach((m: any) => m.setMap(null));
    polylinesRef.current.forEach((p: any) => p.setMap(null));
    markersRef.current = [];
    polylinesRef.current = [];
  }

  /* 渲染路线和标记 */
  useEffect(() => {
    if (!loaded || !map || !trip?.itinerary) return;

    clearOverlays();
    const allPoints: [number, number][] = [];
    const AMap = window.AMap;

    trip.itinerary.forEach((day, di) => {
      const color = DAY_COLORS[di % DAY_COLORS.length];
      const path: [number, number][] = day.activities.map((a) => [a.longitude, a.latitude]);
      allPoints.push(...path);

      const isActive = day.day === selectedDay;

      const polyline = new AMap.Polyline({
        path,
        strokeColor: isActive ? color : "#d1d5db",
        strokeWeight: isActive ? 5 : 2,
        strokeOpacity: isActive ? 0.8 : 0.4,
        zIndex: isActive ? 10 : 1,
      });
      polyline.setMap(map);
      polylinesRef.current.push(polyline);

      day.activities.forEach((act) => {
        const marker = new AMap.Marker({
          position: [act.longitude, act.latitude],
          label: {
            content: `<span style="background:${color};color:#fff;padding:2px 6px;border-radius:10px;font-size:11px">${act.name}</span>`,
            direction: "top",
          },
          zIndex: isActive ? 100 : 50,
          visible: isActive,
        });
        marker.on("click", () => {
          setSelectedDay(day.day);
          setSelectedPOI([act.longitude, act.latitude]);
        });
        marker.setMap(map);
        markersRef.current.push(marker);
      });
    });

    if (allPoints.length > 0) {
      map.setFitView(undefined, false, [60, 60, 60, 300]);
    }
  }, [loaded, map, trip, selectedDay]);

  /* 选中景点飞过去 */
  useEffect(() => {
    const pos = useTripStore.getState().selectedPOI;
    if (pos && map) {
      map.setZoomAndCenter(15, pos);
    }
  }, [useTripStore((s) => s.selectedPOI)]);

  return (
    <div className="relative w-full h-full rounded-xl overflow-hidden">
      <div ref={containerRef} className="w-full h-full" />

      {!loaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-50 rounded-xl">
          <span className="text-gray-400">地图加载中...</span>
        </div>
      )}

      {loaded && trip?.itinerary && trip.itinerary.length > 1 && (
        <div className="absolute top-3 left-3 flex gap-1.5 z-10">
          {trip.itinerary.map((day) => (
            <button
              key={day.day}
              onClick={() => setSelectedDay(day.day)}
              className={`px-3 py-1.5 text-xs font-medium rounded-lg shadow transition-colors ${
                selectedDay === day.day
                  ? "bg-indigo-500 text-white"
                  : "bg-white text-gray-600 hover:bg-gray-50"
              }`}
            >
              第{day.day}天
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
