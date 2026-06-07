import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import axios from 'axios'
import toast from 'react-hot-toast'
import { agentChatApi } from '../lib/api/agentChat'
import type { AgentMessage, AgentChatResponse } from '../types/agent'
import { extractErrorMessage } from '../lib/utils'

export function useAgentChat(workspaceId: string) {
  const [messages, setMessages] = useState<AgentMessage[]>([])
  const [lastResponse, setLastResponse] = useState<AgentChatResponse | null>(null)
  const [includeEvidence, setIncludeEvidence] = useState(false)
  const [includeSourceTrace, setIncludeSourceTrace] = useState(false)

  const mutation = useMutation({
    mutationFn: (userMessage: string) =>
      agentChatApi.chat(workspaceId, {
        message: userMessage,
        include_evidence: includeEvidence,
        include_source_trace: includeSourceTrace,
        max_evidence: 5,
      }),
    onSuccess: (response) => {
      setLastResponse(response)
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: response.answer },
      ])
    },
    onError: (err, userMessage) => {
      const status = axios.isAxiosError(err) ? err.response?.status : undefined

      // 401 is handled globally by the API client (redirect to login)
      if (status === 401) return

      const inlineMessage =
        status === 403
          ? 'You do not have permission to use the agent for this workspace.'
          : 'The agent could not answer right now. Please try again.'

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: inlineMessage,
          _error: true,
          // Only offer retry for non-permission errors
          ...(status !== 403 && { _retryContent: userMessage }),
        },
      ])
      toast.error(extractErrorMessage(err))
    },
  })

  const sendMessage = (content: string) => {
    const userMsg: AgentMessage = { role: 'user', content }
    setMessages((prev) => [...prev, userMsg])
    mutation.mutate(content)
  }

  const retryMessage = (content: string) => {
    // Remove the last error message before retrying
    setMessages((prev) => {
      const lastIdx = [...prev].reverse().findIndex((m) => m._error)
      if (lastIdx === -1) return prev
      const idx = prev.length - 1 - lastIdx
      return prev.filter((_, i) => i !== idx)
    })
    mutation.mutate(content)
  }

  const clearMessages = () => {
    setMessages([])
    setLastResponse(null)
  }

  return {
    messages,
    lastResponse,
    sendMessage,
    retryMessage,
    clearMessages,
    isLoading: mutation.isPending,
    error: mutation.error,
    includeEvidence,
    setIncludeEvidence,
    includeSourceTrace,
    setIncludeSourceTrace,
  }
}
