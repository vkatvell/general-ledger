"use client"

import { useState } from "react"
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { toast } from "sonner"

type Props = {
  accountId: string
  currentName: string
  isActive: boolean
  onSuccess?: () => void
}

export function UpdateAccountDialog({
  accountId,
  currentName,
  isActive,
  onSuccess,
}: Props) {
  const [open, setOpen] = useState(false)
  const [name, setName] = useState(currentName)
  const [submitting, setSubmitting] = useState(false)

  const handleUpdate = async () => {
    if (!name.trim()) {
      toast.error("Account name cannot be empty")
      return
    }

    setSubmitting(true)
    try {
      const response = await fetch(`http://localhost:8000/api/accounts/${accountId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
      })

      const data = await response.json()

      if (!response.ok) {
        toast.info("Unable to Update Account", {
          description: data.detail || "Something went wrong.",
        })
        return
      }

      toast.success("Account Updated", {
        description: "Account name updated successfully.",
      })

      setOpen(false)
      if (onSuccess) onSuccess()

    } catch (err) {
      toast.error("Update Failed", {
        description: (err as Error).message,
      })
      console.error(err)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          Edit
        </Button>
      </DialogTrigger>

      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Edit Account</DialogTitle>
          <DialogDescription>
            Update the name of the account. Active status cannot be changed here.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="name" className="text-right">Name</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="col-span-3"
            />
          </div>

          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="status" className="text-right">Active</Label>
            <Input
              id="status"
              disabled
              readOnly
              value={isActive ? "Yes" : "No"}
              className="col-span-3 bg-muted text-muted-foreground"
            />
          </div>
        </div>

        <DialogFooter>
          <Button type="submit" onClick={handleUpdate} disabled={submitting}>
            {submitting ? "Updating..." : "Update Account"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
