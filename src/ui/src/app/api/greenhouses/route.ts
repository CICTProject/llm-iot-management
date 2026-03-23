import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { z } from "zod";

const hospitalSchema = z.object({
  name: z.string().min(1),
  location: z.string().min(1),
  description: z.string().optional(),
  imageUrl: z.string().optional(),
});

export async function GET() {
  const hospitals = await prisma.hospital.findMany({
    include: {
      zones: {
        include: {
          devices: {
            include: { sensors: true },
          },
        },
      },
    },
    orderBy: { createdAt: "desc" },
  });
  return NextResponse.json(hospitals);
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const data = hospitalSchema.parse(body);
    const hospital = await prisma.hospital.create({ data });
    return NextResponse.json(hospital, { status: 201 });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json({ error: error.issues }, { status: 400 });
    }
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
