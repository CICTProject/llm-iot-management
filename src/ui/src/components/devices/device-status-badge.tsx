import { Badge } from "@/components/ui/badge";

const statusConfig: Record<string, { label: string; variant: "default" | "secondary" | "destructive" | "outline" }> = {
  ONLINE: { label: "Online", variant: "default" },
  OFFLINE: { label: "Offline", variant: "secondary" },
  MAINTENANCE: { label: "Maintenance", variant: "outline" },
  ERROR: { label: "Error", variant: "destructive" },
};

export function DeviceStatusBadge({ status }: { status: string }) {
  const config = statusConfig[status] || { label: status, variant: "secondary" as const };
  return <Badge variant={config.variant}>{config.label}</Badge>;
}
