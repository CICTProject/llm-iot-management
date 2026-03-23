"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface DeviceFormProps {
  zones: { id: string; name: string; hospitalName: string }[];
  onSuccess: () => void;
}

export function DeviceForm({ zones, onSuccess }: DeviceFormProps) {
  const [loading, setLoading] = useState(false);
  const [zoneId, setZoneId] = useState("");

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);

    const formData = new FormData(e.currentTarget);
    const data = {
      name: formData.get("name") as string,
      type: formData.get("type") as string,
      zoneId,
    };

    await fetch("/api/devices", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    setLoading(false);
    onSuccess();
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="name">Device Name</Label>
        <Input id="name" name="name" placeholder="Temperature Sensor Hub" required />
      </div>
      <div className="space-y-2">
        <Label htmlFor="type">Device Type</Label>
        <Input id="type" name="type" placeholder="ESP32, Arduino, etc." required />
      </div>
      <div className="space-y-2">
        <Label>Zone</Label>
        <Select value={zoneId} onValueChange={setZoneId} required>
          <SelectTrigger>
            <SelectValue placeholder="Select a zone" />
          </SelectTrigger>
          <SelectContent>
            {zones.map((zone) => (
              <SelectItem key={zone.id} value={zone.id}>
                {zone.hospitalName} - {zone.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <Button type="submit" className="w-full" disabled={loading || !zoneId}>
        {loading ? "Saving..." : "Save Device"}
      </Button>
    </form>
  );
}
