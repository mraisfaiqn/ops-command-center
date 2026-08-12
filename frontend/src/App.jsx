import { useEffect, useState } from 'react'
import './index.css'
import { getAssets, getIncidents } from './api'
import StatsStrip from './components/StatsStrip'
import AssetStatusGrid from './components/AssetStatusGrid'
import IncidentTable from './components/IncidentTable'
import ReportPanel from './components/ReportPanel'

function App() {
  const [assets, setAssets] = useState([])
  const [incidents, setIncidents] = useState([])
  const [selectedIncident, setSelectedIncident] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([getAssets(), getIncidents()])
      .then(([assetsData, incidentsData]) => {
        setAssets(assetsData)
        setIncidents(incidentsData)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  const assetsById = Object.fromEntries(assets.map((a) => [a.id, a]))

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-slate-400">
        Loading dashboard...
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 p-8 text-center text-red-400">
        Failed to load data: {error}. Is the backend running on localhost:8000?
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-950 p-8 text-slate-100">
      <header className="mb-6">
        <h1 className="text-2xl font-semibold tracking-tight">Ops Command Center</h1>
        <p className="text-sm text-slate-500">Data center asset &amp; network outage tracker</p>
      </header>

      <div className="mb-6">
        <StatsStrip assets={assets} incidents={incidents} />
      </div>

      <div className="mb-6">
        <AssetStatusGrid assets={assets} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <IncidentTable
          incidents={incidents}
          assetsById={assetsById}
          onSelect={setSelectedIncident}
          selectedId={selectedIncident?.id}
        />
        <ReportPanel
          incident={selectedIncident}
          asset={selectedIncident ? assetsById[selectedIncident.asset_id] : null}
        />
      </div>
    </div>
  )
}

export default App