"use client"

import { useEffect, useState } from "react"
import { z } from "zod"
import { format, parseISO } from "date-fns"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"

import { toast } from "sonner"

import {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { CalendarIcon } from "lucide-react"
import { cn } from "@/lib/utils"

const updateSchema = z.object({
  amount: z.number().positive("Amount must be greater than 0"),
  description: z.string().optional(),
})

type UpdateFormData = z.infer<typeof updateSchema>

type Props = {
  entryId: string
  onClose: () => void
  onSuccess?: () => void
}

export function EntryUpdateForm({ entryId, onClose, onSuccess }: Props) {
  const [entryData, setEntryData] = useState<any>(null)
  const [submitting, setSubmitting] = useState(false)

  const form = useForm<UpdateFormData>({
    resolver: zodResolver(updateSchema),
  })

  useEffect(() => {
    const fetchEntry = async () => {
      const res = await fetch(`http://localhost:8000/api/entries/${entryId}`)
      const data = await res.json()
      setEntryData(data)

      form.reset({
        amount: parseFloat(data.amount),
        description: data.description ?? "",
      })
    }

    fetchEntry().catch(console.error)
  }, [entryId])

  const onSubmit = async (values: UpdateFormData) => {
    setSubmitting(true)
    try {
      const response = await fetch(`http://localhost:8000/api/entries/${entryId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values),
      })
  
      const data = await response.json()
  
      if (!response.ok) {
        toast.info("Unable to Update Entry", {
          description: data.detail || "Something went wrong.",
        })
        return
      }
  
      toast.success("Entry Updated", {
        description: "Your new ledger entry was updated successfully.",
      })
  
      onClose()
      if (onSuccess) onSuccess()
  
    } catch (err) {
      toast.error("Unable to Update Entry", {
        description: (err as Error).message,
      })
      console.error(err)
    } finally {
      setSubmitting(false)
    }
  }

  if (!entryData) return null

  const formattedDate = format(parseISO(entryData.date), "MMMM do, yyyy")

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        {/* Row: Account & Entry Type */}
        <div className="flex gap-4">
          <div className="flex-1">
            <FormLabel className = "mb-2 block">Account</FormLabel>
            <Input disabled value={entryData.account_name} className="bg-muted" />
          </div>
          <div className="flex-1">
            <FormLabel className = "mb-2 block">Entry Type</FormLabel>
            <Input disabled value={entryData.entry_type.toUpperCase()} className="bg-muted" />
          </div>
        </div>

        {/* Row: Amount + Currency */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField
  control={form.control}
  name="amount"
  render={({ field }) => {
    const [inputValue, setInputValue] = useState(field.value?.toString() ?? "")

    useEffect(() => {
      // Keep local input in sync if field value changes externally (e.g. form.reset)
      setInputValue(field.value?.toString() ?? "")
    }, [field.value])

    return (
      <FormItem>
        <FormLabel>Amount</FormLabel>
        <FormControl>
          <div className="relative">
            <span className="absolute left-3 top-2 text-sm text-muted-foreground">$</span>
            <Input
              type="text"
              className="pl-7"
              placeholder="0.00"
              inputMode="decimal"
              value={inputValue}
              onChange={(e) => {
                const val = e.target.value
                setInputValue(val)

                // Only update the form field if it's a valid number
                const parsed = parseFloat(val)
                if (!isNaN(parsed)) {
                  field.onChange(parsed)
                } else {
                  // Don't call onChange to avoid corrupting the state
                }
              }}
              onBlur={() => {
                // On blur, try to sync back whatever is valid
                const parsed = parseFloat(inputValue)
                if (!isNaN(parsed)) {
                  field.onChange(parsed)
                } else {
                  setInputValue(field.value?.toString() ?? "")
                }
              }}
            />
          </div>
        </FormControl>
        <FormMessage />
      </FormItem>
    )
  }}
/>

          <div>
            <FormLabel className = "mb-2 block">Currency</FormLabel>
            <Input disabled readOnly value="USD" className="bg-muted" />
          </div>
        </div>

        {/* Date */}
        <div>
          <FormLabel className = "mb-2 block">Date</FormLabel>
          <Button
            disabled
            variant="outline"
            className="w-full justify-start text-left bg-muted text-muted-foreground"
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            {formattedDate}
          </Button>
        </div>

        {/* Description */}
        <FormField
          control={form.control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Description</FormLabel>
              <FormControl>
                <Textarea {...field} placeholder="Optional description..." />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" disabled={submitting} className="w-full">
          {submitting ? "Updating..." : "Update Entry"}
        </Button>
      </form>
    </Form>
  )
}
