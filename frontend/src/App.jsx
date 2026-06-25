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
      <main className="min-h-screen bg-[#0f1117] text-slate-200">
        <NavBar />
        <div className="flex min-h-[calc(100vh-73px)] items-center px-6 py-10">
          <div className="mx-auto w-full max-w-5xl">
            {error && (
              <div className="mb-4 rounded-lg border border-red-900/70 bg-red-950/50 px-4 py-3 text-sm text-red-300">
                {error}
              </div>
            )}

            <div className="grid gap-5 md:grid-cols-[1fr_1fr]">
              <PDFUploader onIngested={handleIngested} />
              <DocumentList docs={docs} selected={docId} onSelect={setDocId} />
            </div>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-[#0f1117] text-slate-200">
      <NavBar />

      <div className="mx-auto max-w-7xl px-6 py-6">
        <div className="mb-5 flex flex-col gap-3 rounded-xl border border-[#2d3148] bg-[#1a1d27] px-5 py-4 shadow-lg sm:flex-row sm:items-center sm:justify-between">
          <div className="min-w-0 text-sm text-slate-400">
            Selected document: <span className="font-medium text-slate-200">{docId}</span>
          </div>
          <button
            type="button"
            onClick={() => setDocId(null)}
            className="rounded-lg border border-indigo-500 px-4 py-2 text-sm font-medium text-indigo-400 transition-colors hover:bg-indigo-950"
          >
            Change document
          </button>
        </div>

        {error && (
          <div className="mb-4 rounded-lg border border-red-900/70 bg-red-950/50 px-4 py-3 text-sm text-red-300">
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

function NavBar() {
  return (
    <nav className="w-full border-b border-[#2d3148] bg-[#11131d]">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <div className="text-lg font-bold text-white">👁️ Multimodal RAG</div>
        <div className="rounded-full border border-[#2d3148] bg-[#1a1d27] px-3 py-1 text-xs font-medium text-slate-400">
          Powered by ColPali + GPT
        </div>
      </div>
    </nav>
  )
}

export default App
