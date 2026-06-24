import { useState } from "react"
import { ingestPdf } from "../api/client"

function PDFUploader({ onIngested }) {
  const [file, setFile] = useState(null)
  const [progress, setProgress] = useState(0)
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState("")
  const [error, setError] = useState("")

  const handleUpload = async () => {
    if (!file || uploading) return

    setUploading(true)
    setProgress(0)
    setError("")
    setMessage("")

    try {
      const result = await ingestPdf(file, setProgress)
      setMessage(`Indexed ${result.doc_id}`)
      onIngested?.(result.doc_id, result.num_pages, result.num_chunks)
    } catch (err) {
      setError(typeof err === "string" ? err : "Upload failed")
    } finally {
      setUploading(false)
    }
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-slate-950">Upload PDF</h2>
        <p className="mt-1 text-sm text-slate-600">Add a document to the multimodal index.</p>
      </div>

      <input
        type="file"
        accept=".pdf,application/pdf"
        onChange={event => setFile(event.target.files?.[0] ?? null)}
        className="block w-full text-sm text-slate-700 file:mr-4 file:rounded-md file:border-0 file:bg-slate-950 file:px-4 file:py-2 file:text-sm file:font-medium file:text-white hover:file:bg-slate-800"
      />

      <button
        type="button"
        onClick={handleUpload}
        disabled={!file || uploading}
        className="mt-4 inline-flex h-10 items-center justify-center rounded-md bg-emerald-600 px-4 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-slate-300"
      >
        {uploading ? (
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
        ) : (
          "Upload"
        )}
      </button>

      <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-100">
        <div
          className="h-full bg-emerald-500 transition-all"
          style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
        />
      </div>

      {message && <p className="mt-3 text-sm text-emerald-700">{message}</p>}
      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
    </section>
  )
}

export default PDFUploader
