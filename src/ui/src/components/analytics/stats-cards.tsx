import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, TrendingDown, TrendingUp, Database } from "lucide-react";

interface StatsCardsProps {
  stats: {
    sensorName: string;
    sensorType: string;
    unit: string;
    count: number;
    min: number;
    max: number;
    avg: number;
  }[];
  totalReadings: number;
}

export function StatsCards({ stats, totalReadings }: StatsCardsProps) {
  const overallAvg = stats.length > 0
    ? stats.reduce((acc, s) => acc + s.avg, 0) / stats.length
    : 0;
  const overallMin = stats.length > 0
    ? Math.min(...stats.map((s) => s.min))
    : 0;
  const overallMax = stats.length > 0
    ? Math.max(...stats.map((s) => s.max))
    : 0;

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Readings</CardTitle>
          <Database className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{totalReadings.toLocaleString()}</div>
          <p className="text-xs text-muted-foreground">From {stats.length} sensors</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Average</CardTitle>
          <Activity className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{overallAvg.toFixed(1)}</div>
          <p className="text-xs text-muted-foreground">Across all sensors</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Minimum</CardTitle>
          <TrendingDown className="h-4 w-4 text-blue-500" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{overallMin === Infinity ? "N/A" : overallMin.toFixed(1)}</div>
          <p className="text-xs text-muted-foreground">Lowest recorded value</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Maximum</CardTitle>
          <TrendingUp className="h-4 w-4 text-red-500" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{overallMax === -Infinity ? "N/A" : overallMax.toFixed(1)}</div>
          <p className="text-xs text-muted-foreground">Highest recorded value</p>
        </CardContent>
      </Card>
    </div>
  );
}
