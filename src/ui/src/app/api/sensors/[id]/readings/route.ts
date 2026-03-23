import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { z } from "zod";

const readingSchema = z.object({
  value: z.number(),
  timestamp: z.string().optional(),
});

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const { searchParams } = new URL(request.url);
  const hours = parseInt(searchParams.get("hours") || "24");
  const since = new Date(Date.now() - hours * 60 * 60 * 1000);

  const readings = await prisma.sensorReading.findMany({
    where: {
      sensorId: id,
      timestamp: { gte: since },
    },
    orderBy: { timestamp: "asc" },
  });
  return NextResponse.json(readings);
}

export async function POST(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const body = await request.json();
    const { value, timestamp } = readingSchema.parse(body);

    const reading = await prisma.sensorReading.create({
      data: {
        sensorId: id,
        value,
        timestamp: timestamp ? new Date(timestamp) : new Date(),
      },
    });

    // Check alert rules
    const alertRules = await prisma.alertRule.findMany({
      where: { sensorId: id, enabled: true },
      include: { sensor: true },
    });

    for (const rule of alertRules) {
      let triggered = false;
      if (rule.condition === "ABOVE" && value > rule.threshold) triggered = true;
      if (rule.condition === "BELOW" && value < rule.threshold) triggered = true;
      if (rule.condition === "EQUAL" && value === rule.threshold) triggered = true;

      if (triggered) {
        await prisma.alert.create({
          data: {
            message: `${rule.sensor.name}: value ${value} ${rule.sensor.unit} is ${rule.condition.toLowerCase()} threshold ${rule.threshold} ${rule.sensor.unit}`,
            severity: rule.severity,
            value,
            threshold: rule.threshold,
            sensorId: id,
          },
        });
      }
    }

    return NextResponse.json(reading, { status: 201 });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json({ error: error.issues }, { status: 400 });
    }
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
