import { useState } from "react"

function QueryInput({ onSubmit, loading }) {
  const [value, setValue] = useState("")

  const submit = () => {
    const query = value.trim()
    if (!query || loading) return
    onSubmit?.(query)
  }

  return (
    <div className="flex flex-col gap-3 rounded-lg border border-slate-200 bg-white p-4 shadow-sm sm:flex-row">
      <input
        type="text"
        value={value}
        onChange={event => setValue(event.target.value)}
        onKeyDown={event => {
          if (event.key === "Enter") submit()
        }}
        disabled={loading}
        placeholder="Ask about a figure, table, or section"
        className="min-h-10 flex-1 rounded-md border border-slate-300 px-3 text-sm text-slate-950 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 disabled:bg-slate-100"
      />
      <button
        type="button"
        onClick={submit}
        disabled={loading || !value.trim()}
        className="h-10 rounded-md bg-slate-950 px-5 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-slate-300"
      >
        Submit
      </button>
    </div>
  )
}

export default QueryInput
