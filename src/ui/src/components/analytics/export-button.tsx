"use client";

import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";

interface ExportButtonProps {
  hours: number;
}

export function ExportButton({ hours }: ExportButtonProps) {
  function handleExport() {
    window.open(`/api/analytics/export?hours=${hours}`, "_blank");
  }

  return (
    <Button variant="outline" onClick={handleExport}>
      <Download className="mr-2 h-4 w-4" />
      Export CSV
    </Button>
  );
}
