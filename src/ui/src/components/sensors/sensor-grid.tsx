import { SensorCard } from "./sensor-card";

interface SensorGridProps {
  sensors: {
    id: string;
    name: string;
    type: string;
    unit: string;
    device: {
      name: string;
      zone: { name: string; hospital: { name: string } };
    };
    readings: { value: number; timestamp: string }[];
  }[];
}

export function SensorGrid({ sensors }: SensorGridProps) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {sensors.map((sensor) => (
        <SensorCard key={sensor.id} sensor={sensor} />
      ))}
    </div>
  );
}
