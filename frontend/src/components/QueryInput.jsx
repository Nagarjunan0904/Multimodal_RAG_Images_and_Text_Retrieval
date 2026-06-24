import { useState } from "react"

const EXAMPLES = [
  "What does the architecture diagram show?",
  "Summarize the memory bandwidth specs",
  "What are the key differences between SXM and PCIe?",
  "Explain the Transformer Engine",
]

function QueryInput({ onSubmit, loading, sseStatus }) {
  const [value, setValue] = useState("")

  const submit = query => {
    const nextQuery = query.trim()
    if (!nextQuery || loading) return
    onSubmit?.(nextQuery)
  }

  const statusLabel = sseStatus?.includes("Retrieving")
    ? "Retrieving relevant pages..."
    : loading
      ? "Generating answer..."
      : null

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex flex-col gap-3 sm:flex-row">
        <input
          type="text"
          value={value}
          onChange={event => setValue(event.target.value)}
          onKeyDown={event => {
            if (event.key === "Enter") submit(value)
          }}
          disabled={loading}
          placeholder="Ask about a diagram, chart, or anything in this document..."
          className="h-11 flex-1 rounded-md border border-slate-300 px-3 text-sm text-slate-950 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 disabled:bg-slate-100"
        />
        <button
          type="button"
          onClick={() => submit(value)}
          disabled={loading || !value.trim()}
          className="h-11 rounded-md bg-slate-950 px-5 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          Submit
        </button>
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        {EXAMPLES.map(chip => (
          <button
            type="button"
            key={chip}
            onClick={() => {
              setValue(chip)
              submit(chip)
            }}
            disabled={loading}
            className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-700 hover:border-emerald-300 hover:bg-emerald-50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {chip}
          </button>
        ))}
      </div>

      {statusLabel && (
        <div className="mt-3 animate-pulse text-sm font-medium text-emerald-700">
          {sseStatus?.includes("Retrieving") ? "" : "✍️ "}
          {statusLabel}
        </div>
      )}
    </section>
  )
}

export default QueryInput
