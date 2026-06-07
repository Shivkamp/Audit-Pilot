import { useState, useRef, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import {
  Send,
  Bot,
  User,
  Trash2,
  Copy,
  Check,
  AlertTriangle,
  AlertCircle,
  RotateCcw,
  FileText,
  Link as LinkIcon,
  ChevronDown,
  ChevronRight,
  Sparkles,
} from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { motion, AnimatePresence } from 'motion/react'
import { useAgentChat } from '../hooks/useAgentChat'
import { LoadingSpinner } from '../components/common/LoadingState'
import { cn } from '../lib/utils'
import { chatMessageTransition } from '../lib/animation'
import type { AgentChatResponse, CitationItem, EvidenceItem, SourceTraceItem } from '../types/agent'

const SUGGESTED_QUESTIONS = [
  'What are the risks in my data?',
  'Summarize high severity risks.',
  'Why was short deposit flagged?',
  'Show evidence for duplicate invoice DUP-INV-777.',
  'Explain TDS mismatch for Noble Consulting LLP.',
  'Which vendors have missing PAN?',
]

interface ResponseDetailsPanelProps {
  response: AgentChatResponse
}

function ResponseDetailsPanel({ response }: ResponseDetailsPanelProps) {
  const [showWarnings, setShowWarnings] = useState(true)
  const [showCitations, setShowCitations] = useState(false)
  const [showEvidence, setShowEvidence] = useState(false)
  const [showSourceTraces, setShowSourceTraces] = useState(false)

  const hasWarnings = response.warnings && response.warnings.length > 0
  const hasCitations = response.citations && response.citations.length > 0
  const hasEvidence = response.evidence && response.evidence.length > 0
  const hasSourceTraces = response.source_traces && response.source_traces.length > 0
  const hasMeta = response.intent || response.confidence != null || response.provider

  if (!hasWarnings && !hasCitations && !hasEvidence && !hasSourceTraces && !hasMeta) return null

  return (
    <div className="mt-3 space-y-2 text-xs border-t border-slate-100 pt-3">
      {hasMeta && (
        <div className="flex flex-wrap gap-3 text-slate-400">
          {response.intent && (
            <span>Intent: <span className="text-slate-600 font-medium">{response.intent}</span></span>
          )}
          {response.confidence != null && (
            <span>Confidence: <span className="text-slate-600 font-medium">
              {isNaN(parseFloat(response.confidence))
                ? response.confidence
                : `${(parseFloat(response.confidence) * 100).toFixed(0)}%`}
            </span></span>
          )}
          {response.provider && (
            <span>Model: <span className="text-slate-600 font-medium">{response.provider}{response.model ? ` / ${response.model}` : ''}</span></span>
          )}
        </div>
      )}

      {hasWarnings && (
        <div>
          <button
            onClick={() => setShowWarnings((v) => !v)}
            className="flex items-center gap-1.5 text-amber-700 font-medium cursor-pointer hover:opacity-80"
          >
            {showWarnings ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
            <AlertTriangle className="w-3 h-3" />
            {response.warnings!.length} warning{response.warnings!.length !== 1 ? 's' : ''}
          </button>
          {showWarnings && (
            <ul className="mt-1.5 pl-4 space-y-1">
              {response.warnings!.map((w, i) => (
                <li key={i} className="text-amber-800 list-disc">{w}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      {hasCitations && (
        <div>
          <button
            onClick={() => setShowCitations((v) => !v)}
            className="flex items-center gap-1.5 text-blue-700 font-medium cursor-pointer hover:opacity-80"
          >
            {showCitations ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
            <LinkIcon className="w-3 h-3" />
            {response.citations!.length} citation{response.citations!.length !== 1 ? 's' : ''}
          </button>
          {showCitations && (
            <div className="mt-1.5 space-y-1">
              {(response.citations as CitationItem[]).map((c, i) => (
                <div key={i} className="pl-4 text-slate-600 flex flex-wrap items-center gap-x-2">
                  {c.source_type && (
                    <span className="px-1 py-0.5 bg-blue-50 text-blue-700 rounded text-xs">{c.source_type}</span>
                  )}
                  <span className="font-mono text-xs">
                    {c.chunk_id ?? c.source_id ?? c.document_id ?? `citation-${i + 1}`}
                  </span>
                  {c.relevance_score != null && (
                    <span className="text-slate-400 text-xs">({(c.relevance_score * 100).toFixed(1)}%)</span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {hasEvidence && (
        <div>
          <button
            onClick={() => setShowEvidence((v) => !v)}
            className="flex items-center gap-1.5 text-teal-700 font-medium cursor-pointer hover:opacity-80"
          >
            {showEvidence ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
            <FileText className="w-3 h-3" />
            {response.evidence!.length} evidence item{response.evidence!.length !== 1 ? 's' : ''}
          </button>
          {showEvidence && (
            <div className="mt-1.5 space-y-1">
              {(response.evidence as EvidenceItem[]).map((ev, i) => (
                <div key={i} className="pl-4 text-slate-600">
                  {ev.source_type && <span className="px-1 py-0.5 bg-teal-50 text-teal-700 rounded mr-2">{ev.source_type}</span>}
                  <span className="font-mono text-xs">{ev.source_id}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {hasSourceTraces && (
        <div>
          <button
            onClick={() => setShowSourceTraces((v) => !v)}
            className="flex items-center gap-1.5 text-slate-600 font-medium cursor-pointer hover:opacity-80"
          >
            {showSourceTraces ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
            <FileText className="w-3 h-3" />
            {response.source_traces!.length} source trace{response.source_traces!.length !== 1 ? 's' : ''}
          </button>
          {showSourceTraces && (
            <div className="mt-1.5 space-y-1">
              {(response.source_traces as SourceTraceItem[]).map((st, i) => (
                <div key={i} className="pl-4 text-slate-600">
                  {st.source_type && <span className="px-1 py-0.5 bg-slate-100 text-slate-600 rounded mr-2">{st.source_type}</span>}
                  <span className="font-mono text-xs">{st.source_id}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export function AgentChatPage() {
  const { workspaceId = '' } = useParams<{ workspaceId: string }>()
  const {
    messages,
    lastResponse,
    sendMessage,
    retryMessage,
    clearMessages,
    isLoading,
    includeEvidence,
    setIncludeEvidence,
    includeSourceTrace,
    setIncludeSourceTrace,
  } = useAgentChat(workspaceId)
  const [input, setInput] = useState('')
  const [copied, setCopied] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const text = input.trim()
    if (!text || isLoading) return
    setInput('')
    sendMessage(text)
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e as unknown as React.FormEvent)
    }
  }

  const handleCopyAnswer = () => {
    if (!lastResponse?.answer) return
    navigator.clipboard.writeText(lastResponse.answer).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  const lastAssistantIdx = messages.map((m) => m.role).lastIndexOf('assistant')

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-white flex-shrink-0">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-blue-600 flex items-center justify-center">
            <Bot className="w-4.5 h-4.5 text-white" />
          </div>
          <div>
            <h1 className="text-sm font-semibold text-slate-900 leading-tight">Tax Audit AI</h1>
            <p className="text-xs text-slate-400">Powered by evidence from your documents</p>
          </div>
        </div>
        <div className="flex items-center gap-1.5">
          {lastResponse?.answer && (
            <button
              onClick={handleCopyAnswer}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-green-600" /> : <Copy className="w-3.5 h-3.5" />}
              {copied ? 'Copied!' : 'Copy answer'}
            </button>
          )}
          {messages.length > 0 && (
            <button
              onClick={clearMessages}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-slate-500 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer"
              title="Clear conversation"
            >
              <Trash2 className="w-3.5 h-3.5" />
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4 bg-[#F8FAFC]">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 rounded-2xl bg-blue-600 flex items-center justify-center mb-4 shadow-lg">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-lg font-semibold text-slate-900 mb-1.5">Tax Audit AI</h2>
            <p className="text-sm text-slate-500 mb-6 max-w-sm leading-relaxed">
              Ask questions about TDS compliance, risk findings, or your indexed documents.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-lg">
              {SUGGESTED_QUESTIONS.map((q) => (
                <button
                  key={q}
                  onClick={() => sendMessage(q)}
                  className="text-left px-3 py-2.5 text-xs text-blue-700 bg-white border border-blue-100 rounded-xl hover:bg-blue-50 hover:border-blue-200 hover:shadow-card transition-all cursor-pointer leading-relaxed"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        <AnimatePresence initial={false}>
          {messages.map((message, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={chatMessageTransition}
              className={cn(
                'flex gap-3',
                message.role === 'user' ? 'justify-end' : 'justify-start',
              )}
            >
              {message.role === 'assistant' && (
                <div className="flex-shrink-0 w-7 h-7 rounded-xl bg-blue-600 flex items-center justify-center mt-0.5 shadow-sm">
                  <Bot className="w-4 h-4 text-white" />
                </div>
              )}
              <div
                className={cn(
                  'max-w-[80%] rounded-2xl px-4 py-3 text-sm',
                  message.role === 'user'
                    ? 'bg-blue-600 text-white rounded-tr-sm shadow-sm'
                  : message._error
                    ? 'bg-red-50 border border-red-200 text-red-800 shadow-card rounded-tl-sm'
                    : 'bg-white border border-slate-200 text-slate-800 shadow-card rounded-tl-sm',
                )}
              >
                {message._error && (
                  <div className="flex items-center gap-1.5 mb-1.5 text-red-600 font-medium text-xs">
                    <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
                    Error
                  </div>
                )}
                {message.role === 'assistant' && !message._error ? (
                  <div className="prose prose-sm prose-slate max-w-none leading-relaxed [&_table]:text-xs [&_td]:py-1 [&_th]:py-1">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
                  </div>
                ) : (
                  <p className="leading-relaxed whitespace-pre-wrap">{message.content}</p>
                )}
                {message._error && message._retryContent && (
                  <button
                    onClick={() => retryMessage(message._retryContent!)}
                    disabled={isLoading}
                    className="flex items-center gap-1.5 mt-2 px-2.5 py-1 text-xs font-medium text-red-700 bg-red-100 hover:bg-red-200 rounded-lg transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <RotateCcw className="w-3 h-3" />
                    Retry
                  </button>
                )}
                {message.role === 'assistant' && !message._error && idx === lastAssistantIdx && lastResponse && (
                  <ResponseDetailsPanel response={lastResponse} />
                )}
              </div>
              {message.role === 'user' && (
                <div className="flex-shrink-0 w-7 h-7 rounded-xl bg-slate-200 flex items-center justify-center mt-0.5">
                  <User className="w-4 h-4 text-slate-600" />
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.18 }}
            className="flex gap-3 justify-start"
          >
            <div className="flex-shrink-0 w-7 h-7 rounded-xl bg-blue-600 flex items-center justify-center shadow-sm">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-sm px-4 py-3 shadow-card">
              <div className="flex items-center gap-2 text-sm text-slate-500">
                <LoadingSpinner className="w-3.5 h-3.5 border-slate-300 border-t-blue-600" />
                <span>Thinking…</span>
                <span className="flex gap-0.5">
                  <span className="w-1 h-1 rounded-full bg-slate-400 motion-safe:animate-pulse-dot" style={{ animationDelay: '0ms' }} />
                  <span className="w-1 h-1 rounded-full bg-slate-400 motion-safe:animate-pulse-dot" style={{ animationDelay: '200ms' }} />
                  <span className="w-1 h-1 rounded-full bg-slate-400 motion-safe:animate-pulse-dot" style={{ animationDelay: '400ms' }} />
                </span>
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Footer */}
      <div className="flex-shrink-0 border-t border-slate-200 bg-white px-6 py-3">
        <div className="flex items-center gap-4 mb-2 text-xs">
          <label className="flex items-center gap-1.5 text-slate-500 cursor-pointer select-none hover:text-slate-700 transition-colors">
            <input
              type="checkbox"
              checked={includeEvidence}
              onChange={(e) => setIncludeEvidence(e.target.checked)}
              className="w-3.5 h-3.5 rounded border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
            />
            Include evidence
          </label>
          <label className="flex items-center gap-1.5 text-slate-500 cursor-pointer select-none hover:text-slate-700 transition-colors">
            <input
              type="checkbox"
              checked={includeSourceTrace}
              onChange={(e) => setIncludeSourceTrace(e.target.checked)}
              className="w-3.5 h-3.5 rounded border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
            />
            Include source trace
          </label>
        </div>
        <form onSubmit={handleSubmit} className="flex gap-2 items-end">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about your documents…"
            rows={1}
            className="flex-1 resize-none px-4 py-2.5 text-sm border border-slate-300 rounded-xl placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors min-h-[42px] max-h-32 overflow-y-auto"
            style={{ height: 'auto' }}
            onInput={(e) => {
              const el = e.currentTarget
              el.style.height = 'auto'
              el.style.height = `${el.scrollHeight}px`
            }}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className={cn(
              'flex-shrink-0 p-2.5 rounded-xl transition-all cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 active:scale-95',
              input.trim() && !isLoading
                ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-sm'
                : 'bg-slate-100 text-slate-400 cursor-not-allowed',
            )}
            aria-label="Send message"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  )
}
