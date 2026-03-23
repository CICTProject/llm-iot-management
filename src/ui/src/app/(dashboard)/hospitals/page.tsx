"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { HospitalCard } from "@/components/hospitals/hospital-card";
import { HospitalForm } from "@/components/hospitals/hospital-form";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

interface Hospital {
  id: string;
  name: string;
  location: string;
  description: string | null;
  zones: { id: string; devices: { id: string; sensors: { id: string }[] }[] }[];
}

export default function HospitalsPage() {
  const [hospitals, setHospitals] = useState<Hospital[]>([]);
  const [open, setOpen] = useState(false);

  async function loadHospitals() {
    const res = await fetch("/api/hospitals");
    const data = await res.json();
    setHospitals(data);
  }

  useEffect(() => {
    loadHospitals();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Hospitals</h1>
          <p className="text-muted-foreground">Manage your hospitals and zones</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add Hospital
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add Hospital</DialogTitle>
            </DialogHeader>
            <HospitalForm
              onSuccess={() => {
                setOpen(false);
                loadHospitals();
              }}
            />
          </DialogContent>
        </Dialog>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {hospitals.map((hospital) => (
          <HospitalCard key={hospital.id} hospital={hospital} />
        ))}
      </div>
      {hospitals.length === 0 && (
        <div className="text-center py-12 text-muted-foreground">
          No hospital departments yet. Add your first hospital department to get started.
        </div>
      )}
    </div>
  );
}
