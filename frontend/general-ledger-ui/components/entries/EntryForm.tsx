// src/components/entries/EntryForm.tsx

"use client"

import { z } from "zod"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useState } from "react"
import { v4 as uuidv4 } from "uuid"

const entrySchema = z.object({
  amount: z.number().positive("Amount must be greater than 0"),
  currency: z.string().length(3, "Currency must be a 3-letter code"),
  source_account: z.string().min(1, "Source account required"),
  destination_account: z.string().min(1, "Destination account required"),
  idempotency_key: z.string().uuid("Invalid UUID"),
})

type EntryFormData = z.infer<typeof entrySchema>

export function EntryForm() {
  const [submitting, setSubmitting] = useState(false)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<EntryFormData>({
    resolver: zodResolver(entrySchema),
    defaultValues: {
      idempotency_key: uuidv4(),
    },
  })

  const onSubmit = async (data: EntryFormData) => {
    setSubmitting(true)
    try {
      const response = await fetch("http://localhost:8000/api/entries", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      })
      if (!response.ok) {
        throw new Error("Failed to create entry")
      }
      reset({ ...data, amount: 0, idempotency_key: uuidv4() })
    } catch (err) {
      console.error(err)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <Label htmlFor="amount">Amount</Label>
        <Input
          type="number"
          step="0.01"
          {...register("amount", { valueAsNumber: true })}
        />
        {errors.amount && (
          <p className="text-sm text-red-500">{errors.amount.message}</p>
        )}
      </div>

      <div className="flex space-x-4">
        <div className="flex-1">
          <Label htmlFor="currency">Currency</Label>
          <Input {...register("currency")} placeholder="e.g., USD" />
          {errors.currency && (
            <p className="text-sm text-red-500">{errors.currency.message}</p>
          )}
        </div>
        <div className="flex-1">
          <Label htmlFor="idempotency_key">Idempotency Key</Label>
          <Input {...register("idempotency_key")} />
          {errors.idempotency_key && (
            <p className="text-sm text-red-500">
              {errors.idempotency_key.message}
            </p>
          )}
        </div>
      </div>

      <div className="flex space-x-4">
        <div className="flex-1">
          <Label htmlFor="source_account">Source Account</Label>
          <Input {...register("source_account")} />
          {errors.source_account && (
            <p className="text-sm text-red-500">
              {errors.source_account.message}
            </p>
          )}
        </div>
        <div className="flex-1">
          <Label htmlFor="destination_account">Destination Account</Label>
          <Input {...register("destination_account")} />
          {errors.destination_account && (
            <p className="text-sm text-red-500">
              {errors.destination_account.message}
            </p>
          )}
        </div>
      </div>

      <Button type="submit" disabled={submitting}>
        {submitting ? "Submitting..." : "Create Entry"}
      </Button>
    </form>
  )
}
