"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { DeviceTable } from "@/components/devices/device-table";
import { DeviceForm } from "@/components/devices/device-form";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

export default function DevicesPage() {
  const [devices, setDevices] = useState([]);
  const [zones, setZones] = useState([]);
  const [open, setOpen] = useState(false);

  async function loadDevices() {
    const res = await fetch("/api/devices");
    setDevices(await res.json());
  }

  async function loadZones() {
    const res = await fetch("/api/hospitals");
    const hospitals = await res.json();
    const allZones = hospitals.flatMap((h: any) =>
      h.zones.map((z: any) => ({ ...z, hospitalName: h.name }))
    );
    setZones(allZones);
  }

  useEffect(() => {
    loadDevices();
    loadZones();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Devices</h1>
          <p className="text-muted-foreground">Manage and monitor your devices</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add Device
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add Device</DialogTitle>
            </DialogHeader>
            <DeviceForm
              zones={zones}
              onSuccess={() => {
                setOpen(false);
                loadDevices();
              }}
            />
          </DialogContent>
        </Dialog>
      </div>
      <DeviceTable devices={devices} onRefresh={loadDevices} />
    </div>
  );
}
