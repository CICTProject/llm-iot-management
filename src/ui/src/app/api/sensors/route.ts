import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { z } from "zod";

const sensorSchema = z.object({
  name: z.string().min(1),
  type: z.enum(["TEMPERATURE", "HUMIDITY", "SOIL_MOISTURE", "LIGHT", "CO2"]),
  unit: z.string().min(1),
  deviceId: z.string().min(1),
  minValue: z.number().optional(),
  maxValue: z.number().optional(),
});

export async function GET() {
  const sensors = await prisma.sensor.findMany({
    include: {
      device: { include: { zone: { include: { hospital: true } } } },
      readings: { take: 1, orderBy: { timestamp: "desc" } },
    },
    orderBy: { createdAt: "desc" },
  });
  return NextResponse.json(sensors);
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const data = sensorSchema.parse(body);
    const sensor = await prisma.sensor.create({
      data,
      include: { device: { include: { zone: { include: { hospital: true } } } } },
    });
    return NextResponse.json(sensor, { status: 201 });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json({ error: error.issues }, { status: 400 });
    }
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
