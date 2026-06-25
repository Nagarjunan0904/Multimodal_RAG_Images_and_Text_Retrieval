import ReactMarkdown from "react-markdown"

function AnswerPanel({
  answer = "",
  loading = false,
  latency_ms = null,
  sources = [],
  used_image = false,
  onSourceClick,
}) {
  const isEmpty = answer === "" && !loading

  return (
    <section className="relative min-h-96 rounded-xl border border-[#2d3148] bg-[#1a1d27] p-5 shadow-lg">
      <div className="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-400">
        Answer
      </div>

      {used_image === true && (
        <div className="mb-4 rounded-lg border border-indigo-700 bg-indigo-900/50 px-4 py-2 text-sm font-semibold text-indigo-300">
          Visual: Answer grounded in page image
        </div>
      )}

      {isEmpty ? (
        <div className="flex min-h-64 items-center justify-center text-center text-sm text-slate-500">
          Ask a question to see the answer here, grounded in the retrieved page.
        </div>
      ) : loading && answer === "" ? (
        <div className="space-y-3">
          <div className="h-4 w-11/12 animate-pulse rounded bg-[#2d3148]" />
          <div className="h-4 w-4/5 animate-pulse rounded bg-[#2d3148]" />
          <div className="h-4 w-2/3 animate-pulse rounded bg-[#2d3148]" />
        </div>
      ) : (
        <div className="prose prose-invert max-w-none text-sm leading-6 text-slate-200">
          <ReactMarkdown>{answer}</ReactMarkdown>
          {loading && (
            <span className="ml-1 inline-block h-5 w-[2px] animate-pulse bg-current align-text-bottom" />
          )}
        </div>
      )}

      {sources.length > 0 && (
        <div className="mt-6 flex flex-wrap gap-2">
          {sources.map(source => (
            <button
              type="button"
              key={`${source.doc_id}-${source.page_num}`}
              onClick={() => onSourceClick?.(source.page_num)}
              className="rounded-full bg-[#2d3148] px-3 py-1.5 text-xs font-semibold text-slate-300 transition-colors hover:bg-indigo-900"
            >
              Page {source.page_num}
            </button>
          ))}
        </div>
      )}

      {latency_ms !== null && (
        <div className="mt-6 text-right text-xs text-slate-500">
          Generated in {(latency_ms / 1000).toFixed(2)}s
        </div>
      )}
    </section>
  )
}

export default AnswerPanel
