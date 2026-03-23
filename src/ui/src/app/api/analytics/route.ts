import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const hours = parseInt(searchParams.get("hours") || "168");
  const sensorType = searchParams.get("sensorType");
  const since = new Date(Date.now() - hours * 60 * 60 * 1000);

  const where: Record<string, unknown> = {
    timestamp: { gte: since },
  };
  if (sensorType) {
    where.sensor = { type: sensorType };
  }

  const readings = await prisma.sensorReading.findMany({
    where,
    include: {
      sensor: {
        select: { name: true, type: true, unit: true },
      },
    },
    orderBy: { timestamp: "asc" },
  });

  const sensorStats: Record<string, {
    sensorName: string;
    sensorType: string;
    unit: string;
    count: number;
    min: number;
    max: number;
    sum: number;
    avg: number;
    readings: { value: number; timestamp: string }[];
  }> = {};

  for (const reading of readings) {
    const key = reading.sensorId;
    if (!sensorStats[key]) {
      sensorStats[key] = {
        sensorName: reading.sensor.name,
        sensorType: reading.sensor.type,
        unit: reading.sensor.unit,
        count: 0,
        min: Infinity,
        max: -Infinity,
        sum: 0,
        avg: 0,
        readings: [],
      };
    }
    const s = sensorStats[key];
    s.count++;
    s.min = Math.min(s.min, reading.value);
    s.max = Math.max(s.max, reading.value);
    s.sum += reading.value;
    s.avg = s.sum / s.count;
    s.readings.push({ value: reading.value, timestamp: reading.timestamp.toISOString() });
  }

  return NextResponse.json({
    stats: Object.entries(sensorStats).map(([id, s]) => ({ sensorId: id, ...s })),
    totalReadings: readings.length,
  });
}
