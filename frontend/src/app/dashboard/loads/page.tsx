'use client'

import { useQuery } from '@tanstack/react-query'
import { loads } from '@/lib/api'
import { formatCurrency, formatDate, getStatusColor } from '@/lib/utils'
import { Plus, Search } from 'lucide-react'

export default function LoadsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['loads'],
    queryFn: () => loads.list().then(r => r.data),
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Loads</h2>
          <p className="text-gray-500 dark:text-gray-400">Manage and track all freight loads</p>
        </div>
        <button className="btn-primary gap-2">
          <Plus className="h-4 w-4" />
          New Load
        </button>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input className="input-field pl-10" placeholder="Search loads..." />
        </div>
        <select className="input-field w-40">
          <option value="">All Status</option>
          <option value="pending">Pending</option>
          <option value="in_transit">In Transit</option>
          <option value="delivered">Delivered</option>
        </select>
      </div>

      <div className="rounded-xl border bg-white dark:bg-gray-900">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-gray-50 dark:bg-gray-800">
                <th className="px-4 py-3 text-left font-medium">Route</th>
                <th className="px-4 py-3 text-left font-medium">Pickup</th>
                <th className="px-4 py-3 text-left font-medium">Weight</th>
                <th className="px-4 py-3 text-left font-medium">Rate</th>
                <th className="px-4 py-3 text-left font-medium">Status</th>
                <th className="px-4 py-3 text-left font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {data?.items?.map((load: any) => (
                <tr key={load.id} className="border-b hover:bg-gray-50 dark:hover:bg-gray-800">
                  <td className="px-4 py-3">
                    <p className="font-medium">{load.origin_city} → {load.destination_city}</p>
                  </td>
                  <td className="px-4 py-3 text-gray-500">{formatDate(load.pickup_date)}</td>
                  <td className="px-4 py-3">{load.weight_kg ? `${load.weight_kg} kg` : '-'}</td>
                  <td className="px-4 py-3 font-medium">{load.shipper_rate ? formatCurrency(load.shipper_rate) : '-'}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${getStatusColor(load.status)}`}>
                      {load.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <button className="text-primary-600 hover:text-primary-700 text-sm font-medium">View</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
