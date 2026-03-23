import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { z } from "zod";

const alertRuleSchema = z.object({
  name: z.string().min(1),
  sensorId: z.string().min(1),
  condition: z.enum(["ABOVE", "BELOW", "EQUAL"]),
  threshold: z.number(),
  severity: z.enum(["LOW", "MEDIUM", "HIGH", "CRITICAL"]).optional(),
  enabled: z.boolean().optional(),
});

export async function GET() {
  const rules = await prisma.alertRule.findMany({
    include: { sensor: { include: { device: { include: { zone: { include: { hospital: true } } } } } } },
    orderBy: { createdAt: "desc" },
  });
  return NextResponse.json(rules);
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const data = alertRuleSchema.parse(body);
    const rule = await prisma.alertRule.create({
      data,
      include: { sensor: true },
    });
    return NextResponse.json(rule, { status: 201 });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json({ error: error.issues }, { status: 400 });
    }
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
