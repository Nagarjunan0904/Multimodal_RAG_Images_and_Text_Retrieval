import { useEffect, useState } from "react"

import { BASE } from "../api/client"

function ResultCard({ pages = [], chunks = [] }) {
  const [imageError, setImageError] = useState(false)
  const page = pages[0]
  const chunk = chunks[0]
  const pageNum = page?.page_num
  const imageScore = Number(page?.score ?? 0)
  const textScore = Number(chunk?.score ?? 0)
  const imageUrl = page?.image_path ? getImageUrl(page.image_path) : null
  const textChunk = chunk?.text ?? ""
  const preview = textChunk.length > 300 ? `${textChunk.slice(0, 300)}...` : textChunk

  useEffect(() => {
    setImageError(false)
  }, [imageUrl])

  if (!pages.length) {
    return (
      <section className="flex min-h-96 items-center justify-center rounded-xl border border-[#2d3148] bg-[#1a1d27] p-5 text-center shadow-lg">
        <div>
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-[#12141f] text-slate-500">
            ?
          </div>
          <p className="text-sm text-slate-500">Ask a question to see results</p>
        </div>
      </section>
    )
  }

  return (
    <section className="rounded-xl border border-[#2d3148] bg-[#1a1d27] p-5 shadow-lg">
      <div className="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-400">
        Retrieved Context
      </div>

      <div className="relative overflow-hidden rounded-lg bg-[#12141f]">
        <div className="absolute left-2 top-2 z-10 rounded bg-indigo-600 px-2 py-1 text-xs font-semibold text-white shadow-sm">
          Page {pageNum}
        </div>
        {imageUrl && !imageError ? (
          <img
            src={imageUrl}
            alt={`Page ${pageNum}`}
            onError={() => setImageError(true)}
            className="max-h-[420px] w-full object-contain"
          />
        ) : (
          <div className="flex min-h-[320px] items-center justify-center bg-[#12141f] text-sm font-medium text-slate-500">
            Image unavailable
          </div>
        )}
      </div>

      <div className="mt-4">
        <div className="mb-2 text-xs font-semibold uppercase text-slate-500">Matched text</div>
        <div className="max-h-[150px] overflow-y-auto rounded-lg bg-[#12141f] p-3 text-sm leading-6 text-slate-400">
          {preview || "No matched text returned"}
        </div>
      </div>

      <div className="mt-4 space-y-3">
        <ScoreBar label="Visual match" score={imageScore} color="bg-indigo-500" />
        <ScoreBar label="Text match" score={textScore} color="bg-emerald-500" />
      </div>
    </section>
  )
}

function ScoreBar({ label, score, color }) {
  const percent = Math.round(clamp(score) * 100)

  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-xs font-medium text-slate-400">
        <span>{label}</span>
        <span>{percent}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-[#12141f]">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${percent}%` }} />
      </div>
    </div>
  )
}

function getImageUrl(image_path) {
  const parts = image_path.replace(/\\/g, "/").split("/")
  return `${BASE}/static/pages/${parts[parts.length - 2]}/${parts[parts.length - 1]}`
}

function clamp(value) {
  return Math.min(1, Math.max(0, Number.isFinite(value) ? value : 0))
}

export default ResultCard
