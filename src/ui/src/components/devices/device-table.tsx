"use client";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { DeviceStatusBadge } from "./device-status-badge";
import { Button } from "@/components/ui/button";
import { Trash2 } from "lucide-react";

interface Device {
  id: string;
  name: string;
  type: string;
  status: string;
  lastSeen: string;
  sensors: { id: string }[];
  zone: {
    name: string;
    hospital: { name: string };
  };
}

interface DeviceTableProps {
  devices: Device[];
  onRefresh: () => void;
}

export function DeviceTable({ devices, onRefresh }: DeviceTableProps) {
  async function handleDelete(id: string) {
    if (!confirm("Delete this device?")) return;
    await fetch(`/api/devices/${id}`, { method: "DELETE" });
    onRefresh();
  }

  if (devices.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        No devices found. Add a device to get started.
      </div>
    );
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Type</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Location</TableHead>
            <TableHead>Sensors</TableHead>
            <TableHead className="w-[50px]"></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {devices.map((device) => (
            <TableRow key={device.id}>
              <TableCell className="font-medium">{device.name}</TableCell>
              <TableCell>{device.type}</TableCell>
              <TableCell>
                <DeviceStatusBadge status={device.status} />
              </TableCell>
              <TableCell>
                {device.zone.hospital.name} / {device.zone.name}
              </TableCell>
              <TableCell>{device.sensors.length}</TableCell>
              <TableCell>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => handleDelete(device.id)}
                >
                  <Trash2 className="h-4 w-4 text-destructive" />
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
