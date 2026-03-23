import { NextResponse } from "next/server";
import bcrypt from "bcryptjs";
import { prisma } from "@/lib/prisma";

export async function POST() {
  try {
    // Clear existing data
    await prisma.alert.deleteMany();
    await prisma.alertRule.deleteMany();
    await prisma.sensorReading.deleteMany();
    await prisma.sensor.deleteMany();
    await prisma.device.deleteMany();
    await prisma.zone.deleteMany();
    await prisma.hospital.deleteMany();
    await prisma.user.deleteMany();

    // Create admin user
    const hashedPassword = await bcrypt.hash("password123", 10);
    await prisma.user.create({
      data: {
        email: "admin@hospital.io",
        name: "Admin User",
        password: hashedPassword,
        role: "ADMIN",
      },
    });

    // Create hospitals, zones, devices, sensors, readings, and alert rules
    const h1 = await prisma.hospital.create({
      data: {
        name: "Main Hospital",
        location: "Building A, North Wing",
        description: "Primary medical facility for patient care",
      },
    });

    const h2 = await prisma.hospital.create({
      data: {
        name: "Research Hospital",
        location: "Building B, East Side",
        description: "Experimental treatments and research facility",
      },
    });

    const zoneNames = [
      ["Zone A - Tomatoes", "Zone B - Peppers", "Zone C - Herbs"],
      ["Zone D - Seedlings", "Zone E - Experiments", "Zone F - Propagation"],
    ];

    const sensorConfigs = [
      { type: "TEMPERATURE" as const, unit: "\u00b0C", min: 18, max: 35, base: 24 },
      { type: "HUMIDITY" as const, unit: "%", min: 40, max: 90, base: 65 },
      { type: "SOIL_MOISTURE" as const, unit: "%", min: 20, max: 80, base: 55 },
      { type: "LIGHT" as const, unit: "lux", min: 200, max: 1200, base: 600 },
      { type: "CO2" as const, unit: "ppm", min: 300, max: 1500, base: 800 },
    ];

    for (const [ghIndex, gh] of [h1, h2].entries()) {
      for (const [zIndex, zoneName] of zoneNames[ghIndex].entries()) {
        const zone = await prisma.zone.create({
          data: {
            name: zoneName,
            description: `Zone ${zIndex + 1} of ${gh.name}`,
            hospitalId: gh.id,
          },
        });

        for (let dIdx = 0; dIdx < 2; dIdx++) {
          const device = await prisma.device.create({
            data: {
              name: `Sensor Hub ${zoneName.split(" - ")[0]}-${dIdx + 1}`,
              type: dIdx === 0 ? "ESP32" : "Arduino Nano",
              status: Math.random() > 0.1 ? "ONLINE" : "OFFLINE",
              zoneId: zone.id,
            },
          });

          const deviceSensors = dIdx === 0 ? sensorConfigs.slice(0, 3) : sensorConfigs.slice(3);

          for (const config of deviceSensors) {
            const sensor = await prisma.sensor.create({
              data: {
                name: `${config.type.replace("_", " ")} - ${zoneName}`,
                type: config.type,
                unit: config.unit,
                minValue: config.min,
                maxValue: config.max,
                deviceId: device.id,
              },
            });

            // Create alert rules
            await prisma.alertRule.create({
              data: {
                name: `${config.type} High - ${zoneName}`,
                sensorId: sensor.id,
                condition: "ABOVE",
                threshold: config.max * 0.9,
                severity: "HIGH",
                enabled: true,
              },
            });

            await prisma.alertRule.create({
              data: {
                name: `${config.type} Low - ${zoneName}`,
                sensorId: sensor.id,
                condition: "BELOW",
                threshold: config.min * 1.1,
                severity: "MEDIUM",
                enabled: true,
              },
            });

            // Generate 30 days of readings (every 30 min = 1440 readings)
            const readings = [];
            const now = Date.now();
            for (let i = 0; i < 1440; i++) {
              const timestamp = new Date(now - (1440 - i) * 30 * 60 * 1000);
              const hourOfDay = timestamp.getHours();
              const dayFactor = Math.sin(((hourOfDay - 6) * Math.PI) / 12) * 0.3;
              const noise = (Math.random() - 0.5) * (config.max - config.min) * 0.15;
              const value = Math.max(
                config.min,
                Math.min(config.max, config.base + dayFactor * (config.max - config.min) * 0.3 + noise)
              );

              readings.push({
                sensorId: sensor.id,
                value: Math.round(value * 100) / 100,
                timestamp,
              });
            }

            await prisma.sensorReading.createMany({ data: readings });

            // Create some triggered alerts
            if (Math.random() > 0.5) {
              const alertValue = config.max * (0.9 + Math.random() * 0.15);
              await prisma.alert.create({
                data: {
                  message: `${sensor.name}: value ${alertValue.toFixed(1)} ${config.unit} is above threshold ${(config.max * 0.9).toFixed(1)} ${config.unit}`,
                  severity: "HIGH",
                  value: alertValue,
                  threshold: config.max * 0.9,
                  sensorId: sensor.id,
                  acknowledged: Math.random() > 0.5,
                  createdAt: new Date(now - Math.random() * 24 * 60 * 60 * 1000),
                },
              });
            }
          }
        }
      }
    }

    return NextResponse.json({ success: true, message: "Seed data created successfully" });
  } catch (error) {
    console.error("Seed error:", error);
    return NextResponse.json({ error: "Failed to seed data" }, { status: 500 });
  }
}
