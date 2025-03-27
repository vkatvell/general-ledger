"use client"

import { useState, useEffect } from "react"
import { format, parseISO } from "date-fns"
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { CalendarIcon, EyeIcon } from "lucide-react"

type Entry = {
  id: string
  amount: string
  currency: string
  date: string
  description?: string
  entry_type: string
  account_name: string
  version: number
}

type Props = {
  entryId: string
}

export function ViewEntryDialog({ entryId }: Props) {
  const [open, setOpen] = useState(false)
  const [entry, setEntry] = useState<Entry | null>(null)

  useEffect(() => {
    if (!open) return
    const fetchEntry = async () => {
      const res = await fetch(`http://localhost:8000/api/entries/${entryId}`)
      const data = await res.json()
      setEntry(data)
    }
    fetchEntry().catch(console.error)
  }, [open, entryId])

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="secondary" size="sm" className="text-muted-foreground">
          <EyeIcon className="w-4 h-4 mr-1" />
          View
        </Button>
      </DialogTrigger>

      <DialogContent>
        <DialogHeader>
          <DialogTitle>Ledger Entry Details</DialogTitle>
        </DialogHeader>

        {!entry ? (
          <p className="text-sm text-muted-foreground">Loading...</p>
        ) : (
          <div className="space-y-6">

            {/* Row 1: Account + Type */}
            <div className="flex gap-4">
              <div className="flex-1">
                <label className="text-sm block mb-1">Account</label>
                <Input readOnly value={entry.account_name} className="bg-muted" />
              </div>
              <div className="flex-1">
                <label className="text-sm block mb-1">Entry Type</label>
                <Input readOnly value={entry.entry_type.toUpperCase()} className="bg-muted" />
              </div>
            </div>

            {/* Row 2: Amount + Currency */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm block mb-1">Amount</label>
                <Input
                  readOnly
                  value={`${Number(entry.amount).toFixed(2)}`}
                  className="bg-muted"
                />
              </div>
              <div>
                <label className="text-sm block mb-1">Currency</label>
                <Input readOnly disabled value={entry.currency} className="bg-muted" />
              </div>
            </div>

            {/* Row 3: Date */}
            <div>
              <label className="text-sm block mb-1">Date</label>
              <Button
                aria-readonly
                variant="outline"
                className="w-full justify-start text-left bg-muted"
              >
                <CalendarIcon className="mr-2 h-4 w-4" />
                {format(parseISO(entry.date), "MMMM do, yyyy")}
              </Button>
            </div>

            {/* Row 4: Description */}
            <div>
              <label className="text-sm block mb-1">Description</label>
              <Textarea
                readOnly
                value={entry.description}
                className="bg-muted"
              />
            </div>

            {/* Version + ID */}
            <div className="grid grid-cols-1 gap-4 text-sm">
              <div>
                <span className="font-medium">ID:</span> {entry.id}
              </div>
              <div>
                <span className="font-medium">Version:</span> {entry.version}
              </div>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
