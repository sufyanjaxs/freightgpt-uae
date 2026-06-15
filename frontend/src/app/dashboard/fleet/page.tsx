'use client'

import { useQuery } from '@tanstack/react-query'
import { fleet } from '@/lib/api'
import { getStatusColor } from '@/lib/utils'
import { Truck, Users, Wrench } from 'lucide-react'

export default function FleetPage() {
  const { data: trucks } = useQuery({
    queryKey: ['trucks'],
    queryFn: () => fleet.trucks.list().then(r => r.data),
  })

  const { data: drivers } = useQuery({
    queryKey: ['drivers'],
    queryFn: () => fleet.drivers.list().then(r => r.data),
  })

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Fleet Management</h2>
        <p className="text-gray-500 dark:text-gray-400">Manage trucks, drivers, and maintenance</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <Truck className="h-5 w-5 text-blue-600" />
            <span className="text-sm font-medium">Total Trucks</span>
          </div>
          <p className="mt-2 text-2xl font-bold">{trucks?.length || 0}</p>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <Users className="h-5 w-5 text-green-600" />
            <span className="text-sm font-medium">Active Drivers</span>
          </div>
          <p className="mt-2 text-2xl font-bold">{drivers?.length || 0}</p>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <Wrench className="h-5 w-5 text-orange-600" />
            <span className="text-sm font-medium">In Maintenance</span>
          </div>
          <p className="mt-2 text-2xl font-bold">
            {trucks?.filter((t: any) => t.status === 'maintenance').length || 0}
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border bg-white dark:bg-gray-900">
          <div className="p-4 border-b">
            <h3 className="font-semibold">Trucks</h3>
          </div>
          <div className="divide-y">
            {trucks?.map((truck: any) => (
              <div key={truck.id} className="p-4 flex items-center justify-between">
                <div>
                  <p className="font-medium">{truck.plate_number}</p>
                  <p className="text-sm text-gray-500">{truck.truck_type} • {truck.make} {truck.model}</p>
                </div>
                <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${getStatusColor(truck.status)}`}>
                  {truck.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-xl border bg-white dark:bg-gray-900">
          <div className="p-4 border-b">
            <h3 className="font-semibold">Drivers</h3>
          </div>
          <div className="divide-y">
            {drivers?.map((driver: any) => (
              <div key={driver.id} className="p-4 flex items-center justify-between">
                <div>
                  <p className="font-medium">{driver.full_name}</p>
                  <p className="text-sm text-gray-500">{driver.nationality} • ⭐ {driver.rating}</p>
                </div>
                <span className="text-sm text-gray-500">{driver.total_trips} trips</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
