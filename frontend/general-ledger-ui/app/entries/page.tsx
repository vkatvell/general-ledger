// src/app/entries/page.tsx

import { EntryForm } from "@/components/entries/EntryForm"
import { EntryTable } from "@/components/entries/EntryTable"

export default function EntriesPage() {
  return (
    <div className="p-6 space-y-8">
      <h1 className="text-2xl font-bold">Ledger Entries</h1>
      <EntryForm />
      <EntryTable />
    </div>
  )
}
