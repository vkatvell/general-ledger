// components/Navbar.tsx
"use client"

import Link from "next/link"
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuList,
  NavigationMenuLink,
} from "@/components/ui/navigation-menu"
import { navigationMenuTriggerStyle } from "@/components/ui/navigation-menu"

export function Navbar() {
  return (
    <div className="border-b bg-white shadow-sm px-6 py-4">
      <NavigationMenu>
        <NavigationMenuList>
          <NavigationMenuItem>
            <Link href="/entries" passHref legacyBehavior>
              <NavigationMenuLink className={navigationMenuTriggerStyle()}>
                Entries
              </NavigationMenuLink>
            </Link>
          </NavigationMenuItem>
          <NavigationMenuItem>
            <Link href="/summary" passHref legacyBehavior>
              <NavigationMenuLink className={navigationMenuTriggerStyle()}>
                Summary
              </NavigationMenuLink>
            </Link>
          </NavigationMenuItem>
          <NavigationMenuItem>
            <Link href="/accounts" passHref legacyBehavior>
              <NavigationMenuLink className={navigationMenuTriggerStyle()}>
                Accounts
              </NavigationMenuLink>
            </Link>
          </NavigationMenuItem>
        </NavigationMenuList>
      </NavigationMenu>
    </div>
  )
}
