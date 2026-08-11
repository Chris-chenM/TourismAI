interface Props {
  /** 当前阶段，null 时不显示 */
  phase: string | null;
  /** 阶段文案 */
  message: string;
  /** 进度百分比 0-100 */
  progress: number;
  /** 错误信息，非空时变红 */
  error: string | null;
}

export default function LoadingSteps({ phase, message, progress, error }: Props) {
  if (!phase && !error) return null;

  const isError = !!error;
  const displayMessage = isError ? `❌ ${error}` : message;
  const barColor = isError ? "bg-red-400" : "bg-indigo-400";
  const textColor = isError ? "text-red-500" : "text-gray-500";
  const clampedProgress = isError ? 100 : Math.min(100, Math.max(0, progress));

  return (
    <div className="flex flex-col items-center justify-center py-12 gap-4">
      <p className={`text-lg ${isError ? "" : "animate-pulse"} ${textColor}`}>
        {displayMessage}
      </p>
      <div className="w-48 h-1.5 bg-gray-100 rounded-full overflow-hidden">
        <div
          className={`h-full ${barColor} rounded-full transition-all duration-700`}
          style={{ width: `${clampedProgress}%` }}
        />
      </div>
    </div>
  );
}
