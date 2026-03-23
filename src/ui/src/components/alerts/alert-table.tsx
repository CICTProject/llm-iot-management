"use client";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Check } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

interface AlertItem {
  id: string;
  message: string;
  severity: string;
  value: number;
  threshold: number;
  acknowledged: boolean;
  createdAt: string;
  sensor: {
    name: string;
    unit: string;
    device: { name: string; zone: { name: string; hospital: { name: string } } };
  };
}

interface AlertTableProps {
  alerts: AlertItem[];
  onAcknowledge: (id: string) => void;
}

const severityVariant: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
  CRITICAL: "destructive",
  HIGH: "destructive",
  MEDIUM: "default",
  LOW: "secondary",
};

export function AlertTable({ alerts, onAcknowledge }: AlertTableProps) {
  if (alerts.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        No alerts found.
      </div>
    );
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Severity</TableHead>
            <TableHead>Message</TableHead>
            <TableHead>Sensor</TableHead>
            <TableHead>Location</TableHead>
            <TableHead>Time</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="w-[50px]"></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {alerts.map((alert) => (
            <TableRow key={alert.id} className={alert.acknowledged ? "opacity-60" : ""}>
              <TableCell>
                <Badge variant={severityVariant[alert.severity] || "secondary"}>
                  {alert.severity}
                </Badge>
              </TableCell>
              <TableCell className="max-w-xs truncate">{alert.message}</TableCell>
              <TableCell>{alert.sensor.name}</TableCell>
              <TableCell className="text-sm">
                {alert.sensor.device.zone.hospital.name} / {alert.sensor.device.zone.name}
              </TableCell>
              <TableCell className="text-sm text-muted-foreground">
                {formatDistanceToNow(new Date(alert.createdAt), { addSuffix: true })}
              </TableCell>
              <TableCell>
                {alert.acknowledged ? (
                  <span className="text-xs text-muted-foreground">Acknowledged</span>
                ) : (
                  <span className="text-xs text-orange-600 font-medium">Active</span>
                )}
              </TableCell>
              <TableCell>
                {!alert.acknowledged && (
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => onAcknowledge(alert.id)}
                    title="Acknowledge"
                  >
                    <Check className="h-4 w-4" />
                  </Button>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
