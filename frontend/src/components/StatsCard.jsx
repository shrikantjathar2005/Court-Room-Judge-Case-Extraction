export function ConfidenceBadge({ score }) {
  const getColor = (s) => {
    if (s >= 80) return 'badge-success';
    if (s >= 60) return 'badge-warning';
    if (s >= 40) return 'badge-info';
    return 'badge-error';
  };

  const getLabel = (s) => {
    if (s >= 80) return 'High';
    if (s >= 60) return 'Medium';
    if (s >= 40) return 'Low';
    return 'Very Low';
  };

  return (
    <span className={`badge ${getColor(score)}`}>
      {score?.toFixed(1)}% — {getLabel(score)}
    </span>
  );
}

export function ConfidenceBar({ score }) {
  return (
    <div className="w-full bg-surface-700 rounded-full h-2.5 overflow-hidden">
      <div
        className="h-full rounded-full transition-all duration-500"
        style={{
          width: `${Math.min(score, 100)}%`,
          background:
            score >= 80
              ? 'linear-gradient(90deg, #10b981, #34d399)'
              : score >= 60
              ? 'linear-gradient(90deg, #f59e0b, #fbbf24)'
              : score >= 40
              ? 'linear-gradient(90deg, #06b6d4, #22d3ee)'
              : 'linear-gradient(90deg, #ef4444, #f87171)',
        }}
      />
    </div>
  );
}

export function StatusBadge({ status }) {
  const statusMap = {
    uploaded: 'badge-info',
    processing: 'badge-warning',
    processed: 'badge-success',
    reviewed: 'badge-success',
    pending: 'badge-neutral',
    completed: 'badge-success',
    failed: 'badge-error',
  };

  return (
    <span className={`badge ${statusMap[status] || 'badge-neutral'}`}>
      {status}
    </span>
  );
}

export function StatsCard({ title, value, subtitle, icon: Icon, gradient }) {
  return (
    <div className="glass-card p-6 hover:border-primary-500/30 transition-all duration-300 group">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-400 mb-1">{title}</p>
          <p className={`text-3xl font-bold bg-gradient-to-r ${gradient || 'from-white to-gray-300'} bg-clip-text text-transparent`}>
            {value}
          </p>
          {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
        </div>
        {Icon && (
          <div className="p-3 rounded-xl bg-primary-600/10 group-hover:bg-primary-600/20 transition-colors">
            <Icon className="w-6 h-6 text-primary-400" />
          </div>
        )}
      </div>
    </div>
  );
}
