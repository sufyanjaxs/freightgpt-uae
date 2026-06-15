'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/auth'
import DashboardPage from './(dashboard)/page'

export default function Home() {
  const { isAuthenticated, isLoading, loadUser } = useAuthStore()
  const router = useRouter()

  useEffect(() => {
    loadUser()
  }, [loadUser])

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
      </div>
    )
  }

  if (!isAuthenticated) {
    router.push('/auth/login')
    return null
  }

  return <DashboardPage />
}
