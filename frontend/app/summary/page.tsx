"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

type SummaryData = {
  num_debits: number
  total_debit_amount: string
  num_credits: number
  total_credit_amount: string
  is_balanced: boolean
}

export default function SummaryPage() {
  const [summary, setSummary] = useState<SummaryData | null>(null)

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/summary")
        const data = await res.json()
        setSummary(data)
      } catch (err) {
        console.error("Failed to fetch summary:", err)
      }
    }

    fetchSummary()
  }, [])

  return (
    <div className="flex flex-col items-center justify-center p-8">
      <h1 className="text-2xl font-bold mb-6">Ledger Summary</h1>

      {summary ? (
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-lg">Summary Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-muted-foreground">
            <div className="flex justify-between">
              <span>Number of Debits:</span>
              <span className="font-medium text-foreground">{summary.num_debits}</span>
            </div>
            <div className="flex justify-between">
              <span>Total Debit Amount:</span>
              <span className="font-medium text-foreground">${summary.total_debit_amount}</span>
            </div>
            <div className="flex justify-between">
              <span>Number of Credits:</span>
              <span className="font-medium text-foreground">{summary.num_credits}</span>
            </div>
            <div className="flex justify-between">
              <span>Total Credit Amount:</span>
              <span className="font-medium text-foreground">${summary.total_credit_amount}</span>
            </div>
            <div className="flex justify-between pt-2 border-t">
              <span>Status:</span>
              <span className={`font-semibold ${summary.is_balanced ? "text-green-600" : "text-red-600"}`}>
                {summary.is_balanced ? "Balanced" : "Unbalanced"}
              </span>
            </div>
          </CardContent>
        </Card>
      ) : (
        <p className="text-muted-foreground">Loading summary...</p>
      )}
    </div>
  )
}
