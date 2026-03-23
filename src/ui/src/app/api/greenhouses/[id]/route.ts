import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { z } from "zod";

const updateSchema = z.object({
  name: z.string().min(1).optional(),
  location: z.string().min(1).optional(),
  description: z.string().optional(),
  imageUrl: z.string().optional(),
});

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const hospital = await prisma.hospital.findUnique({
    where: { id },
    include: {
      zones: {
        include: {
          devices: {
            include: { sensors: { include: { readings: { take: 1, orderBy: { timestamp: "desc" } } } } },
          },
        },
      },
    },
  });
  if (!hospital) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }
  return NextResponse.json(hospital);
}

export async function PUT(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const body = await request.json();
    const data = updateSchema.parse(body);
    const hospital = await prisma.hospital.update({
      where: { id },
      data,
    });
    return NextResponse.json(hospital);
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json({ error: error.issues }, { status: 400 });
    }
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

export async function DELETE(
  _request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  await prisma.hospital.delete({ where: { id } });
  return NextResponse.json({ success: true });
}
