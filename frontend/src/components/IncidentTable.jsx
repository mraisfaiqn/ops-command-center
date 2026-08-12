const SEVERITY_STYLES = {
  critical: 'bg-red-500/15 text-red-400 border-red-500/30',
  high: 'bg-orange-500/15 text-orange-400 border-orange-500/30',
  medium: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
  low: 'bg-slate-500/15 text-slate-400 border-slate-500/30',
}

function formatDuration(start, end) {
  const startTime = new Date(start)
  const endTime = end ? new Date(end) : new Date()
  const mins = Math.round((endTime - startTime) / 60000)
  if (mins < 60) return `${mins}m`
  return `${Math.floor(mins / 60)}h ${mins % 60}m`
}

export default function IncidentTable({ incidents, assetsById, onSelect, selectedId }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/60">
      <h2 className="border-b border-slate-800 px-5 py-4 text-sm font-medium uppercase tracking-wide text-slate-400">
        Incidents
      </h2>
      <div className="divide-y divide-slate-800">
        {incidents.map((incident) => {
          const asset = assetsById[incident.asset_id]
          const isSelected = incident.id === selectedId
          return (
            <button
              key={incident.id}
              onClick={() => onSelect(incident)}
              className={`flex w-full items-start gap-3 px-5 py-3 text-left transition-colors hover:bg-slate-800/50 ${
                isSelected ? 'bg-slate-800/70' : ''
              }`}
            >
              <span
                className={`mt-0.5 shrink-0 rounded border px-2 py-0.5 text-[11px] font-medium uppercase ${
                  SEVERITY_STYLES[incident.severity]
                }`}
              >
                {incident.severity}
              </span>
              <div className="min-w-0 flex-1">
                <div className="truncate text-sm text-slate-200">{incident.description}</div>
                <div className="mt-0.5 text-xs text-slate-500">
                  {asset?.name ?? 'Unknown asset'} &middot;{' '}
                  {!incident.end_time ? 'Ongoing' : `Resolved in ${formatDuration(incident.start_time, incident.end_time)}`}
                </div>
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
