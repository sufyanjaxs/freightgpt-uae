'use client'

import { useAuthStore } from '@/store/auth'
import { useTheme } from 'next-themes'
import { useEffect, useState } from 'react'
import { User, Bell, Shield, Palette, Globe } from 'lucide-react'

export default function SettingsPage() {
  const { user } = useAuthStore()
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)
  useEffect(() => setMounted(true), [])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Settings</h2>
        <p className="text-gray-500 dark:text-gray-400">Manage your account and preferences</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border bg-white dark:bg-gray-900">
          <div className="p-4 border-b flex items-center gap-3">
            <User className="h-5 w-5 text-primary-600" />
            <h3 className="font-semibold">Profile</h3>
          </div>
          <div className="p-4 space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Full Name</label>
              <input className="input-field" value={user?.full_name || ''} readOnly />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Email</label>
              <input className="input-field" value={user?.email || ''} readOnly />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Role</label>
              <input className="input-field" value={user?.role || ''} readOnly />
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="rounded-xl border bg-white dark:bg-gray-900">
            <div className="p-4 border-b flex items-center gap-3">
              <Palette className="h-5 w-5 text-purple-600" />
              <h3 className="font-semibold">Appearance</h3>
            </div>
            <div className="p-4 space-y-3">
              {mounted && (
                <div className="flex gap-3">
                  <button
                    onClick={() => setTheme('light')}
                    className={`flex-1 p-3 rounded-lg border text-center ${theme === 'light' ? 'border-primary-500 bg-primary-50 dark:bg-primary-950' : 'border-gray-200 dark:border-gray-700'}`}
                  >☀️ Light</button>
                  <button
                    onClick={() => setTheme('dark')}
                    className={`flex-1 p-3 rounded-lg border text-center ${theme === 'dark' ? 'border-primary-500 bg-primary-50 dark:bg-primary-950' : 'border-gray-200 dark:border-gray-700'}`}
                  >🌙 Dark</button>
                  <button
                    onClick={() => setTheme('system')}
                    className={`flex-1 p-3 rounded-lg border text-center ${theme === 'system' ? 'border-primary-500 bg-primary-50 dark:bg-primary-950' : 'border-gray-200 dark:border-gray-700'}`}
                  >💻 System</button>
                </div>
              )}
            </div>
          </div>

          <div className="rounded-xl border bg-white dark:bg-gray-900">
            <div className="p-4 border-b flex items-center gap-3">
              <Globe className="h-5 w-5 text-green-600" />
              <h3 className="font-semibold">Language</h3>
            </div>
            <div className="p-4">
              <select className="input-field w-full">
                <option value="en">English</option>
                <option value="ar">العربية</option>
                <option value="ur">اردو</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
