"use client"

import { useState } from "react"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { EntryUpdateForm } from "./EntryUpdateForm"

type Props = {
  entryId: string
  onSuccess?: () => void
}

export function UpdateEntryDialog({ entryId, onSuccess }: Props) {
  const [open, setOpen] = useState(false)

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          Edit
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit Ledger Entry</DialogTitle>
        </DialogHeader>
        <EntryUpdateForm 
            entryId={entryId} 
            onClose={() => setOpen(false)}
            onSuccess={onSuccess}
        />
      </DialogContent>
    </Dialog>
  )
}
