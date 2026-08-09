/* 高德地图初始化 Hook */

import { useEffect, useRef, useState } from "react";

declare global {
  interface Window {
    AMap: any;
    _AMapSecurityConfig: { securityJsCode: string };
  }
}

export function useMap() {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<any>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    if (!containerRef.current) return;
    let cancelled = false;

    async function init() {
      try {
        const loader = await import("@amap/amap-jsapi-loader");
        // loader.default 是 load 函数，调用后 AMap 挂到 window.AMap
        await loader.default.load({
          key: import.meta.env.VITE_AMAP_WEB_KEY || "",
          version: "2.0",
          plugins: ["AMap.Driving", "AMap.Walking", "AMap.Marker"],
        });

        if (cancelled || !containerRef.current) return;

        const AMap = window.AMap;
        mapRef.current = new AMap.Map(containerRef.current, {
          zoom: 12,
          center: [120.15, 30.28],
          resizeEnable: true,
        });
        setLoaded(true);
      } catch (err) {
        console.error("高德地图加载失败:", err);
      }
    }

    init();
    return () => {
      cancelled = true;
      if (mapRef.current) {
        mapRef.current.destroy();
        mapRef.current = null;
      }
    };
  }, []);

  return { containerRef, map: mapRef, loaded };
}
