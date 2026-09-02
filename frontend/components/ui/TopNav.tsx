"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/", label: "Market Radar" },
  { href: "/performance", label: "Performance" },
  { href: "/about", label: "About" },
];

export function TopNav() {
  const pathname = usePathname();
  return (
    <nav className="flex items-center gap-1 rounded-full border border-white/[0.09] bg-white/[0.04] p-1">
      {LINKS.map((link) => {
        const active = pathname === link.href;
        return (
          <Link
            key={link.href}
            href={link.href}
            className="rounded-full px-3 py-1.5 text-[12px] font-semibold tracking-wide transition-colors"
            style={
              active
                ? { background: "linear-gradient(135deg, var(--belief-ai), var(--agent-diligence))", color: "white" }
                : { color: "var(--ink-muted)" }
            }
          >
            {link.label}
          </Link>
        );
      })}
    </nav>
  );
}
