'use client'

import { useQuery } from '@tanstack/react-query'
import { analytics } from '@/lib/api'
import { formatCurrency } from '@/lib/utils'
import { BarChart3, TrendingUp, DollarSign, Truck } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts'

export default function AnalyticsPage() {
  const { data: dashboard } = useQuery({
    queryKey: ['analytics-dashboard'],
    queryFn: () => analytics.dashboard().then(r => r.data),
  })

  const { data: revenueData } = useQuery({
    queryKey: ['analytics-revenue'],
    queryFn: () => analytics.revenueTimeline(30).then(r => r.data),
  })

  const { data: loadsData } = useQuery({
    queryKey: ['analytics-loads'],
    queryFn: () => analytics.loadsTimeline(30).then(r => r.data),
  })

  const { data: fleetStatus } = useQuery({
    queryKey: ['analytics-fleet'],
    queryFn: () => analytics.fleetStatus().then(r => r.data),
  })

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Analytics</h2>
        <p className="text-gray-500 dark:text-gray-400">Comprehensive business intelligence</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <DollarSign className="h-5 w-5 text-green-600" />
            <span className="text-sm font-medium">Revenue (30d)</span>
          </div>
          <p className="mt-2 text-2xl font-bold">{formatCurrency(dashboard?.revenue_last_30_days || 0)}</p>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <TrendingUp className="h-5 w-5 text-blue-600" />
            <span className="text-sm font-medium">Utilization</span>
          </div>
          <p className="mt-2 text-2xl font-bold">{dashboard?.fleet_utilization || 0}%</p>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <Truck className="h-5 w-5 text-purple-600" />
            <span className="text-sm font-medium">Active Loads</span>
          </div>
          <p className="mt-2 text-2xl font-bold">{dashboard?.active_loads || 0}</p>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <BarChart3 className="h-5 w-5 text-orange-600" />
            <span className="text-sm font-medium">Total Loads</span>
          </div>
          <p className="mt-2 text-2xl font-bold">{dashboard?.total_loads || 0}</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="stat-card">
          <h3 className="font-semibold mb-4">Revenue Trend (30 days)</h3>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={revenueData || []}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
                <XAxis dataKey="date" className="text-xs" />
                <YAxis className="text-xs" />
                <Tooltip />
                <Line type="monotone" dataKey="revenue" stroke="#22c55e" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="stat-card">
          <h3 className="font-semibold mb-4">Loads Timeline</h3>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={loadsData || []}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
                <XAxis dataKey="date" className="text-xs" />
                <YAxis className="text-xs" />
                <Tooltip />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {fleetStatus && Object.entries(fleetStatus).map(([status, count]) => (
          <div key={status} className="stat-card">
            <p className="text-sm font-medium text-gray-500 capitalize">{status.replace(/_/g, ' ')}</p>
            <p className="mt-2 text-3xl font-bold">{count as number}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
