import { useEffect, useState } from "react"
import { getDocuments, streamQuery } from "./api/client"
import AnswerPanel from "./components/AnswerPanel"
import DocumentList from "./components/DocumentList"
import PDFUploader from "./components/PDFUploader"
import QueryInput from "./components/QueryInput"
import ResultCard from "./components/ResultCard"

function App() {
  const [docId, setDocId] = useState(null)
  const [docs, setDocs] = useState([])
  const [query, setQuery] = useState("")
  const [sources, setSources] = useState({ pages: [], chunks: [] })
  const [answer, setAnswer] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [latency, setLatency] = useState(null)
  const [sseStatus, setSseStatus] = useState(null)
  const [usedImage, setUsedImage] = useState(false)

  useEffect(() => {
    let mounted = true

    getDocuments()
      .then(data => {
        if (mounted) setDocs(data.documents ?? [])
      })
      .catch(err => {
        if (mounted) setError(typeof err === "string" ? err : "Could not load documents")
      })

    return () => {
      mounted = false
    }
  }, [])

  const handleIngested = (newDocId) => {
    setDocId(newDocId)
    setDocs(prev => (prev.includes(newDocId) ? prev : [newDocId, ...prev]))
  }

  const handleQuery = (nextQuery) => {
    if (!docId) return

    setQuery(nextQuery)
    setLoading(true)
    setAnswer("")
    setLatency(null)
    setSseStatus(null)
    setUsedImage(false)
    setError(null)
    setSources({ pages: [], chunks: [] })

    streamQuery(
      nextQuery,
      docId,
      (pages, chunks) => {
        setSources({ pages, chunks })
        setUsedImage(pages.length > 0)
      },
      token => setAnswer(prev => prev + token),
      ms => {
        setLatency(ms)
        setLoading(false)
        setSseStatus(null)
      },
      err => {
        setError(err)
        setLoading(false)
        setSseStatus(null)
      },
      status => setSseStatus(status),
    )
  }

  if (docId === null) {
    return (
      <main className="min-h-screen bg-slate-100 px-4 py-8 text-slate-950">
        <div className="mx-auto max-w-5xl">
          <header className="mb-6">
            <h1 className="text-2xl font-semibold">Multimodal RAG</h1>
            <p className="mt-1 text-sm text-slate-600">Upload or select a document to begin.</p>
          </header>

          {error && (
            <div className="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <div className="grid gap-5 md:grid-cols-[1fr_1fr]">
            <PDFUploader onIngested={handleIngested} />
            <DocumentList docs={docs} selected={docId} onSelect={setDocId} />
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-slate-100 text-slate-950">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="min-w-0">
            <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Selected document
            </div>
            <div className="truncate text-sm font-medium text-slate-950">{docId}</div>
          </div>
          <button
            type="button"
            onClick={() => setDocId(null)}
            className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Change document
          </button>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-4 py-6">
        {error && (
          <div className="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <QueryInput onSubmit={handleQuery} loading={loading} sseStatus={sseStatus} />

        <div className="mt-6 grid gap-6 lg:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
          <ResultCard pages={sources.pages} chunks={sources.chunks} />
          <AnswerPanel
            answer={answer}
            loading={loading}
            latency_ms={latency}
            sources={sources.pages}
            used_image={usedImage}
            onSourceClick={() => {}}
          />
        </div>

        {query && (
          <div className="mt-4 text-xs text-slate-500">
            Last query: {query}
          </div>
        )}
      </div>
    </main>
  )
}

export default App
