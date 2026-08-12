const STATUS_STYLES = {
  healthy: 'bg-teal-400',
  degraded: 'bg-amber-400',
  down: 'bg-red-400',
}

export default function AssetStatusGrid({ assets }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-5">
      <h2 className="mb-4 text-sm font-medium uppercase tracking-wide text-slate-400">
        Asset Status
      </h2>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
        {assets.map((asset) => (
          <div
            key={asset.id}
            className="flex items-center gap-2 rounded border border-slate-800 bg-slate-950/50 px-3 py-2"
          >
            <span
              className={`h-2 w-2 shrink-0 rounded-full ${STATUS_STYLES[asset.status]}`}
              title={asset.status}
            />
            <div className="min-w-0">
              <div className="truncate font-mono text-xs text-slate-200">{asset.name}</div>
              <div className="truncate text-[11px] text-slate-500">{asset.location}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
