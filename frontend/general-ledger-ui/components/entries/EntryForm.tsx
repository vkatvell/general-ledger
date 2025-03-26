"use client"

import { useEffect, useState } from "react"

import { z } from "zod"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import {
  Command,
  CommandEmpty,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command"

import { Calendar as CalendarIcon } from "lucide-react"
import { format } from "date-fns"
import { v4 as uuidv4 } from "uuid"
import { cn } from "@/lib/utils"

const entrySchema = z.object({
  account_name: z.string().min(1, "Account is required"),
  entry_type: z.enum(["debit", "credit"]),
  amount: z.number().positive("Amount must be greater than 0"),
  currency: z.literal("USD"),
  description: z.string().optional(),
  date: z
  .union([z.string().datetime(), z.date()])
  .optional(),
})

type EntryFormData = z.infer<typeof entrySchema>

export function EntryForm() {
  const [accounts, setAccounts] = useState<string[]>([])
  const [submitting, setSubmitting] = useState(false)
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(undefined)

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<EntryFormData>({
    resolver: zodResolver(entrySchema),
    defaultValues: {
      currency: "USD",
    },
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
          date: selectedDate?.toISOString(),
          idempotency_key: uuidv4(), // Generating idempotency key automatically
        }),
      })
      if (!response.ok) throw new Error("Failed to create entry")

      reset({ amount: 0, currency: "USD", description: undefined })
    } catch (err) {
      console.error(err)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {/* Account Select */}
      <div className="flex gap-4">
        <div className="flex-1">
          <Label htmlFor="account_name" className="mb-1 block">
            Account
          </Label>
          <Popover>
            <PopoverTrigger asChild>
              <Button variant="outline" className="w-full justify-start text-left text-muted-foreground">
                {watch("account_name") || "Search accounts..."}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-full p-0" side="bottom" align="start">
              <Command>
                <CommandInput placeholder="Search accounts..." />
                <CommandList>
                  <CommandEmpty>No account found</CommandEmpty>
                  {accounts.map((acc) => (
                    <CommandItem
                      key={acc}
                      value={acc}
                      onSelect={() => setValue("account_name", acc)}
                    >
                      {acc}
                    </CommandItem>
                  ))}
                </CommandList>
              </Command>
            </PopoverContent>
          </Popover>
          {errors.account_name && (
            <p className="text-sm text-red-500">{errors.account_name.message}</p>
          )}
        </div>

      {/* Entry Type */}
      <div className="flex-1">
        <Label htmlFor="entry_type" className="mb-1 block">
          Entry Type
        </Label>
        <Select onValueChange={(val) => setValue("entry_type", val as "debit" | "credit")}>
          <SelectTrigger>
            <SelectValue placeholder="Select debit or credit" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="debit">Debit</SelectItem>
            <SelectItem value="credit">Credit</SelectItem>
          </SelectContent>
        </Select>
        {errors.entry_type && (
          <p className="text-sm text-red-500">{errors.entry_type.message}</p>
        )}
      </div>
      </div>
    
        
      {/* Amount */}
      <div className="grid grid-cols-3 gap-4">
      <div>
        <Label htmlFor="amount" className="mb-1 block">
          Amount
        </Label>
        <Input
          type="number"
          step="0.01"
          {...register("amount", { valueAsNumber: true })}
        />
        {errors.amount && <p className="text-sm text-red-500">{errors.amount.message}</p>}
      </div>

      {/* Currency (Locked to USD) */}
      <div>
        <Label htmlFor="currency" className="mb-1 block">
          Currency
        </Label>
        <Input
          {...register("currency")}
          disabled
          value="USD"
          className="bg-muted cursor-not-allowed"
        />
      </div>

      {/* Date Picker */}
      <div>
        <Label htmlFor="date" className="mb-1 block">
          Date (Optional)
        </Label>
        <Popover>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              className={cn(
                "w-full justify-start text-left font-normal",
                !selectedDate && "text-muted-foreground"
              )}
            >
              <CalendarIcon className="mr-2 h-4 w-4" />
              {selectedDate ? format(selectedDate, "PPP") : <span>Pick a date</span>}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto p-0" align="start" side="bottom">
            <Calendar
              mode="single"
              selected={selectedDate}
              onSelect={setSelectedDate}
              initialFocus
            />
          </PopoverContent>
        </Popover>
      </div>
    </div>


      {/* Description */}
      <div>
        <Label htmlFor="description" className="mb-1 block">
          Description
        </Label>
        <Textarea
          {...register("description")}
          placeholder="Optional description (e.g., invoice #123)"
          className="resize-none"
        />
      </div>

      <Button type="submit" disabled={submitting} className="w-full">
        {submitting ? "Submitting..." : "Create Entry"}
      </Button>
    </form>
  )
}
