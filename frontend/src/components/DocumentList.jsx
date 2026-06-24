function DocumentList({ docs, selected, onSelect }) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-950">Documents</h2>

      {docs.length === 0 ? (
        <p className="mt-4 text-sm text-slate-500">No documents ingested yet</p>
      ) : (
        <div className="mt-4 space-y-2">
          {docs.map(doc => (
            <button
              type="button"
              key={doc}
              onClick={() => onSelect?.(doc)}
              className={`block w-full truncate rounded-md border px-3 py-2 text-left text-sm ${
                selected === doc
                  ? "border-emerald-500 bg-emerald-50 text-emerald-950"
                  : "border-slate-200 bg-white text-slate-700 hover:bg-slate-50"
              }`}
            >
              {doc}
            </button>
          ))}
        </div>
      )}
    </section>
  )
}

export default DocumentList
