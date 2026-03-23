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

interface AlertRuleFormProps {
  sensors: { id: string; name: string; unit: string; device: { name: string; zone: { name: string; hospital: { name: string } } } }[];
  onSuccess: () => void;
}

export function AlertRuleForm({ sensors, onSuccess }: AlertRuleFormProps) {
  const [loading, setLoading] = useState(false);
  const [sensorId, setSensorId] = useState("");
  const [condition, setCondition] = useState("");
  const [severity, setSeverity] = useState("MEDIUM");

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);

    const formData = new FormData(e.currentTarget);
    const data = {
      name: formData.get("name") as string,
      sensorId,
      condition,
      threshold: parseFloat(formData.get("threshold") as string),
      severity,
    };

    await fetch("/api/alert-rules", {
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
        <Label htmlFor="name">Rule Name</Label>
        <Input id="name" name="name" placeholder="High Temperature Alert" required />
      </div>
      <div className="space-y-2">
        <Label>Sensor</Label>
        <Select value={sensorId} onValueChange={setSensorId} required>
          <SelectTrigger>
            <SelectValue placeholder="Select sensor" />
          </SelectTrigger>
          <SelectContent>
            {sensors.map((s) => (
              <SelectItem key={s.id} value={s.id}>
                {s.name} ({s.device.zone.hospital.name}/{s.device.zone.name})
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label>Condition</Label>
          <Select value={condition} onValueChange={setCondition} required>
            <SelectTrigger>
              <SelectValue placeholder="Condition" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ABOVE">Above</SelectItem>
              <SelectItem value="BELOW">Below</SelectItem>
              <SelectItem value="EQUAL">Equal to</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label htmlFor="threshold">Threshold</Label>
          <Input id="threshold" name="threshold" type="number" step="any" required />
        </div>
      </div>
      <div className="space-y-2">
        <Label>Severity</Label>
        <Select value={severity} onValueChange={setSeverity}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="LOW">Low</SelectItem>
            <SelectItem value="MEDIUM">Medium</SelectItem>
            <SelectItem value="HIGH">High</SelectItem>
            <SelectItem value="CRITICAL">Critical</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <Button type="submit" className="w-full" disabled={loading || !sensorId || !condition}>
        {loading ? "Creating..." : "Create Alert Rule"}
      </Button>
    </form>
  );
}
