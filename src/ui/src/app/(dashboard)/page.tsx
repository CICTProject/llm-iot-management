"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Warehouse, Cpu, Bell, Activity } from "lucide-react";
import Link from "next/link";
import { AlertBanner } from "@/components/alerts/alert-banner";
import { SensorGrid } from "@/components/sensors/sensor-grid";
import { formatDistanceToNow } from "date-fns";

interface DashboardData {
  hospitals: number;
  devices: number;
  activeAlerts: number;
  sensors: any[];
  recentAlerts: any[];
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData>({
    hospitals: 0,
    devices: 0,
    activeAlerts: 0,
    sensors: [],
    recentAlerts: [],
  });

  useEffect(() => {
    Promise.all([
      fetch("/api/hospitals").then((r) => r.json()),
      fetch("/api/devices").then((r) => r.json()),
      fetch("/api/alerts?acknowledged=false").then((r) => r.json()),
      fetch("/api/sensors").then((r) => r.json()),
      fetch("/api/alerts?limit=5").then((r) => r.json()),
    ]).then(([hospitals, devices, activeAlerts, sensors, recentAlerts]) => {
      setData({
        hospitals: hospitals.length,
        devices: devices.length,
        activeAlerts: activeAlerts.length,
        sensors,
        recentAlerts,
      });
    });
  }, []);

  return (
    <div className="space-y-6">
      <AlertBanner />
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">Hospital monitoring overview</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Hospitals</CardTitle>
            <Warehouse className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.hospitals}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Devices</CardTitle>
            <Cpu className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.devices}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Alerts</CardTitle>
            <Bell className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">{data.activeAlerts}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Sensors</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.sensors.length}</div>
          </CardContent>
        </Card>
      </div>

      {data.recentAlerts.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Recent Alerts</CardTitle>
              <Link href="/alerts" className="text-sm text-primary hover:underline">
                View all
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {data.recentAlerts.slice(0, 5).map((alert: any) => (
                <div key={alert.id} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Badge
                      variant={
                        alert.severity === "CRITICAL" || alert.severity === "HIGH"
                          ? "destructive"
                          : "secondary"
                      }
                    >
                      {alert.severity}
                    </Badge>
                    <div>
                      <p className="text-sm font-medium">{alert.message}</p>
                      <p className="text-xs text-muted-foreground">
                        {alert.sensor?.name} - {formatDistanceToNow(new Date(alert.createdAt), { addSuffix: true })}
                      </p>
                    </div>
                  </div>
                  {!alert.acknowledged && (
                    <span className="text-xs text-orange-600 font-medium">Active</span>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {data.sensors.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Sensor Readings</h2>
            <Link href="/sensors" className="text-sm text-primary hover:underline">
              View all
            </Link>
          </div>
          <SensorGrid sensors={data.sensors.slice(0, 8)} />
        </div>
      )}
    </div>
  );
}
