function DocumentList({ docs, selected, onSelect }) {
  return (
    <section className="rounded-xl border border-[#2d3148] bg-[#1a1d27] p-5 shadow-lg">
      <h2 className="text-lg font-semibold text-white">Documents</h2>

      {docs.length === 0 ? (
        <p className="mt-4 text-sm text-slate-500">No documents ingested yet</p>
      ) : (
        <div className="mt-4 space-y-2">
          {docs.map(doc => (
            <button
              type="button"
              key={doc}
              onClick={() => onSelect?.(doc)}
              className={`block w-full truncate rounded-lg px-3 py-2 text-left text-sm transition-colors ${
                selected === doc
                  ? "border-l-2 border-indigo-500 bg-indigo-900 text-slate-100"
                  : "text-slate-300 hover:bg-[#2d3148]"
              }`}
            >
              <span className="mr-2">▣</span>
              {doc.slice(0, 8)}...
            </button>
          ))}
        </div>
      )}
    </section>
  )
}

export default DocumentList
