"use client";

import { useEffect, useState } from "react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertTriangle, X } from "lucide-react";
import { Button } from "@/components/ui/button";

export function AlertBanner() {
  const [alerts, setAlerts] = useState<{ id: string; severity: string }[]>([]);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    fetch("/api/alerts?acknowledged=false&limit=5")
      .then((res) => res.json())
      .then(setAlerts)
      .catch(() => {});
  }, []);

  const criticalAlerts = alerts.filter(
    (a) => a.severity === "CRITICAL" || a.severity === "HIGH"
  );

  if (dismissed || criticalAlerts.length === 0) return null;

  return (
    <Alert variant="destructive" className="mb-4">
      <AlertTriangle className="h-4 w-4" />
      <AlertDescription className="flex items-center justify-between">
        <span>
          {criticalAlerts.length} critical/high alert{criticalAlerts.length > 1 ? "s" : ""} require attention
        </span>
        <Button
          variant="ghost"
          size="icon"
          className="h-6 w-6"
          onClick={() => setDismissed(true)}
        >
          <X className="h-3 w-3" />
        </Button>
      </AlertDescription>
    </Alert>
  );
}
