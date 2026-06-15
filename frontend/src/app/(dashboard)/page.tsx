'use client'

import { useQuery } from '@tanstack/react-query'
import { analytics } from '@/lib/api'
import { formatCurrency } from '@/lib/utils'
import { Package, Truck, TrendingUp, DollarSign } from 'lucide-react'
import dynamic from 'next/dynamic'

const Chart = dynamic(() => import('recharts').then((mod) => mod.LineChart), { ssr: false })
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts'

const statCards = [
  { label: 'Active Loads', key: 'active_loads', icon: Package, color: 'text-blue-600', bg: 'bg-blue-50 dark:bg-blue-950' },
  { label: 'Available Trucks', key: 'available_trucks', icon: Truck, color: 'text-green-600', bg: 'bg-green-50 dark:bg-green-950' },
  { label: 'Fleet Utilization', key: 'fleet_utilization', icon: TrendingUp, color: 'text-purple-600', bg: 'bg-purple-50 dark:bg-purple-950', suffix: '%' },
  { label: 'Revenue (30d)', key: 'revenue_last_30_days', icon: DollarSign, color: 'text-primary-600', bg: 'bg-primary-50 dark:bg-primary-950', prefix: true },
]

export default function DashboardPage() {
  const { data: dashboard } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => analytics.dashboard().then(r => r.data),
    refetchInterval: 30000,
  })

  const { data: revenueData } = useQuery({
    queryKey: ['revenue-timeline'],
    queryFn: () => analytics.revenueTimeline(7).then(r => r.data),
  })

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Dashboard</h2>
        <p className="text-gray-500 dark:text-gray-400">Real-time overview of your logistics operations</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat) => {
          const value = dashboard?.[stat.key]
          const displayValue = stat.prefix
            ? formatCurrency(value || 0)
            : (value ?? '-') + (stat.suffix || '')

          return (
            <div key={stat.key} className="stat-card">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{stat.label}</p>
                <div className={`rounded-lg p-2 ${stat.bg}`}>
                  <stat.icon className={`h-5 w-5 ${stat.color}`} />
                </div>
              </div>
              <p className="mt-3 text-2xl font-bold">{displayValue}</p>
            </div>
          )
        })}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="stat-card">
          <h3 className="font-semibold mb-4">Revenue Trend</h3>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={revenueData || []}>
                <defs>
                  <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
                <XAxis dataKey="date" className="text-xs" />
                <YAxis className="text-xs" />
                <Tooltip />
                <Area type="monotone" dataKey="revenue" stroke="#3b82f6" fill="url(#revenueGradient)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="stat-card">
          <h3 className="font-semibold mb-4">Recent Activity</h3>
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="h-2 w-2 rounded-full bg-green-500" />
              <div className="flex-1">
                <p className="text-sm font-medium">Load #1234 delivered</p>
                <p className="text-xs text-gray-500">Dubai to Abu Dhabi</p>
              </div>
              <span className="text-xs text-gray-400">2m ago</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="h-2 w-2 rounded-full bg-blue-500" />
              <div className="flex-1">
                <p className="text-sm font-medium">New bid placed</p>
                <p className="text-xs text-gray-500">Load #5678 - Riyadh</p>
              </div>
              <span className="text-xs text-gray-400">15m ago</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="h-2 w-2 rounded-full bg-yellow-500" />
              <div className="flex-1">
                <p className="text-sm font-medium">Truck #042 in maintenance</p>
                <p className="text-xs text-gray-500">Scheduled service</p>
              </div>
              <span className="text-xs text-gray-400">1h ago</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
