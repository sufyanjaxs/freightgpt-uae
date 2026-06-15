'use client'

import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { agents } from '@/lib/api'
import { Bot, Play, Clock, CheckCircle, XCircle } from 'lucide-react'
import { toast } from 'sonner'

const agentList = [
  { id: 'market_intelligence', name: 'Market Intelligence', description: 'Monitor markets & analyze trends', icon: '📊' },
  { id: 'load_acquisition', name: 'Load Acquisition', description: 'Automatically acquire freight', icon: '🎯' },
  { id: 'shipper_acquisition', name: 'Shipper Acquisition', description: 'Find and onboard shippers', icon: '👥' },
  { id: 'sales', name: 'AI Sales Agent', description: 'Handle calls, email & WhatsApp', icon: '💬' },
  { id: 'dispatch', name: 'Dispatch Agent', description: 'Assign trucks & plan routes', icon: '🚛' },
  { id: 'driver_copilot', name: 'Driver AI Copilot', description: 'Assist drivers on the road', icon: '🧭' },
  { id: 'pricing', name: 'Pricing AI', description: 'Calculate optimal rates', icon: '💰' },
  { id: 'document_ai', name: 'Document AI', description: 'Process PODs, BOLs & invoices', icon: '📄' },
  { id: 'finance', name: 'Finance Agent', description: 'Handle invoices & collections', icon: '🏦' },
  { id: 'ceo', name: 'CEO Agent', description: 'Executive reports & analytics', icon: '👔' },
]

export default function AgentsPage() {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)
  const [input, setInput] = useState('')

  const { data: runs } = useQuery({
    queryKey: ['agent-runs'],
    queryFn: () => agents.runs(10).then(r => r.data),
    refetchInterval: 10000,
  })

  const runMutation = useMutation({
    mutationFn: (data: { agent_type: string; input_data: any }) => agents.run(data.agent_type, data.input_data),
    onSuccess: () => {
      toast.success('Agent task completed')
    },
    onError: () => {
      toast.error('Agent task failed')
    },
  })

  const handleRunAgent = (agentId: string) => {
    runMutation.mutate({
      agent_type: agentId,
      input_data: { action: 'analyze_market', query: input || 'Provide market overview' },
    })
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">AI Agents</h2>
        <p className="text-gray-500 dark:text-gray-400">Run and monitor autonomous AI agents</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {agentList.map((agent) => (
          <div
            key={agent.id}
            className="rounded-xl border bg-white dark:bg-gray-900 p-4 hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => setSelectedAgent(agent.id)}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{agent.icon}</span>
                <div>
                  <h3 className="font-semibold">{agent.name}</h3>
                  <p className="text-xs text-gray-500">{agent.description}</p>
                </div>
              </div>
            </div>
            <button
              className="btn-primary w-full mt-4 gap-2"
              onClick={(e) => { e.stopPropagation(); handleRunAgent(agent.id) }}
            >
              <Play className="h-4 w-4" />
              Run Agent
            </button>
          </div>
        ))}
      </div>

      <div className="rounded-xl border bg-white dark:bg-gray-900">
        <div className="p-4 border-b">
          <h3 className="font-semibold">Recent Runs</h3>
        </div>
        <div className="divide-y">
          {runs?.map((run: any) => (
            <div key={run.id} className="p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                {run.status === 'completed' ? (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                ) : run.status === 'failed' ? (
                  <XCircle className="h-5 w-5 text-red-500" />
                ) : (
                  <Clock className="h-5 w-5 text-yellow-500" />
                )}
                <div>
                  <p className="font-medium capitalize">{run.agent_type.replace(/_/g, ' ')}</p>
                  <p className="text-xs text-gray-500">
                    {run.duration_ms ? `${(run.duration_ms / 1000).toFixed(1)}s` : 'Running...'}
                    {run.model_used && ` • ${run.model_used}`}
                  </p>
                </div>
              </div>
              <span className={`text-xs font-medium ${run.status === 'completed' ? 'text-green-600' : run.status === 'failed' ? 'text-red-600' : 'text-yellow-600'}`}>
                {run.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
