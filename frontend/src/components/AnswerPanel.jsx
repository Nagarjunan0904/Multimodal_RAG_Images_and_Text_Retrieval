function AnswerPanel({ answer, loading, latency_ms }) {
  return (
    <section className="min-h-96 rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-slate-950">Answer</h2>
        {latency_ms !== null && (
          <span className="text-xs font-medium text-slate-500">{latency_ms} ms</span>
        )}
      </div>

      <div className="whitespace-pre-wrap text-sm leading-6 text-slate-800">
        {answer || (loading ? "" : "Submit a query to generate an answer.")}
        {loading && <span className="ml-1 inline-block animate-pulse text-slate-950">|</span>}
      </div>
    </section>
  )
}

export default AnswerPanel
