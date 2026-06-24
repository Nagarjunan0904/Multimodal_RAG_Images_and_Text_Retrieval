function ResultCard({ pages, chunks }) {
  const page = pages[0]
  const chunk = chunks[0]

  if (!page && !chunk) {
    return (
      <section className="min-h-96 rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <p className="text-sm text-slate-500">Ask a question to see results</p>
      </section>
    )
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-slate-950">Retrieved Evidence</h2>
        {page?.page_num && (
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
            Page {page.page_num}
          </span>
        )}
      </div>

      {page?.image_path ? (
        <img
          src={page.image_path}
          alt={`Page ${page.page_num ?? ""}`}
          className="aspect-[3/4] w-full rounded-md border border-slate-200 object-contain"
        />
      ) : (
        <div className="flex aspect-[3/4] items-center justify-center rounded-md border border-dashed border-slate-300 text-sm text-slate-500">
          No page image
        </div>
      )}

      <div className="mt-4 rounded-md bg-slate-50 p-4">
        <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
          Top text chunk
        </div>
        <p className="text-sm leading-6 text-slate-700">
          {chunk?.text ? `${chunk.text.slice(0, 200)}${chunk.text.length > 200 ? "..." : ""}` : "No text chunk returned"}
        </p>
      </div>
    </section>
  )
}

export default ResultCard
