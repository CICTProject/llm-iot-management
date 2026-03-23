"use client";

import { Button } from "@/components/ui/button";

interface DateRangePickerProps {
  hours: number;
  onChange: (hours: number) => void;
}

const ranges = [
  { label: "24h", hours: 24 },
  { label: "3d", hours: 72 },
  { label: "7d", hours: 168 },
  { label: "14d", hours: 336 },
  { label: "30d", hours: 720 },
];

export function DateRangePicker({ hours, onChange }: DateRangePickerProps) {
  return (
    <div className="flex gap-2">
      {ranges.map((range) => (
        <Button
          key={range.hours}
          variant={hours === range.hours ? "default" : "outline"}
          size="sm"
          onClick={() => onChange(range.hours)}
        >
          {range.label}
        </Button>
      ))}
    </div>
  );
}
