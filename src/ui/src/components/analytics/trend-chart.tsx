"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { format } from "date-fns";

const COLORS = [
  "#22c55e",
  "#3b82f6",
  "#f59e0b",
  "#ef4444",
  "#8b5cf6",
];

interface TrendChartProps {
  stats: {
    sensorId: string;
    sensorName: string;
    sensorType: string;
    unit: string;
    readings: { value: number; timestamp: string }[];
  }[];
}

export function TrendChart({ stats }: TrendChartProps) {
  if (stats.length === 0) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-64 text-muted-foreground">
          No data available for the selected time range
        </CardContent>
      </Card>
    );
  }

  const byType: Record<string, typeof stats> = {};
  for (const s of stats) {
    if (!byType[s.sensorType]) byType[s.sensorType] = [];
    byType[s.sensorType].push(s);
  }

  return (
    <div className="space-y-4">
      {Object.entries(byType).map(([type, sensors]) => {
        const timeMap = new Map<string, Record<string, number>>();
        sensors.forEach((sensor) => {
          sensor.readings.forEach((r) => {
            const key = format(new Date(r.timestamp), "MMM dd HH:mm");
            if (!timeMap.has(key)) timeMap.set(key, {});
            timeMap.get(key)![sensor.sensorName] = r.value;
          });
        });

        const data = Array.from(timeMap.entries())
          .map(([time, values]) => ({ time, ...values }))
          .slice(-100);

        return (
          <Card key={type}>
            <CardHeader>
              <CardTitle>{type.replace("_", " ")} ({sensors[0]?.unit})</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={data}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis dataKey="time" tick={{ fontSize: 12 }} interval="preserveStartEnd" />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Legend />
                  {sensors.map((sensor, i) => (
                    <Line
                      key={sensor.sensorId}
                      type="monotone"
                      dataKey={sensor.sensorName}
                      stroke={COLORS[i % COLORS.length]}
                      strokeWidth={2}
                      dot={false}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
