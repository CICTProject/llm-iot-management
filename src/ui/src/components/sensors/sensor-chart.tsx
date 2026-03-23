"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { format } from "date-fns";

interface SensorChartProps {
  readings: { value: number; timestamp: string }[];
  unit: string;
  sensorName: string;
}

export function SensorChart({ readings, unit, sensorName }: SensorChartProps) {
  if (readings.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-muted-foreground">
        No data available for the selected time range
      </div>
    );
  }

  const data = readings.map((r) => ({
    time: format(new Date(r.timestamp), "MMM dd HH:mm"),
    value: r.value,
    fullTime: new Date(r.timestamp).toLocaleString(),
  }));

  return (
    <ResponsiveContainer width="100%" height={350}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="hsl(142, 76%, 36%)" stopOpacity={0.3} />
            <stop offset="95%" stopColor="hsl(142, 76%, 36%)" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
        <XAxis
          dataKey="time"
          className="text-xs"
          tick={{ fontSize: 12 }}
          interval="preserveStartEnd"
        />
        <YAxis
          className="text-xs"
          tick={{ fontSize: 12 }}
          label={{ value: unit, angle: -90, position: "insideLeft" }}
        />
        <Tooltip
          content={({ active, payload }) => {
            if (active && payload && payload.length) {
              return (
                <div className="rounded-lg border bg-background p-2 shadow-md">
                  <p className="text-sm font-medium">{sensorName}</p>
                  <p className="text-sm text-muted-foreground">
                    {payload[0].payload.fullTime}
                  </p>
                  <p className="text-sm font-bold">
                    {Number(payload[0].value).toFixed(2)} {unit}
                  </p>
                </div>
              );
            }
            return null;
          }}
        />
        <Area
          type="monotone"
          dataKey="value"
          stroke="hsl(142, 76%, 36%)"
          fill="url(#colorValue)"
          strokeWidth={2}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
