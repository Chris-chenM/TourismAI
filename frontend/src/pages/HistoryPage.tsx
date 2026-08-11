import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchPlans, deletePlan } from "../api/trip";
import { getVisitorId } from "../utils/visitorId";
import type { PlanSummary } from "../types/trip";

export default function HistoryPage() {
  const navigate = useNavigate();
  const [plans, setPlans] = useState<PlanSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const visitorId = getVisitorId();
    fetchPlans(visitorId)
      .then(setPlans)
      .catch(() => setPlans([]))
      .finally(() => setLoading(false));
  }, []);

  async function handleDelete(id: string) {
    if (!confirm("确定删除这条记录？")) return;
    await deletePlan(id);
    setPlans((prev) => prev.filter((p) => p.id !== id));
  }

  const statusLabel: Record<string, string> = {
    generating: "? 生成中",
    completed: "? 已完成",
    failed: "? 失败",
  };

  const statusColor: Record<string, string> = {
    generating: "text-yellow-500",
    completed: "text-green-500",
    failed: "text-red-400",
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-white p-4">
      <div className="max-w-2xl mx-auto">
        {/* 头部 */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">?? 我的行程</h1>
            <p className="text-sm text-gray-400 mt-1">历史旅行计划</p>
          </div>
          <button
            onClick={() => navigate("/")}
            className="text-sm text-gray-400 hover:text-indigo-500 transition-colors cursor-pointer"
          >
            ← 返回首页
          </button>
        </div>

        {/* 列表 */}
        {loading ? (
          <p className="text-center text-gray-400 py-12">加载中…</p>
        ) : plans.length === 0 ? (
          <div className="text-center py-16">
            <p className="text-gray-400 text-lg mb-2">还没有旅行记录</p>
            <button
              onClick={() => navigate("/")}
              className="text-indigo-500 hover:text-indigo-600 text-sm transition-colors cursor-pointer"
            >
              去生成第一个计划 →
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {plans.map((plan) => (
              <div
                key={plan.id}
                className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 flex items-center justify-between hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => navigate(`/trip?plan_id=${plan.id}`)}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold text-gray-700">{plan.destination}</span>
                    <span className="text-xs text-gray-400">{plan.days}天</span>
                  </div>
                  <div className="text-xs text-gray-400">
                    预算 ￥{plan.budget} · {plan.interests || "无偏好"}
                  </div>
                  <div className="text-xs text-gray-400 mt-0.5">
                    {new Date(plan.created_at).toLocaleString("zh-CN")}
                  </div>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <span className={`text-xs ${statusColor[plan.status] || "text-gray-400"}`}>
                    {statusLabel[plan.status] || plan.status}
                  </span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(plan.id);
                    }}
                    className="text-xs text-gray-300 hover:text-red-400 transition-colors cursor-pointer"
                  >
                    删除
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
