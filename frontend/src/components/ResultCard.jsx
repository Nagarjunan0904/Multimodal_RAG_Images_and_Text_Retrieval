import { useEffect, useState } from "react"

const STATIC_PAGE_BASE = "http://localhost:8000/static/pages"

function ResultCard({ pages = [], chunks = [] }) {
  const [imageError, setImageError] = useState(false)
  const page = pages[0]
  const chunk = chunks[0]
  const pageNum = page?.page_num
  const imageScore = Number(page?.score ?? 0)
  const textScore = Number(chunk?.score ?? 0)
  const imageUrl = page?.image_path ? `${STATIC_PAGE_BASE}/${basename(page.image_path)}` : null
  const textChunk = chunk?.text ?? ""
  const preview = textChunk.length > 300 ? `${textChunk.slice(0, 300)}...` : textChunk

  useEffect(() => {
    setImageError(false)
  }, [imageUrl])

  if (!pages.length) {
    return (
      <section className="flex min-h-96 items-center justify-center rounded-lg border border-slate-200 bg-white p-5 text-center shadow-sm">
        <div>
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 text-slate-400">
            ?
          </div>
          <p className="text-sm text-slate-500">Ask a question to see results</p>
        </div>
      </section>
    )
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="relative overflow-hidden rounded-lg border border-slate-200 bg-slate-50">
        <div className="absolute left-3 top-3 z-10 rounded-full bg-emerald-600 px-3 py-1 text-xs font-semibold text-white shadow-sm">
          Page {pageNum}
        </div>
        {imageUrl && !imageError ? (
          <img
            src={imageUrl}
            alt={`Page ${pageNum}`}
            onError={() => setImageError(true)}
            className="max-h-[420px] w-full rounded-lg object-contain"
          />
        ) : (
          <div className="flex min-h-[320px] items-center justify-center rounded-lg bg-slate-200 text-sm font-medium text-slate-500">
            Image unavailable
          </div>
        )}
      </div>

      <div className="mt-4">
        <div className="mb-2 text-xs font-semibold uppercase text-slate-500">Matched text</div>
        <div className="max-h-[150px] overflow-y-auto rounded-md border border-slate-200 bg-slate-50 p-3 text-sm leading-6 text-slate-700">
          {preview || "No matched text returned"}
        </div>
      </div>

      <div className="mt-4 space-y-3">
        <ScoreBar label="Visual match" score={imageScore} color="bg-emerald-500" />
        <ScoreBar label="Text match" score={textScore} color="bg-sky-500" />
      </div>
    </section>
  )
}

function ScoreBar({ label, score, color }) {
  const percent = Math.round(clamp(score) * 100)

  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-xs font-medium text-slate-600">
        <span>{label}</span>
        <span>{percent}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-slate-100">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${percent}%` }} />
      </div>
    </div>
  )
}

function basename(path) {
  return String(path).split(/[\\/]/).pop()
}

function clamp(value) {
  return Math.min(1, Math.max(0, Number.isFinite(value) ? value : 0))
}

export default ResultCard
