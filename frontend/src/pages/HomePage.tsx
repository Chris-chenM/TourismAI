import { useNavigate } from "react-router-dom";
import SearchForm from "../components/SearchForm";
import LoadingSteps from "../components/LoadingSteps";
import { usePlanTrip } from "../api/trip";
import { useTripStore } from "../store/tripStore";
import type { PlanRequest } from "../api/trip";

export default function HomePage() {
  const navigate = useNavigate();
  const mutation = usePlanTrip();
  const setTrip = useTripStore((s) => s.setTrip);

  function handleSubmit(data: PlanRequest) {
    mutation.mutate(data, {
      onSuccess: (result) => {
        setTrip(result);
        navigate("/trip");
      },
    });
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
          <SearchForm onSubmit={handleSubmit} loading={mutation.isPending} />
        </div>

        {/* Loading */}
        <LoadingSteps show={mutation.isPending} />

        {/* 错误 */}
        {mutation.isError && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-xl text-red-500 text-sm text-center">
            ❌ {mutation.error?.message || "请求失败，请检查后端是否启动"}
          </div>
        )}
      </div>
    </div>
  );
}
