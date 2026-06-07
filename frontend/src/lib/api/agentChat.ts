import { post } from './client'
import type { AgentChatRequest, AgentChatResponse } from '../../types/agent'

export const agentChatApi = {
  chat: (workspaceId: string, data: AgentChatRequest): Promise<AgentChatResponse> =>
    post<AgentChatResponse>(`/workspaces/${workspaceId}/agent-chat`, data, { timeout: 120000 }),
}
