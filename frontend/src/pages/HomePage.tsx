import { useState, useRef } from "react";
import { useNavigate, Link } from "react-router-dom";
import SearchForm from "../components/SearchForm";
import LoadingSteps from "../components/LoadingSteps";
import { streamPlanTrip } from "../api/trip";
import { useTripStore } from "../store/tripStore";
import { getVisitorId } from "../utils/visitorId";
import type { PlanRequest } from "../api/trip";

export default function HomePage() {
  const navigate = useNavigate();
  const setTrip = useTripStore((s) => s.setTrip);

  const [loadingPhase, setLoadingPhase] = useState<string | null>(null);
  const [loadingMessage, setLoadingMessage] = useState("");
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const abortRef = useRef<AbortController | null>(null);

  function handleSubmit(data: Omit<PlanRequest, "visitor_id">) {
    setLoading(true);
    setError(null);
    setLoadingPhase(null);
    setLoadingMessage("");
    setLoadingProgress(0);

    const req: PlanRequest = { ...data, visitor_id: getVisitorId() };

    const controller = streamPlanTrip(req, {
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
          <h1 className="text-3xl font-bold text-gray-800 mb-2">?? TourismAI</h1>
          <p className="text-gray-400 text-sm">智能旅游规划助手</p>
        </div>

        {/* 表单卡片 */}
        <div className="bg-white rounded-2xl shadow-lg shadow-indigo-100/50 p-6">
          <SearchForm onSubmit={handleSubmit} loading={loading} />
        </div>

        {/* 历史记录入口 */}
        <div className="text-center mt-6">
          <Link
            to="/history"
            className="text-sm text-gray-400 hover:text-indigo-500 transition-colors"
          >
            ?? 查看历史记录
          </Link>
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
