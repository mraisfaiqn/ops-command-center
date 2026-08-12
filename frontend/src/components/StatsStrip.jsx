function StatCard({ label, value, tone = 'default' }) {
  const toneClasses = {
    default: 'text-slate-100',
    critical: 'text-red-400',
    warning: 'text-amber-400',
    good: 'text-teal-400',
  }

  return (
    <div className="flex-1 rounded-lg border border-slate-800 bg-slate-900/60 px-5 py-4">
      <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
      <div className={`mt-1 text-3xl font-semibold tabular-nums ${toneClasses[tone]}`}>
        {value}
      </div>
    </div>
  )
}

export default function StatsStrip({ assets, incidents }) {
  const activeIncidents = incidents.filter((i) => !i.end_time).length
  const criticalIncidents = incidents.filter((i) => i.severity === 'critical').length
  const assetsDown = assets.filter((a) => a.status === 'down').length

  const resolved = incidents.filter((i) => i.end_time)
  const avgResolutionMin = resolved.length
    ? Math.round(
        resolved.reduce((sum, i) => {
          const mins = (new Date(i.end_time) - new Date(i.start_time)) / 60000
          return sum + mins
        }, 0) / resolved.length
      )
    : 0

  return (
    <div className="flex gap-4">
      <StatCard label="Active Incidents" value={activeIncidents} tone={activeIncidents > 0 ? 'warning' : 'good'} />
      <StatCard label="Critical" value={criticalIncidents} tone={criticalIncidents > 0 ? 'critical' : 'good'} />
      <StatCard label="Assets Down" value={assetsDown} tone={assetsDown > 0 ? 'critical' : 'good'} />
      <StatCard label="Avg. Resolution" value={`${avgResolutionMin}m`} />
      <StatCard label="Total Assets" value={assets.length} />
    </div>
  )
}
