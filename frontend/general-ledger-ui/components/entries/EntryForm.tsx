"use client"

import { useEffect, useState } from "react"
import { z } from "zod"
import { format } from "date-fns"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { useFormState } from "react-dom"

import { toast } from "sonner"

import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Calendar } from "@/components/ui/calendar"
import {
  Popover,
  PopoverTrigger,
  PopoverContent,
} from "@/components/ui/popover"
import {
  Command,
  CommandInput,
  CommandItem,
  CommandEmpty,
  CommandList,
} from "@/components/ui/command"
import { CalendarIcon } from "lucide-react"
import { cn } from "@/lib/utils"
import { v4 as uuidv4 } from "uuid"
import { useRouter } from "next/navigation"

const entrySchema = z.object({
  account_name: z.string().min(1, "Account is required"),
  entry_type: z.enum(["debit", "credit"]),
  amount: z.number().positive("Amount must be greater than 0"),
  currency: z.literal("USD"),
  description: z.string().optional(),
  date: z.union([z.date(), z.string().datetime()]).optional(),
})

type EntryFormData = z.infer<typeof entrySchema>

type Props = {
  onClose: () => void
  onSuccess?: () => void
}

export function EntryForm({ onClose, onSuccess }: Props ){
  const [accounts, setAccounts] = useState<string[]>([])
  const [submitting, setSubmitting] = useState(false)
  const [selectedDate, setSelectedDate] = useState<Date | undefined>()
  const router = useRouter()

  const form = useForm<EntryFormData>({
    resolver: zodResolver(entrySchema),
    defaultValues: {
      currency: "USD",
    },
    mode: "onTouched",
    shouldUseNativeValidation: false,
  })

  useEffect(() => {
    const fetchAccounts = async () => {
      const res = await fetch("http://localhost:8000/api/accounts")
      const data = await res.json()
      setAccounts(data.accounts.map((a: { name: string }) => a.name))
    }

    fetchAccounts().catch(console.error)
  }, [])

  const onSubmit = async (data: EntryFormData) => {
    setSubmitting(true)
    try {
      const response = await fetch("http://localhost:8000/api/entries", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...data,
          currency: "USD",
          date: selectedDate?.toISOString(),
          idempotency_key: uuidv4(),
        }),
      })
      if (!response.ok) throw new Error("Failed to create entry")

      toast.success("Entry Created", {
          description: "Your new ledger entry was added successfully.",
      })

      form.reset()
      setSelectedDate(undefined)

      // Close dialog
      if (onClose) onClose()

      if (onSuccess) onSuccess()

      // Optionally refresh UI
      router.refresh()
    } catch (err) {
      toast.error("Unable to Create Entry", {
        description: (err as Error).message,
      })
      console.error(err)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        {/* Row: Account + Entry Type */}
        <div className="flex gap-4">
          <FormField
            control={form.control}
            name="account_name"
            render={({ field }) => (
              <FormItem className="flex-1">
                <FormLabel>Account</FormLabel>
                <Popover>
                  <PopoverTrigger asChild>
                    <FormControl>
                      <Button
                        variant="outline"
                        className={cn(
                          "w-full justify-start text-left",
                          !field.value
                        )}
                      >
                        {field.value || "Search accounts..."}
                      </Button>
                    </FormControl>
                  </PopoverTrigger>
                  <PopoverContent className="p-0 w-full" side="bottom">
                    <Command>
                      <CommandInput placeholder="Search accounts..." />
                      <CommandList>
                        <CommandEmpty>No account found</CommandEmpty>
                        {accounts.map((acc) => (
                          <CommandItem
                            key={acc}
                            value={acc}
                            onSelect={() => field.onChange(acc)}
                          >
                            {acc}
                          </CommandItem>
                        ))}
                      </CommandList>
                    </Command>
                  </PopoverContent>
                </Popover>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="entry_type"
            render={({ field }) => (
              <FormItem className="flex-1">
                <FormLabel>Entry Type</FormLabel>
                <FormControl>
                  <select
                    value={field.value || ""}
                    onChange={field.onChange}
                    className="w-full border rounded-md h-10 px-3 text-sm"
                  >
                    <option value="" disabled>
                      Select type
                    </option>
                    <option value="debit">Debit</option>
                    <option value="credit">Credit</option>
                  </select>
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        {/* Row: Amount + Currency */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="amount"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Amount</FormLabel>
                <FormControl>
                  <div className="relative">
                    <span className="absolute left-3 top-2 text-sm text-muted-foreground">$</span>
                    <Input
                      {...field}
                      type="number"
                      step="0.01"
                      className="pl-7"
                      placeholder="0.00"
                      value={isNaN(field.value) ? "" : field.value}
                      onChange={(e) => {
                        const value = e.target.value
                        field.onChange(value === "" ? undefined : parseFloat(value))
                      }}
                    />
                  </div>
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormItem>
            <FormLabel>Currency</FormLabel>
            <Input disabled readOnly value="USD" className="bg-muted cursor-not-allowed" />
          </FormItem>

        </div>

        <FormItem>
            <FormLabel>Date</FormLabel>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className={cn(
                    "w-full justify-start text-left font-normal truncate",
                    !selectedDate && "text-muted-foreground"
                  )}
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  <span className="truncate block">
                    {selectedDate ? format(selectedDate, "MMMM do, yyyy") : "Pick a date"}
                  </span>
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0 z-[9999]" align="start">
                <Calendar
                  mode="single"
                  selected={selectedDate}
                  onSelect={setSelectedDate}
                  initialFocus
                />
              </PopoverContent>
            </Popover>
          </FormItem>

        {/* Row: Description */}
        <FormField
          control={form.control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Description</FormLabel>
              <FormControl>
                <Textarea
                  {...field}
                  placeholder="Optional description (e.g., invoice #123)"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" disabled={submitting} className="w-full">
          {submitting ? "Submitting..." : "Create Entry"}
        </Button>
      </form>
    </Form>
  )
}
