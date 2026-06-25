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
    <section className="rounded-xl border border-[#2d3148] bg-[#1a1d27] p-4 shadow-lg">
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
          className="w-full rounded-xl border border-[#3d4166] bg-[#12141f] px-4 py-3 text-sm text-white outline-none transition-colors focus:border-indigo-500 disabled:cursor-not-allowed disabled:text-slate-500"
        />
        <button
          type="button"
          onClick={() => submit(value)}
          disabled={loading || !value.trim()}
          className="rounded-xl bg-indigo-600 px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-indigo-500 disabled:cursor-not-allowed disabled:bg-[#3d4166] disabled:text-slate-500"
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
            className="cursor-pointer rounded-full bg-[#2d3148] px-3 py-1 text-sm font-medium text-slate-300 transition-colors hover:bg-[#3d4166] disabled:cursor-not-allowed disabled:opacity-60"
          >
            {chip}
          </button>
        ))}
      </div>

      {statusLabel && (
        <div className="mt-3 animate-pulse text-sm font-medium text-indigo-300">
          {sseStatus?.includes("Retrieving") ? "" : "Generating: "}
          {statusLabel}
        </div>
      )}
    </section>
  )
}

export default QueryInput
