// src/app/entries/page.tsx

import { EntryTable } from "@/components/entries/EntryTable"
import { CreateEntryDialog } from "@/components/entries/CreateEntryDialog"

export default function EntriesPage() {
  return (
    <div className="p-6 space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Ledger Entries</h1>
        <CreateEntryDialog />
      </div>
      <EntryTable />
    </div>
  )
}
