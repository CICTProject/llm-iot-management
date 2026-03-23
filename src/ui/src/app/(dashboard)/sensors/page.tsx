"use client";

import { useEffect, useState } from "react";
import { SensorGrid } from "@/components/sensors/sensor-grid";

interface Sensor {
  id: string;
  name: string;
  type: string;
  unit: string;
  device: {
    name: string;
    zone: { name: string; hospital: { name: string } };
  };
  readings: { value: number; timestamp: string }[];
}

export default function SensorsPage() {
  const [sensors, setSensors] = useState<Sensor[]>([]);

  useEffect(() => {
    fetch("/api/sensors")
      .then((res) => res.json())
      .then(setSensors);
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Sensors</h1>
        <p className="text-muted-foreground">
          Monitor all sensor readings across your devices and zones in one place
        </p>
      </div>
      <SensorGrid sensors={sensors} />
      {sensors.length === 0 && (
        <div className="text-center py-12 text-muted-foreground">
          No sensors found. Add sensors to your devices to start monitoring.
        </div>
      )}
    </div>
  );
}
