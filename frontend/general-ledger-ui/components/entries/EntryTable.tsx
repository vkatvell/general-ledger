"use client"

import { useEffect, useState } from "react"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"

type TLedgerEntryList = {
  id: string
  account_name: string
  date: string
  entry_type: "debit" | "credit"
  amount: string
  currency: string
  description: string
  is_deleted: boolean
  version: number
  canadian_amount: string
}

export function EntryTable() {
  const [entries, setEntries] = useState<TLedgerEntryList[]>([])

  useEffect(() => {
    const fetchData = async () => {
      const res = await fetch("http://localhost:8000/api/entries")
      const data = await res.json()
      setEntries(data.entries)
    }

    fetchData().catch(console.error)
  }, [])

  return (
    <Card>
      <CardContent className="p-4 overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Date</TableHead>
              <TableHead>Account</TableHead>
              <TableHead>Type</TableHead>
              <TableHead className="text-right">Amount</TableHead>
              <TableHead>Currency</TableHead>
              <TableHead className="text-right">CAD $</TableHead>
              <TableHead>Description</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {entries.map((entry) => (
              <TableRow key={entry.id}>
                <TableCell>{entry.date.slice(0, 10)}</TableCell>
                <TableCell className="font-medium">{entry.account_name}</TableCell>
                <TableCell>
                  <Badge variant={entry.entry_type === "debit" ? "destructive" : "secondary"}>
                    {entry.entry_type.toUpperCase()}
                  </Badge>
                </TableCell>
                <TableCell className="text-right font-mono">
                  {Number(entry.amount).toFixed(2)}
                </TableCell>
                <TableCell>{entry.currency}</TableCell>
                <TableCell className="text-right font-mono">
                  {Number(entry.canadian_amount).toFixed(2)}
                </TableCell>
                <TableCell>{entry.description}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}
