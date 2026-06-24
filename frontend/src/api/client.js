export const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000"

export async function ingestPdf(file, onProgress) {
  const form = new FormData()
  form.append("file", file)
  const xhr = new XMLHttpRequest()
  return new Promise((resolve, reject) => {
    xhr.upload.onprogress = e => e.lengthComputable && onProgress?.(e.loaded / e.total * 100)
    xhr.onload = () => xhr.status === 200 ? resolve(JSON.parse(xhr.responseText)) : reject(xhr.responseText)
    xhr.onerror = () => reject("Network error")
    xhr.open("POST", `${BASE}/ingest`)
    xhr.send(form)
  })
}

export async function getDocuments() {
  const res = await fetch(`${BASE}/documents`)
  return res.json()
}

export async function postQuery(query, doc_id) {
  const res = await fetch(`${BASE}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, doc_id }),
  })
  return res.json()
}

export function streamQuery(query, doc_id, onSources, onToken, onDone, onError, onStatus) {
  const url = `${BASE}/query/stream?query=${encodeURIComponent(query)}&doc_id=${encodeURIComponent(doc_id)}`
  const es = new EventSource(url)
  es.onmessage = e => {
    const data = JSON.parse(e.data)
    if (data.type === "status") onStatus?.(data.content)
    else if (data.type === "sources") onSources?.(data.pages, data.chunks)
    else if (data.type === "token") onToken?.(data.content)
    else if (data.type === "done") { onDone?.(data.latency_ms); es.close() }
    else if (data.type === "error") { onError?.(data.message); es.close() }
  }
  es.onerror = () => { onError?.("Stream connection lost"); es.close() }
  return () => es.close()
}
