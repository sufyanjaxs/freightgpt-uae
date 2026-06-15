'use client'

import { useAuthStore } from '@/store/auth'
import { useTheme } from 'next-themes'
import { Moon, Sun, Bell, User } from 'lucide-react'
import { useEffect, useState } from 'react'

export function Header() {
  const { user } = useAuthStore()
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => setMounted(true), [])

  return (
    <header className="flex h-14 items-center justify-between border-b bg-white dark:bg-gray-950 px-6">
      <div>
        <h1 className="text-lg font-semibold">Welcome, {user?.full_name || 'User'}</h1>
      </div>

      <div className="flex items-center gap-3">
        <button className="relative p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
          <Bell className="h-5 w-5 text-gray-500" />
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-red-500" />
        </button>

        {mounted && (
          <button
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </button>
        )}

        <div className="flex items-center gap-2 pl-3 border-l">
          <div className="h-8 w-8 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
            <User className="h-4 w-4 text-primary-600" />
          </div>
          <div className="text-sm">
            <p className="font-medium">{user?.full_name}</p>
            <p className="text-xs text-gray-500">{user?.role}</p>
          </div>
        </div>
      </div>
    </header>
  )
}
