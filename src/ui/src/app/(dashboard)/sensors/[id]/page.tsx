"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft } from "lucide-react";
import { SensorChart } from "@/components/sensors/sensor-chart";

interface Sensor {
  id: string;
  name: string;
  type: string;
  unit: string;
  minValue: number | null;
  maxValue: number | null;
  device: {
    name: string;
    zone: { name: string; hospital: { name: string } };
  };
  alertRules: { id: string; name: string; condition: string; threshold: number; severity: string; enabled: boolean }[];
}

interface Reading {
  id: string;
  value: number;
  timestamp: string;
}

export default function SensorDetailPage() {
  const params = useParams();
  const [sensor, setSensor] = useState<Sensor | null>(null);
  const [readings, setReadings] = useState<Reading[]>([]);
  const [hours, setHours] = useState(24);

  useEffect(() => {
    fetch(`/api/sensors/${params.id}`)
      .then((res) => res.json())
      .then(setSensor);
  }, [params.id]);

  useEffect(() => {
    fetch(`/api/sensors/${params.id}/readings?hours=${hours}`)
      .then((res) => res.json())
      .then(setReadings);
  }, [params.id, hours]);

  if (!sensor) return <div className="p-6">Loading...</div>;

  const latestReading = readings[readings.length - 1];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/sensors">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold">{sensor.name}</h1>
          <p className="text-sm text-muted-foreground">
            {sensor.device.zone.hospital.name} / {sensor.device.zone.name} / {sensor.device.name}
          </p>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Current Reading
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {latestReading ? `${latestReading.value.toFixed(1)} ${sensor.unit}` : "N/A"}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Sensor Type
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-xl font-semibold">{sensor.type.replace("_", " ")}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Readings
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-xl font-semibold">{readings.length}</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Historical Data</CardTitle>
            <div className="flex gap-2">
              {[6, 12, 24, 48, 168].map((h) => (
                <Button
                  key={h}
                  variant={hours === h ? "default" : "outline"}
                  size="sm"
                  onClick={() => setHours(h)}
                >
                  {h < 24 ? `${h}h` : `${h / 24}d`}
                </Button>
              ))}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <SensorChart readings={readings} unit={sensor.unit} sensorName={sensor.name} />
        </CardContent>
      </Card>

      {sensor.alertRules.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Alert Rules</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {sensor.alertRules.map((rule) => (
                <div key={rule.id} className="flex items-center justify-between rounded-lg border p-3">
                  <div>
                    <p className="font-medium">{rule.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {rule.condition} {rule.threshold} {sensor.unit}
                    </p>
                  </div>
                  <span className="text-sm text-muted-foreground">{rule.severity}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
