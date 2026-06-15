'use client'

import { useQuery } from '@tanstack/react-query'
import { documents } from '@/lib/api'
import { FileText, Upload, Search } from 'lucide-react'
import { formatDate, getStatusColor } from '@/lib/utils'

export default function DocumentsPage() {
  const { data: docs, isLoading } = useQuery({
    queryKey: ['documents'],
    queryFn: () => documents.list().then(r => r.data),
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Documents</h2>
          <p className="text-gray-500 dark:text-gray-400">Upload and process logistics documents</p>
        </div>
        <button className="btn-primary gap-2">
          <Upload className="h-4 w-4" />
          Upload Document
        </button>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input className="input-field pl-10" placeholder="Search documents..." />
        </div>
        <select className="input-field w-40">
          <option value="">All Types</option>
          <option value="pod">POD</option>
          <option value="bol">BOL</option>
          <option value="invoice">Invoice</option>
        </select>
      </div>

      <div className="rounded-xl border bg-white dark:bg-gray-900">
        <div className="divide-y">
          {docs?.map((doc: any) => (
            <div key={doc.id} className="p-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-primary-50 dark:bg-primary-950">
                  <FileText className="h-5 w-5 text-primary-600" />
                </div>
                <div>
                  <p className="font-medium">{doc.original_filename}</p>
                  <p className="text-xs text-gray-500">
                    {doc.document_type.toUpperCase()} • {formatDate(doc.created_at)}
                    {doc.file_size_bytes && ` • ${(doc.file_size_bytes / 1024).toFixed(1)} KB`}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${getStatusColor(doc.status)}`}>
                  {doc.status}
                </span>
                <button className="text-primary-600 hover:text-primary-700 text-sm font-medium">View</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
