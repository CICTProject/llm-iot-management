"use client";

import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MapPin, Boxes, Cpu } from "lucide-react";

interface HospitalCardProps {
  hospital: {
    id: string;
    name: string;
    location: string;
    description: string | null;
    zones: { id: string; devices: { id: string; sensors: { id: string }[] }[] }[];
  };
}

export function HospitalCard({ hospital }: HospitalCardProps) {
  const totalDevices = hospital.zones.reduce(
    (acc, z) => acc + z.devices.length,
    0
  );

  return (
    <Link href={`/hospitals/${hospital.id}`}>
      <Card className="hover:shadow-md transition-shadow cursor-pointer">
        <CardHeader className="pb-2">
          <CardTitle className="text-lg">{hospital.name}</CardTitle>
          <div className="flex items-center gap-1 text-muted-foreground">
            <MapPin className="h-3 w-3" />
            <span className="text-sm">{hospital.location}</span>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex gap-3">
            <Badge variant="secondary" className="gap-1">
              <Boxes className="h-3 w-3" />
              {hospital.zones.length} zones
            </Badge>
            <Badge variant="secondary" className="gap-1">
              <Cpu className="h-3 w-3" />
              {totalDevices} devices
            </Badge>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
