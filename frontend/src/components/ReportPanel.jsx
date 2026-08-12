import { useEffect, useState } from 'react'
import { getIncidentReport, generateIncidentReport } from '../api'

export default function ReportPanel({ incident, asset }) {
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!incident) return
    setReport(null)
    setError(null)
    setLoading(true)
    getIncidentReport(incident.id)
      .then(setReport)
      .finally(() => setLoading(false))
  }, [incident])

  async function handleGenerate() {
    setGenerating(true)
    setError(null)
    try {
      const result = await generateIncidentReport(incident.id)
      setReport(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setGenerating(false)
    }
  }

  if (!incident) {
    return (
      <div className="flex h-full items-center justify-center rounded-lg border border-slate-800 bg-slate-900/60 p-8 text-center text-sm text-slate-500">
        Select an incident to view or generate its AI report
      </div>
    )
  }

  return (
    <div className="flex h-full flex-col rounded-lg border border-slate-800 bg-slate-900/60">
      <div className="border-b border-slate-800 px-5 py-4">
        <h2 className="text-sm font-medium uppercase tracking-wide text-slate-400">
          Incident Report
        </h2>
        <div className="mt-1 text-sm text-slate-200">{asset?.name}</div>
        <div className="text-xs text-slate-500">{incident.description}</div>
      </div>

      <div className="flex-1 overflow-y-auto p-5">
        {loading && <div className="text-sm text-slate-500">Loading...</div>}

        {!loading && !report && (
          <div className="flex flex-col items-start gap-3">
            <p className="text-sm text-slate-500">
              No report has been generated for this incident yet.
            </p>
            <button
              onClick={handleGenerate}
              disabled={generating}
              className="rounded-md bg-teal-500 px-4 py-2 text-sm font-medium text-slate-950 transition-colors hover:bg-teal-400 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {generating ? 'Generating...' : 'Generate AI Report'}
            </button>
            {error && <p className="text-sm text-red-400">{error}</p>}
          </div>
        )}

        {!loading && report && (
          <div className="space-y-6">
            <section>
              <h3 className="text-xs font-medium uppercase tracking-wide text-slate-500">
                Summary
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-300">{report.ai_summary}</p>
            </section>

            <section>
              <h3 className="text-xs font-medium uppercase tracking-wide text-slate-500">
                Root Cause Hypothesis
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-300">
                {report.root_cause_hypothesis}
              </p>
            </section>

            <section>
              <h3 className="text-xs font-medium uppercase tracking-wide text-slate-500">
                Stakeholder Email Draft
              </h3>
              <pre className="mt-2 whitespace-pre-wrap rounded-md border border-slate-800 bg-slate-950/60 p-4 font-sans text-sm leading-relaxed text-slate-300">
                {report.stakeholder_email_draft}
              </pre>
            </section>

            <button
              onClick={handleGenerate}
              disabled={generating}
              className="text-xs text-slate-500 underline decoration-dotted hover:text-slate-300 disabled:opacity-50"
            >
              {generating ? 'Regenerating...' : 'Regenerate report'}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
