"use client"

import { useState } from "react"
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { toast } from "sonner"

type Props = {
  onSuccess: () => void
}

export function CreateAccountDialog({ onSuccess }: Props) {
  const [open, setOpen] = useState(false)
  const [name, setName] = useState("")
  const [submitting, setSubmitting] = useState(false)

  const handleCreate = async () => {
    if (!name.trim()) {
      toast.error("Account name is required")
      return
    }

    setSubmitting(true)
    try {
        const response = await fetch("http://localhost:8000/api/accounts", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name }),
        })

        const resData = await response.json()

        if (!response.ok) {
          toast.info("Unable to Create Account", {
            description: resData.detail || "Something went wrong.",
          })
          return
        }
    
        toast.success("Account Created", {
          description: "Your new account was added successfully.",
        })
        setName("")
        setOpen(false)
        onSuccess()
    } catch (err) {
        toast.error("Unable to Create Account", {
            description: (err as Error).message,
        })
    } finally {
        setSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="default">Create Account</Button>
      </DialogTrigger>

      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>New Account</DialogTitle>
          <DialogDescription>
            Create a new ledger account by entering a name below.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-2 items-center gap-4">
            <Label htmlFor="name" className="text-right">
              Account Name
            </Label>
            <Input
              id="name"
              placeholder="e.g. Cash"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="col-span-3"
            />
          </div>
        </div>

        <DialogFooter>
          <Button type="submit" onClick={handleCreate} disabled={submitting}>
            {submitting ? "Creating..." : "Create Account"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
