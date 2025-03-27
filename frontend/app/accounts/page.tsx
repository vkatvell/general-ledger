"use client"

import { useEffect, useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { CreateAccountDialog } from "@/components/accounts/CreateAccountDialog"
import { UpdateAccountDialog } from "@/components/accounts/UpdateAccountDialog"

type Account = {
  id: string
  name: string
  is_active: boolean
  created_at: string
}

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<Account[]>([])

  const fetchAccounts = async () => {
    const res = await fetch("http://localhost:8000/api/accounts")
    const data = await res.json()
    setAccounts(data.accounts)
  }

  useEffect(() => {
    fetchAccounts()
  }, [])


  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Accounts</h1>
        <CreateAccountDialog onSuccess={fetchAccounts} />
      </div> 

      <Card>
        <CardContent className="p-4 space-y-4">
          {accounts.map((account) => (
            <div
              key={account.id}
              className="flex justify-between items-center border-b pb-3"
            >
              <div>
                <p className="font-medium">{account.name}</p>
                <p className="text-sm text-muted-foreground">
                  Created: {account.created_at.slice(0, 10)}
                </p>
              </div>
              <div className="flex items-center gap-2">
              <UpdateAccountDialog
                accountId={account.id}
                currentName={account.name}
                isActive={account.is_active}
                onSuccess={fetchAccounts}
                />
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}
