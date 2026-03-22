interface JsonCardProps {
  title: string;
  data: unknown;
}

export function JsonCard({ title, data }: JsonCardProps) {
  return (
    <section className="rounded-xl border border-black/10 bg-background p-4 shadow-sm">
      <h3 className="mb-3 text-sm font-semibold">{title}</h3>
      <pre className="max-h-80 overflow-auto rounded-lg bg-foreground/5 p-3 text-xs leading-5">
        {JSON.stringify(data, null, 2)}
      </pre>
    </section>
  );
}
