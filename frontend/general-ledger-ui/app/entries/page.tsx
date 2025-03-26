// src/app/entries/page.tsx

"use client"

import { useEffect, useState } from "react"
import { EntryTable } from "@/components/entries/EntryTable"
import { CreateEntryDialog } from "@/components/entries/CreateEntryDialog"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"

export default function EntriesPage() {
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(true)

  const fetchEntries = async () => {
    try {
      setLoading(true)
      const res = await fetch("http://localhost:8000/api/entries")
      const data = await res.json()
      setEntries(data.entries)
    } catch (error) {
      console.error("Failed to fetch entries", error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchEntries()
  }, [])

  return (
    <div className="p-6 space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Ledger Entries</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={fetchEntries}>
            Refresh
          </Button>
          <CreateEntryDialog onSuccess={fetchEntries} />
        </div>
      </div>
      {loading ? (
        <Skeleton className="h-64 w-full rounded-md" />
      ) : (
        <EntryTable entries={entries} onRefresh={fetchEntries} />
      )}
    </div>
  )
}
