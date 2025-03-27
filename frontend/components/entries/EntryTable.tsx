"use client"

import { UpdateEntryDialog } from "./UpdateEntryDialog"
import { ViewEntryDialog } from "./ViewEntryDialog"
import { DeleteEntryDialog } from "./DeleteEntryDialog"
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

type Props = {
  entries: TLedgerEntryList[]
  onRefresh?: () => void
}

export function EntryTable({ entries, onRefresh }: Props) {
  if (!entries || entries.length === 0) {
    return <p className="text-muted-foreground">No entries found.</p>
  }

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
              <TableHead>Actions</TableHead>
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
                <TableCell className="flex gap-2">
                  <ViewEntryDialog entryId={entry.id} />
                  <UpdateEntryDialog entryId={entry.id} onSuccess={onRefresh} />
                  <DeleteEntryDialog entryId={entry.id} onSuccess={onRefresh} />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}
