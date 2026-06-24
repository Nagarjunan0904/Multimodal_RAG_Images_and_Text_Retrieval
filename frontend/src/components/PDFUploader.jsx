import axios from "axios"
import { useRef, useState } from "react"
import { BASE } from "../api/client"

const DEMO_DOC_ID = "bffb0169-aa17-401e-82d9-2f972556a2b0"

function PDFUploader({ onIngested }) {
  const inputRef = useRef(null)
  const [file, setFile] = useState(null)
  const [dragging, setDragging] = useState(false)
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState("idle")
  const [result, setResult] = useState(null)
  const [error, setError] = useState("")

  const selectFile = nextFile => {
    if (!nextFile) return
    setFile(nextFile)
    setStatus("idle")
    setResult(null)
    setError("")
    setProgress(0)
  }

  const upload = async () => {
    if (!file || status === "uploading" || status === "indexing") return

    const formData = new FormData()
    formData.append("file", file)
    setStatus("uploading")
    setProgress(0)
    setError("")
    setResult(null)

    try {
      const response = await axios.post(`${BASE}/ingest`, formData, {
        onUploadProgress: e => {
          setProgress(e.total > 0 ? (e.loaded / e.total) * 100 : 50)
          if (e.total > 0 && e.loaded >= e.total) setStatus("indexing")
        },
      })
      setStatus("done")
      setProgress(100)
      setResult(response.data)
      onIngested?.(response.data.doc_id, response.data.num_pages, response.data.num_chunks)
    } catch (err) {
      setStatus("error")
      setError(err.response?.data?.detail ?? err.message ?? "Upload failed")
    }
  }

  const tryDemo = () => {
    const demo = { doc_id: DEMO_DOC_ID, num_pages: 70, num_chunks: 91 }
    setResult(demo)
    setStatus("done")
    setError("")
    onIngested?.(DEMO_DOC_ID, 70, 91)
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-slate-950">Upload PDF</h2>
        <p className="mt-1 text-sm text-slate-600">Index a document or open the demo.</p>
      </div>

      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        onDragOver={event => {
          event.preventDefault()
          setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={event => {
          event.preventDefault()
          setDragging(false)
          selectFile(event.dataTransfer.files?.[0])
        }}
        className={`flex min-h-40 w-full flex-col items-center justify-center rounded-lg border-2 border-dashed px-4 text-center transition ${
          dragging
            ? "border-emerald-500 bg-emerald-50"
            : "border-slate-300 bg-slate-50 hover:border-slate-400"
        }`}
      >
        <span className="text-3xl text-slate-400">PDF</span>
        <span className="mt-3 text-sm font-medium text-slate-800">
          {file ? file.name : "Drop a PDF here or click to browse"}
        </span>
        <span className="mt-1 text-xs text-slate-500">Only .pdf files are accepted</span>
      </button>

      <input
        ref={inputRef}
        type="file"
        accept=".pdf"
        onChange={event => selectFile(event.target.files?.[0])}
        className="hidden"
      />

      <div className="mt-4 flex flex-col gap-3 sm:flex-row">
        <button
          type="button"
          onClick={upload}
          disabled={!file || status === "uploading" || status === "indexing"}
          className="h-10 rounded-md bg-emerald-600 px-4 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          {status === "uploading" ? "Uploading..." : "Upload document"}
        </button>
        <button
          type="button"
          onClick={tryDemo}
          className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          Try demo: NVIDIA H100 Whitepaper
        </button>
      </div>

      {(status === "uploading" || status === "indexing") && (
        <div className="mt-4">
          <div className="h-2 overflow-hidden rounded-full bg-slate-100">
            <div className="h-full bg-emerald-500 transition-all" style={{ width: `${progress}%` }} />
          </div>
          {status === "indexing" && (
            <p className="mt-2 animate-pulse text-sm text-emerald-700">Indexing pages...</p>
          )}
        </div>
      )}

      {status === "done" && result && (
        <p className="mt-4 text-sm font-medium text-emerald-700">
          Indexed {result.num_pages} pages, {result.num_chunks} text chunks
        </p>
      )}
      {status === "error" && <p className="mt-4 text-sm font-medium text-red-600">{error}</p>}
    </section>
  )
}

export default PDFUploader
