// src/app/entries/page.tsx

"use client"

import { useEffect, useState } from "react"

import { EntryTable } from "@/components/entries/EntryTable"
import { CreateEntryDialog } from "@/components/entries/CreateEntryDialog"
import { useDebounce } from "@/hooks/useDebounce"

import {
  Sheet,
  SheetContent,
  SheetTrigger,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { Label } from "@/components/ui/label"
import { FilterIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Input } from "@/components/ui/input"
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"

import { format } from "date-fns"
import { CalendarIcon, XIcon, RefreshCwIcon } from "lucide-react"

export default function EntriesPage() {
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(true)

  const [accountName, setAccountName] = useState("")
  const [currency, setCurrency] = useState("")
  const [entryType, setEntryType] = useState("")
  const [startDate, setStartDate] = useState<Date | undefined>()
  const [endDate, setEndDate] = useState<Date | undefined>()

  const debouncedAccountName = useDebounce(accountName)
  const debouncedCurrency = useDebounce(currency)

  const fetchEntries = async () => {
    try {
      setLoading(true)

      const params = new URLSearchParams()
      if (debouncedAccountName) params.append("account_name", debouncedAccountName)
      if (debouncedCurrency) params.append("currency", debouncedCurrency)
      if (entryType) params.append("entry_type", entryType)
      if (startDate) params.append("start_date", startDate.toISOString())
      if (endDate) params.append("end_date", endDate.toISOString())

      const res = await fetch(`http://localhost:8000/api/entries?${params.toString()}`)
      const data = await res.json()
      setEntries(data.entries)
    } catch (error) {
      console.error("Failed to fetch entries", error)
    } finally {
      setLoading(false)
    }
  }

  const clearFilters = () => {
    setAccountName("")
    setCurrency("")
    setEntryType("")
    setStartDate(undefined)
    setEndDate(undefined)
  }

  useEffect(() => {
    fetchEntries()
  }, [debouncedAccountName, debouncedCurrency, entryType, startDate, endDate])


  return (
  <div className="p-6 space-y-6">
  <div className="flex justify-between items-center">
    <h1 className="text-2xl font-bold">Ledger Entries</h1>
    <div className="flex gap-2">
      <Sheet>
        <SheetTrigger asChild>
          <Button variant="outline">
            <FilterIcon className="w-4 h-4 mr-2" />
            Filters
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-[300px] sm:w-[320px] px-5">
          <SheetHeader>
            <SheetTitle>Search Filters</SheetTitle>
          </SheetHeader>

          {/* Filter Content */}
          <div className="pt-4 space-y-4">
            <div>
              <Label className="mb-1 block text-sm">Account Name</Label>
              <Input
                placeholder="Account Name"
                value={accountName}
                onChange={(e) => setAccountName(e.target.value)}
              />
            </div>

            <div>
              <Label className="mb-1 block text-sm">Currency</Label>
              <Input
                placeholder="Currency (e.g. USD)"
                value={currency}
                onChange={(e) => setCurrency(e.target.value)}
              />
            </div>

            <div>
              <Label className="mb-1 block text-sm">Entry Type</Label>
              <Select value={entryType} onValueChange={setEntryType}>
                <SelectTrigger>
                  <SelectValue placeholder="Entry Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="debit">Debit</SelectItem>
                  <SelectItem value="credit">Credit</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label className="mb-1 block text-sm">Start Date</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button variant="outline" className="w-full justify-start text-left">
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {startDate ? format(startDate, "MMM d, yyyy") : "Start Date"}
                  </Button>
                </PopoverTrigger>
                <PopoverContent align="start" className="w-auto p-0">
                  <Calendar mode="single" selected={startDate} onSelect={setStartDate} initialFocus />
                </PopoverContent>
              </Popover>
            </div>

            <div>
              <Label className="mb-1 block text-sm">End Date</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button variant="outline" className="w-full justify-start text-left">
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {endDate ? format(endDate, "MMM d, yyyy") : "End Date"}
                  </Button>
                </PopoverTrigger>
                <PopoverContent align="start" className="w-auto p-0">
                  <Calendar mode="single" selected={endDate} onSelect={setEndDate} initialFocus />
                </PopoverContent>
              </Popover>
            </div>

            <div className="pt-2">
              <Button variant="outline" onClick={clearFilters} size="sm" className="text-red-500">
                <XIcon className="h-4 w-4 mr-1" />
                Clear Filters
              </Button>
            </div>
          </div>
        </SheetContent>
      </Sheet>

      <Button variant="outline" onClick={fetchEntries}>
        <RefreshCwIcon className="mr-1 h-4 w-4" />
        Refresh
      </Button>

      <CreateEntryDialog onSuccess={fetchEntries} />
    </div>
  </div>

  {/* Entries Table with Skeleton Loading */}
  {loading ? (
  <div className="space-y-2 rounded-md border p-4">
    {/* Skeleton loading rows */}
    {Array.from({ length: 5 }).map((_, i) => (
      <div key={i} className="flex items-center justify-between py-2">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-4 w-20" />
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-4 w-36" />
      </div>
    ))}
  </div>
) : (
  <EntryTable entries={entries} onRefresh={fetchEntries} />
  )}
</div>
  )
}
