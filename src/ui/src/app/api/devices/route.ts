import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { z } from "zod";

const deviceSchema = z.object({
  name: z.string().min(1),
  type: z.string().min(1),
  zoneId: z.string().min(1),
  status: z.enum(["ONLINE", "OFFLINE", "MAINTENANCE", "ERROR"]).optional(),
});

export async function GET() {
  const devices = await prisma.device.findMany({
    include: {
      sensors: true,
      zone: { include: { hospital: true } },
    },
    orderBy: { createdAt: "desc" },
  });
  return NextResponse.json(devices);
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const data = deviceSchema.parse(body);
    const device = await prisma.device.create({
      data,
      include: { zone: { include: { hospital: true } }, sensors: true },
    });
    return NextResponse.json(device, { status: 201 });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json({ error: error.issues }, { status: 400 });
    }
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
