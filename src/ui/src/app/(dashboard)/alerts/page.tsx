"use client";

import { useEffect, useState } from "react";
import { AlertTable } from "@/components/alerts/alert-table";
import { AlertRuleForm } from "@/components/alerts/alert-rule-form";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Plus } from "lucide-react";

interface Alert {
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

interface AlertRule {
  id: string;
  name: string;
  condition: string;
  threshold: number;
  severity: string;
  enabled: boolean;
  sensor: {
    name: string;
    unit: string;
    device: { name: string; zone: { name: string; hospital: { name: string } } };
  };
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [sensors, setSensors] = useState([]);
  const [open, setOpen] = useState(false);

  async function loadAlerts() {
    const res = await fetch("/api/alerts");
    setAlerts(await res.json());
  }

  async function loadRules() {
    const res = await fetch("/api/alert-rules");
    setRules(await res.json());
  }

  async function loadSensors() {
    const res = await fetch("/api/sensors");
    setSensors(await res.json());
  }

  useEffect(() => {
    loadAlerts();
    loadRules();
    loadSensors();
  }, []);

  async function handleAcknowledge(id: string) {
    await fetch("/api/alerts", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, acknowledged: true }),
    });
    loadAlerts();
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Alerts</h1>
          <p className="text-muted-foreground">Monitor and manage alert rules and notifications</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add Alert Rule
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create Alert Rule</DialogTitle>
            </DialogHeader>
            <AlertRuleForm
              sensors={sensors}
              onSuccess={() => {
                setOpen(false);
                loadRules();
              }}
            />
          </DialogContent>
        </Dialog>
      </div>

      <Tabs defaultValue="alerts">
        <TabsList>
          <TabsTrigger value="alerts">Alerts ({alerts.filter((a) => !a.acknowledged).length} active)</TabsTrigger>
          <TabsTrigger value="rules">Rules ({rules.length})</TabsTrigger>
        </TabsList>
        <TabsContent value="alerts" className="mt-4">
          <AlertTable alerts={alerts} onAcknowledge={handleAcknowledge} />
        </TabsContent>
        <TabsContent value="rules" className="mt-4">
          <div className="space-y-2">
            {rules.map((rule) => (
              <div key={rule.id} className="flex items-center justify-between rounded-lg border p-4">
                <div>
                  <p className="font-medium">{rule.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {rule.sensor.name}: {rule.condition} {rule.threshold} {rule.sensor.unit}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-xs px-2 py-1 rounded ${
                    rule.severity === "CRITICAL" ? "bg-red-100 text-red-800" :
                    rule.severity === "HIGH" ? "bg-orange-100 text-orange-800" :
                    rule.severity === "MEDIUM" ? "bg-yellow-100 text-yellow-800" :
                    "bg-blue-100 text-blue-800"
                  }`}>
                    {rule.severity}
                  </span>
                  <span className={`text-xs ${rule.enabled ? "text-green-600" : "text-muted-foreground"}`}>
                    {rule.enabled ? "Active" : "Disabled"}
                  </span>
                </div>
              </div>
            ))}
            {rules.length === 0 && (
              <div className="text-center py-12 text-muted-foreground">
                No alert rules configured.
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
