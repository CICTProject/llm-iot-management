import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const sensor = await prisma.sensor.findUnique({
    where: { id },
    include: {
      device: { include: { zone: { include: { hospital: true } } } },
      alertRules: true,
    },
  });
  if (!sensor) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }
  return NextResponse.json(sensor);
}

export async function DELETE(
  _request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  await prisma.sensor.delete({ where: { id } });
  return NextResponse.json({ success: true });
}
