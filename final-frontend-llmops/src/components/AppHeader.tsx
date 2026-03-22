import Link from "next/link";

const links = [
  { href: "/chat", label: "Chat" },
  { href: "/admin", label: "Admin" },
  { href: "/health", label: "Health" },
];

export function AppHeader() {
  return (
    <header className="border-b border-black/10 bg-background/95">
      <div className="mx-auto flex w-full max-w-6xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        <Link href="/" className="text-sm font-semibold tracking-tight">
          LLMOps Frontend
        </Link>
        <nav className="flex items-center gap-3 text-sm">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="rounded-md px-3 py-1.5 text-foreground/80 transition hover:bg-foreground/10 hover:text-foreground"
            >
              {link.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
