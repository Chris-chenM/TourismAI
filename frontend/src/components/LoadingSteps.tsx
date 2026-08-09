import { useEffect, useState } from "react";

const STEPS = ["🔍 正在搜索景点…", "🧠 AI 正在规划路线…", "🗺 正在生成地图…"];

interface Props {
  show: boolean;
}

export default function LoadingSteps({ show }: Props) {
  const [step, setStep] = useState(0);

  useEffect(() => {
    if (!show) {
      setStep(0);
      return;
    }
    const timer = setInterval(() => {
      setStep((s) => (s + 1) % STEPS.length);
    }, 1800);
    return () => clearInterval(timer);
  }, [show]);

  if (!show) return null;

  return (
    <div className="flex flex-col items-center justify-center py-12 gap-4 animate-pulse">
      <p className="text-gray-500 text-lg">{STEPS[step]}</p>
      <div className="w-48 h-1.5 bg-gray-100 rounded-full overflow-hidden">
        <div
          className="h-full bg-indigo-400 rounded-full transition-all duration-1000"
          style={{ width: `${((step + 1) / STEPS.length) * 100}%` }}
        />
      </div>
    </div>
  );
}
