"use client"

import { useState } from "react"
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { EntryForm } from "@/components/entries/EntryForm"

type Props = {
    onSuccess?: () => void
  }

export function CreateEntryDialog({ onSuccess }: Props) {
    const [open, setOpen] = useState(false)
  
    return (
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTrigger asChild>
          <Button>Create Entry</Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>New Ledger Entry</DialogTitle>
          </DialogHeader>
          <EntryForm onClose={() => setOpen(false)} onSuccess={onSuccess} />
        </DialogContent>
      </Dialog>
    )
  }
