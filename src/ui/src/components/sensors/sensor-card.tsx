import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Thermometer, Droplets, Sun, Wind, Sprout } from "lucide-react";
import { type LucideIcon } from "lucide-react";

const sensorIcons: Record<string, LucideIcon> = {
  TEMPERATURE: Thermometer,
  HUMIDITY: Droplets,
  SOIL_MOISTURE: Sprout,
  LIGHT: Sun,
  CO2: Wind,
};

const sensorColors: Record<string, string> = {
  TEMPERATURE: "text-red-500",
  HUMIDITY: "text-blue-500",
  SOIL_MOISTURE: "text-green-500",
  LIGHT: "text-yellow-500",
  CO2: "text-purple-500",
};

interface SensorCardProps {
  sensor: {
    id: string;
    name: string;
    type: string;
    unit: string;
    device: {
      name: string;
      zone: { name: string; hospital: { name: string } };
    };
    readings: { value: number; timestamp: string }[];
  };
}

export function SensorCard({ sensor }: SensorCardProps) {
  const Icon = sensorIcons[sensor.type] || Thermometer;
  const color = sensorColors[sensor.type] || "text-gray-500";
  const latestReading = sensor.readings[0];

  return (
    <Link href={`/sensors/${sensor.id}`}>
      <Card className="hover:shadow-md transition-shadow cursor-pointer">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-medium">{sensor.name}</CardTitle>
            <Icon className={`h-4 w-4 ${color}`} />
          </div>
          <p className="text-xs text-muted-foreground">
            {sensor.device.zone.hospital.name} / {sensor.device.zone.name}
          </p>
        </CardHeader>
        <CardContent>
          <div className={`text-2xl font-bold ${color}`}>
            {latestReading
              ? `${latestReading.value.toFixed(1)} ${sensor.unit}`
              : "No data"}
          </div>
          {latestReading && (
            <p className="text-xs text-muted-foreground mt-1">
              {new Date(latestReading.timestamp).toLocaleString()}
            </p>
          )}
        </CardContent>
      </Card>
    </Link>
  );
}
