import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { BookOpen, Search, RefreshCw, Trash2, Database, GitBranch, ChevronDown, ChevronUp } from 'lucide-react'
import { PageHeader } from '../components/common/PageHeader'
import { EmptyState } from '../components/common/EmptyState'
import { LoadingSpinner, LoadingState } from '../components/common/LoadingState'
import { ErrorState } from '../components/common/ErrorState'
import { ConfirmDialog } from '../components/common/ConfirmDialog'
import { Pagination } from '../components/common/Pagination'
import { SourceTraceDrawer } from '../components/evidence/SourceTraceDrawer'
import { useKnowledgeSearch } from '../hooks/useKnowledgeSearch'
import {
  useKnowledgeIndexSummary,
  useRebuildKnowledgeIndex,
  useDeleteKnowledgeIndex,
  useKnowledgeChunks,
} from '../hooks/useKnowledgeIndex'
import { useMyWorkspaceRole } from '../hooks/useMyWorkspaceRole'
import { useAuth } from '../hooks/useAuth'
import { canRebuildKnowledgeIndex, canDeleteKnowledgeIndex } from '../lib/auth/permissions'
import { useSourceTrace } from '../hooks/useAgentRetrieval'
import { cn, formatDateTime } from '../lib/utils'

const CHUNK_TEXT_PREVIEW = 200

export function KnowledgeSearchPage() {
  const { workspaceId = '' } = useParams<{ workspaceId: string }>()
  const { currentWorkspaceRole } = useAuth()
  const { role: derivedRole } = useMyWorkspaceRole(workspaceId)
  const role = derivedRole ?? currentWorkspaceRole

  const [query, setQuery] = useState('')
  const [topK, setTopK] = useState(10)
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [activeTab, setActiveTab] = useState<'search' | 'chunks'>('search')
  const [chunkPage, setChunkPage] = useState(1)
  const [chunkPageSize, setChunkPageSize] = useState(25)
  const [expandedChunks, setExpandedChunks] = useState<Set<string>>(new Set())
  const sourceTrace = useSourceTrace(workspaceId)

  const searchMutation = useKnowledgeSearch(workspaceId)
  const { data: summary } = useKnowledgeIndexSummary(workspaceId)
  const { data: chunks, isLoading: chunksLoading } = useKnowledgeChunks(workspaceId)
  const rebuildIndex = useRebuildKnowledgeIndex(workspaceId)
  const deleteIndex = useDeleteKnowledgeIndex(workspaceId)

  const canRebuild = canRebuildKnowledgeIndex(role)
  const canDelete = canDeleteKnowledgeIndex(role)

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      searchMutation.mutate({ query: query.trim(), limit: topK })
    }
  }

  const toggleChunkExpand = (id: string) => {
    setExpandedChunks((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const allChunks = chunks ?? []
  const totalChunks = allChunks.length
  const pagedChunks = allChunks.slice((chunkPage - 1) * chunkPageSize, chunkPage * chunkPageSize)

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <PageHeader
        title="Knowledge Search"
        subtitle="Search across indexed document content using semantic similarity"
        actions={
          <div className="flex items-center gap-2">
            {canRebuild && (
              <button
                onClick={() => rebuildIndex.mutate()}
                disabled={rebuildIndex.isPending}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-xl hover:bg-slate-50 transition-colors cursor-pointer disabled:opacity-60"
              >
                <RefreshCw className={cn('w-4 h-4', rebuildIndex.isPending && 'animate-spin')} />
                {rebuildIndex.isPending ? 'Rebuilding…' : 'Rebuild Index'}
              </button>
            )}
            {canDelete && (
              <button
                onClick={() => setConfirmDelete(true)}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-red-600 bg-white border border-red-200 rounded-xl hover:bg-red-50 transition-colors cursor-pointer"
              >
                <Trash2 className="w-4 h-4" />
                Delete Index
              </button>
            )}
          </div>
        }
      />

      {/* Index Summary */}
      {summary && (
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-card mb-6">
          <div className="flex items-center gap-2 mb-3">
            <Database className="w-4 h-4 text-slate-400" />
            <p className="text-sm font-semibold text-slate-700">Index Summary</p>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
            <div>
              <p className="text-slate-400 font-medium mb-0.5">Total Chunks</p>
              <p className="text-slate-900 font-semibold text-lg">{summary.total_chunks}</p>
            </div>
            <div>
              <p className="text-slate-400 font-medium mb-0.5">Documents</p>
              <p className="text-slate-900 font-semibold text-lg">{summary.documents_indexed}</p>
            </div>
            {summary.last_rebuilt_at && (
              <div className="col-span-2">
                <p className="text-slate-400 font-medium mb-0.5">Last Rebuilt</p>
                <p className="text-slate-700">{formatDateTime(summary.last_rebuilt_at)}</p>
              </div>
            )}
          </div>
          {summary.by_source_type && Object.keys(summary.by_source_type).length > 0 && (
            <div className="mt-3 pt-3 border-t border-slate-100">
              <p className="text-xs font-medium text-slate-400 mb-2">By Source Type</p>
              <div className="flex flex-wrap gap-2">
                {Object.entries(summary.by_source_type).map(([k, v]) => (
          <span key={k} className="px-2 py-0.5 bg-teal-50 text-teal-700 text-xs rounded-full border border-teal-200">
                    {k}: {v}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 border-b border-slate-200 mb-6">
        {(['search', 'chunks'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={cn(
              'px-4 py-2.5 text-sm font-medium transition-colors cursor-pointer border-b-2 -mb-px',
              activeTab === tab
                ? 'text-blue-700 border-blue-600'
                : 'text-slate-500 border-transparent hover:text-slate-700',
            )}
          >
            {tab === 'search'
              ? 'Semantic Search'
              : `Chunks${chunks ? ` (${chunks.length})` : ''}`}
          </button>
        ))}
      </div>

      {/* Search Tab */}
      {activeTab === 'search' && (
        <>
          <form onSubmit={handleSearch} className="mb-6">
            <div className="flex gap-2 max-w-2xl">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type="search"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search your documents…"
                  className="w-full pl-9 pr-4 py-2.5 text-sm text-slate-900 bg-white border border-slate-300 rounded-xl placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                />
              </div>
              <select
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                className="px-3 py-2.5 text-sm border border-slate-300 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {[5, 10, 20, 50].map((n) => (
                  <option key={n} value={n}>Top {n}</option>
                ))}
              </select>
              <button
                type="submit"
                disabled={!query.trim() || searchMutation.isPending}
                className={cn(
                  'px-5 py-2.5 text-sm font-semibold rounded-xl transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 flex items-center gap-2',
                  query.trim()
                    ? 'bg-blue-600 hover:bg-blue-700 text-white'
                    : 'bg-slate-100 text-slate-400 cursor-not-allowed',
                )}
              >
                {searchMutation.isPending && (
                  <LoadingSpinner className="w-3.5 h-3.5 border-white border-t-blue-300" />
                )}
                Search
              </button>
            </div>
          </form>

          {searchMutation.error && (
            <ErrorState error={searchMutation.error as Error} className="mb-4" />
          )}

          {searchMutation.data && (
            <div>
              <p className="text-sm text-slate-500 mb-4">
                {searchMutation.data.results.length} result{searchMutation.data.results.length !== 1 ? 's' : ''} for &ldquo;{searchMutation.data.query}&rdquo;
              </p>
              {searchMutation.data.results.length === 0 ? (
                <EmptyState
                  icon={<BookOpen className="w-12 h-12" />}
                  title="No results found"
                  body="Try a different search query, or rebuild the knowledge index."
                />
              ) : (
                <div className="space-y-3">
                  {searchMutation.data.results.map((result, i) => (
                    <div
                      key={result.chunk_id}
                      className="bg-white border border-slate-200 rounded-xl p-4 shadow-card"
                    >
                      <div className="flex items-start justify-between gap-3 mb-2">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-xs text-slate-400 font-medium">#{i + 1}</span>
                          {result.source_type && (
                            <span className="px-1.5 py-0.5 bg-teal-50 text-teal-700 text-xs rounded border border-teal-200">
                              {result.source_type}
                            </span>
                          )}
                          {result.chunk_type && (
                            <span className="px-1.5 py-0.5 bg-slate-100 text-slate-600 text-xs rounded">
                              {result.chunk_type}
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-2 flex-shrink-0">
                          <span className="text-xs font-medium text-teal-700 bg-teal-50 px-2 py-0.5 rounded-full border border-teal-200">
                            {(result.score * 100).toFixed(1)}%
                          </span>
                          {result.source_type && result.source_id && (
                            <button
                              onClick={() => sourceTrace.open(result.source_type!, result.source_id!)}
                              className="p-1 text-slate-400 hover:text-slate-600 rounded transition-colors cursor-pointer"
                              title="View source trace"
                            >
                              <GitBranch className="w-3.5 h-3.5" />
                            </button>
                          )}
                        </div>
                      </div>
                      <p className="text-sm text-slate-700 leading-relaxed">{result.chunk_text}</p>
                      {result.source_id && (
                        <p className="text-xs text-slate-400 mt-2 font-mono">
                          source: {result.source_id.slice(0, 20)}…
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {!searchMutation.data && !searchMutation.isPending && (
            <EmptyState
              icon={<BookOpen className="w-12 h-12" />}
              title="Search your documents"
              body="Enter a query above to search across indexed document content using semantic similarity."
            />
          )}
        </>
      )}

      {/* Chunks Tab */}
      {activeTab === 'chunks' && (
        <>
          {chunksLoading && <LoadingState />}
          {!chunksLoading && totalChunks === 0 && (
            <EmptyState
              icon={<Database className="w-12 h-12" />}
              title="No chunks indexed"
              body="Upload documents and rebuild the knowledge index to see chunks here."
            />
          )}
          {!chunksLoading && totalChunks > 0 && (
            <>
              <div className="space-y-3">
                {pagedChunks.map((chunk) => {
                  const isExpanded = expandedChunks.has(chunk.id)
                  const isLong = chunk.chunk_text.length > CHUNK_TEXT_PREVIEW
                  const displayText = isExpanded || !isLong
                    ? chunk.chunk_text
                    : chunk.chunk_text.slice(0, CHUNK_TEXT_PREVIEW) + '…'
                  return (
                    <div
                      key={chunk.id}
                      className="bg-white border border-slate-200 rounded-xl p-4 shadow-card"
                    >
                      <div className="flex items-center justify-between gap-3 mb-2">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="px-1.5 py-0.5 bg-blue-50 text-blue-600 text-xs rounded border border-blue-200">
                            {chunk.source_type}
                          </span>
                          <span className="px-1.5 py-0.5 bg-slate-100 text-slate-600 text-xs rounded">
                            {chunk.chunk_type}
                          </span>
                          {chunk.embedding_status && (
                            <span className={cn(
                              'px-1.5 py-0.5 text-xs rounded',
                              chunk.embedding_status === 'embedded'
                                ? 'bg-green-50 text-green-700'
                                : 'bg-amber-50 text-amber-700',
                            )}>
                              {chunk.embedding_status}
                            </span>
                          )}
                        </div>
                        <button
                          onClick={() => sourceTrace.open(chunk.source_type, chunk.source_id)}
                          className="p-1 text-slate-400 hover:text-slate-600 rounded transition-colors cursor-pointer flex-shrink-0"
                          title="View source trace"
                        >
                          <GitBranch className="w-3.5 h-3.5" />
                        </button>
                      </div>
                      <p className="text-sm text-slate-700 leading-relaxed">
                        {displayText}
                      </p>
                      {isLong && (
                        <button
                          onClick={() => toggleChunkExpand(chunk.id)}
                          className="mt-1.5 flex items-center gap-1 text-xs text-blue-700 hover:text-blue-600 cursor-pointer"
                        >
                          {isExpanded
                            ? <><ChevronUp className="w-3 h-3" /> Show less</>
                            : <><ChevronDown className="w-3 h-3" /> Show more</>}
                        </button>
                      )}
                      <p className="text-xs text-slate-400 mt-2 font-mono">
                        {chunk.source_id.slice(0, 20)}…
                      </p>
                    </div>
                  )
                })}
              </div>
              <Pagination
                page={chunkPage}
                pageSize={chunkPageSize}
                totalItems={totalChunks}
                onPageChange={setChunkPage}
                onPageSizeChange={(size) => { setChunkPageSize(size); setChunkPage(1) }}
              />
            </>
          )}
        </>
      )}

      {/* Delete confirm dialog */}
      <ConfirmDialog
        open={confirmDelete}
        title="Delete Knowledge Index"
        description="This will permanently delete all knowledge chunks for this workspace. This action cannot be undone."
        confirmLabel="Delete Index"
        variant="danger"
        onConfirm={() => {
          deleteIndex.mutate()
          setConfirmDelete(false)
        }}
        onCancel={() => setConfirmDelete(false)}
      />

      <SourceTraceDrawer state={sourceTrace} onClose={sourceTrace.close} />
    </div>
  )
}
