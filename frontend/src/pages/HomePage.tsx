import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import SearchForm from "../components/SearchForm";
import LoadingSteps from "../components/LoadingSteps";
import { streamPlanTrip } from "../api/trip";
import { useTripStore } from "../store/tripStore";
import type { PlanRequest } from "../api/trip";

export default function HomePage() {
  const navigate = useNavigate();
  const setTrip = useTripStore((s) => s.setTrip);

  const [loadingPhase, setLoadingPhase] = useState<string | null>(null);
  const [loadingMessage, setLoadingMessage] = useState("");
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // 保存 AbortController 以便中断
  const abortRef = useRef<AbortController | null>(null);

  function handleSubmit(data: PlanRequest) {
    // 重置状态
    setLoading(true);
    setError(null);
    setLoadingPhase(null);
    setLoadingMessage("");
    setLoadingProgress(0);

    const controller = streamPlanTrip(data, {
      onPhase: (phase, message, progress) => {
        setLoadingPhase(phase);
        setLoadingMessage(message);
        setLoadingProgress(progress);
      },
      onResult: (result) => {
        setTrip(result);
        setLoading(false);
        navigate("/trip");
      },
      onError: (errMsg) => {
        setError(errMsg);
        setLoading(false);
        setLoadingPhase(null);
      },
    });

    abortRef.current = controller;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-white flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* 头部 */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">🗺 TourismAI</h1>
          <p className="text-gray-400 text-sm">智能旅游规划助手</p>
        </div>

        {/* 表单卡片 */}
        <div className="bg-white rounded-2xl shadow-lg shadow-indigo-100/50 p-6">
          <SearchForm onSubmit={handleSubmit} loading={loading} />
        </div>

        {/* Loading / 错误 */}
        <LoadingSteps
          phase={loadingPhase}
          message={loadingMessage}
          progress={loadingProgress}
          error={error}
        />
      </div>
    </div>
  );
}
