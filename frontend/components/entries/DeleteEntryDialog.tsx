"use client"

import { useState } from "react"
import {
  AlertDialog,
  AlertDialogTrigger,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogFooter,
  AlertDialogCancel,
  AlertDialogAction,
  AlertDialogDescription,
} from "@/components/ui/alert-dialog"
import { Button } from "@/components/ui/button"
import { toast } from "sonner"
import { Trash2Icon } from "lucide-react"

type Props = {
  entryId: string
  onSuccess?: () => void
}

export function DeleteEntryDialog({ entryId, onSuccess }: Props) {
  const [loading, setLoading] = useState(false)

  const handleDelete = async () => {
    setLoading(true)
    try {
      const res = await fetch(`http://localhost:8000/api/entries/${entryId}`, {
        method: "DELETE",
      })
      if (!res.ok) {
        const error = await res.text()
        throw new Error(error || "Delete failed")
      }

      toast.success("Entry Deleted", {
        description: "The ledger entry was removed successfully.",
      })

      if (onSuccess) onSuccess()
    } catch (err) {
      toast.error("Delete Failed", {
        description: (err as Error).message,
      })
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button variant="default" size="sm" className="hover:bg-destructive/90">
          <Trash2Icon className="w-4 h-4 mr-1" />
          Delete
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Are you sure?</AlertDialogTitle>
          <AlertDialogDescription>
            This action will delete this ledger entry.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={loading}>Cancel</AlertDialogCancel>
          <AlertDialogAction
            className="hover:bg-destructive/90"
            onClick={handleDelete}
            disabled={loading}
          >
            {loading ? "Deleting..." : "Delete Entry"}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
