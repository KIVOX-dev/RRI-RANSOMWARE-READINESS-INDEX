export function EmptyState({ title, description }: { title: string; description: string }) {
  return (
    <div className="border border-dashed border-border rounded-card p-8 text-center">
      <div className="text-light font-medium">{title}</div>
      <div className="text-sm text-muted mt-1 max-w-md mx-auto">{description}</div>
    </div>
  );
}
