"use client";

import { useEffect, useState } from "react";
import { TrendChart } from "@/components/analytics/trend-chart";
import { StatsCards } from "@/components/analytics/stats-cards";
import { DateRangePicker } from "@/components/analytics/date-range-picker";
import { ExportButton } from "@/components/analytics/export-button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface SensorStat {
  sensorId: string;
  sensorName: string;
  sensorType: string;
  unit: string;
  count: number;
  min: number;
  max: number;
  avg: number;
  readings: { value: number; timestamp: string }[];
}

export default function AnalyticsPage() {
  const [stats, setStats] = useState<SensorStat[]>([]);
  const [totalReadings, setTotalReadings] = useState(0);
  const [hours, setHours] = useState(168);
  const [sensorType, setSensorType] = useState("all");

  useEffect(() => {
    const params = new URLSearchParams({ hours: hours.toString() });
    if (sensorType !== "all") params.set("sensorType", sensorType);
    fetch(`/api/analytics?${params}`)
      .then((res) => res.json())
      .then((data) => {
        setStats(data.stats);
        setTotalReadings(data.totalReadings);
      });
  }, [hours, sensorType]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Analytics</h1>
          <p className="text-muted-foreground">Sensor data trends and statistics</p>
        </div>
        <ExportButton hours={hours} />
      </div>

      <div className="flex flex-wrap gap-4">
        <DateRangePicker hours={hours} onChange={setHours} />
        <Select value={sensorType} onValueChange={setSensorType}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="All sensor types" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            <SelectItem value="TEMPERATURE">Temperature</SelectItem>
            <SelectItem value="HUMIDITY">Humidity</SelectItem>
            <SelectItem value="SOIL_MOISTURE">Soil Moisture</SelectItem>
            <SelectItem value="LIGHT">Light</SelectItem>
            <SelectItem value="CO2">CO2</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <StatsCards stats={stats} totalReadings={totalReadings} />
      <TrendChart stats={stats} />
    </div>
  );
}
