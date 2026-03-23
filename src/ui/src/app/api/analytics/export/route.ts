import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const hours = parseInt(searchParams.get("hours") || "168");
  const since = new Date(Date.now() - hours * 60 * 60 * 1000);

  const readings = await prisma.sensorReading.findMany({
    where: { timestamp: { gte: since } },
    include: {
      sensor: {
        include: {
          device: {
            include: { zone: { include: { hospital: true } } },
          },
        },
      },
    },
    orderBy: { timestamp: "asc" },
  });

  const header = "Timestamp,Hospital,Zone,Device,Sensor,Type,Value,Unit\n";
  const rows = readings.map((r) =>
    [
      r.timestamp.toISOString(),
      r.sensor.device.zone.hospital.name,
      r.sensor.device.zone.name,
      r.sensor.device.name,
      r.sensor.name,
      r.sensor.type,
      r.value,
      r.sensor.unit,
    ].join(",")
  );

  const csv = header + rows.join("\n");

  return new NextResponse(csv, {
    headers: {
      "Content-Type": "text/csv",
      "Content-Disposition": `attachment; filename="hospital-data-${new Date().toISOString().split("T")[0]}.csv"`,
    },
  });
}
