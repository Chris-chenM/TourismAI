import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import type { PlanRequest } from "../api/trip";

const schema = z.object({
  destination: z.string().min(1, "请输入目的地"),
  days: z.coerce.number().min(1).max(30),
  budget: z.coerce.number().min(1, "请输入预算"),
  interests: z.string().optional(),
});

type FormData = z.infer<typeof schema>;

interface Props {
  onSubmit: (data: PlanRequest) => void;
  loading: boolean;
}

export default function SearchForm({ onSubmit, loading }: Props) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { destination: "杭州", days: 3, budget: 2000, interests: "历史文化、美食" },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">目的地</label>
          <input
            {...register("destination")}
            placeholder="如：杭州"
            className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm outline-none focus:border-indigo-400 transition-colors"
          />
          {errors.destination && <p className="text-red-400 text-xs mt-1">{errors.destination.message}</p>}
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">天数</label>
          <input
            {...register("days")}
            type="number"
            min={1}
            max={30}
            className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm outline-none focus:border-indigo-400 transition-colors"
          />
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-600 mb-1">预算（元）</label>
        <input
          {...register("budget")}
          type="number"
          placeholder="如：2000"
          className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm outline-none focus:border-indigo-400 transition-colors"
        />
        {errors.budget && <p className="text-red-400 text-xs mt-1">{errors.budget.message}</p>}
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-600 mb-1">兴趣偏好</label>
        <input
          {...register("interests")}
          placeholder="如：历史文化、美食、自然风光"
          className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm outline-none focus:border-indigo-400 transition-colors"
        />
      </div>
      <button
        type="submit"
        disabled={loading}
        className="w-full py-3 bg-indigo-500 hover:bg-indigo-600 disabled:bg-indigo-300 text-white font-medium rounded-lg transition-colors cursor-pointer"
      >
        {loading ? "生成中..." : "生成旅行计划"}
      </button>
    </form>
  );
}
