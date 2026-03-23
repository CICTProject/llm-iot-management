import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const acknowledged = searchParams.get("acknowledged");
  const severity = searchParams.get("severity");
  const limit = parseInt(searchParams.get("limit") || "50");

  const where: Record<string, unknown> = {};
  if (acknowledged !== null && acknowledged !== "") {
    where.acknowledged = acknowledged === "true";
  }
  if (severity) {
    where.severity = severity;
  }

  const alerts = await prisma.alert.findMany({
    where,
    include: {
      sensor: {
        include: {
          device: { include: { zone: { include: { hospital: true } } } },
        },
      },
    },
    orderBy: { createdAt: "desc" },
    take: limit,
  });
  return NextResponse.json(alerts);
}

export async function PATCH(request: Request) {
  const body = await request.json();
  const { id, acknowledged } = body;

  const alert = await prisma.alert.update({
    where: { id },
    data: { acknowledged },
  });
  return NextResponse.json(alert);
}
