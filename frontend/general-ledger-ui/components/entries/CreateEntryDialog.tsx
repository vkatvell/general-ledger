"use client"

import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { EntryForm } from "@/components/entries/EntryForm"

export function CreateEntryDialog() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="default">Create Entry</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>New Ledger Entry</DialogTitle>
        </DialogHeader>
        <EntryForm />
      </DialogContent>
    </Dialog>
  )
}
