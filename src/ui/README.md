# Bio AIoT Monitor

A real-time dashboard with chatbot for monitoring hospital environments through IoT sensors. Track medical sensors across multiple hospital departments, zones, and wireless devices — with configurable alert rules and analytics.

## Features

- **Dashboard Overview** — Summary cards for hospitals, devices, active alerts, and sensors with recent alert feed and live sensor grid
- **Hospital Management** — CRUD for hospital's department with zone organization and detail views
- **Device Tracking** — Table view of IoT devices (ESP32, Arduino Nano) with online/offline status
- **Sensor Monitoring** — Real-time readings with historical chart visualization per sensor
- **Alert System** — Configurable alert rules (above/below thresholds) with severity levels and acknowledgment workflow
- **Analytics** — Trend charts, stats cards, date range filtering, and CSV export
- **Authentication** — NextAuth credentials provider with role-based access (Admin/Viewer)
- **Responsive Layout** — Sidebar navigation with mobile-friendly sheet menu

## Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Database**: SQLite via Prisma 7 with Better-SQLite3 adapter
- **Auth**: NextAuth.js 4 with credentials provider
- **UI**: shadcn/ui + Radix UI + Tailwind CSS 4
- **Charts**: Recharts
- **Forms**: React Hook Form + Zod validation

## Getting Started

### Prerequisites

- Node.js 20+
- pnpm 8+

### Setup

```bash
# Install dependencies
pnpm install

# Copy environment variables
cp .env.example .env

# Generate NextAuth key
pnpm dlx auth secret

# Demo admin user test
npx tsx scripts/seed-admin.ts

# Generate Prisma client and run migrations
pnpm dlx prisma generate
pnpm dlx prisma db push

# Start the dev server
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) to view the app.

### Seed Data

To populate the database with sample hospitals, devices, sensors, and 30 days of readings:

```bash
curl -X POST http://localhost:3000/api/seed
```

This creates:
- 2 hospital departments with 3 zones each
- 12 devices (ESP32 and Arduino Nano)
- 30 sensors (temperature, humidity, light, CO2)
- ~43,000 sensor readings (30 days at 30-minute intervals)
- Alert rules and sample triggered alerts
- Admin user: `admin@hospital.io` / `password123`

## Project Structure

```
src/
├── app/
│   ├── (auth)/              # Login and registration pages
│   ├── (dashboard)/         # Protected dashboard routes
│   │   ├── alerts/          # Alert management
│   │   ├── analytics/       # Trend charts and CSV export
│   │   ├── devices/         # Device table view
│   │   ├── hospitals/     # Hospital CRUD and detail views
│   │   ├── sensors/         # Sensor monitoring and charts
│   │   └── settings/        # User settings
│   └── api/                 # REST API routes
├── components/
│   ├── alerts/              # Alert banner, table, rule form
│   ├── analytics/           # Trend chart, stats, date picker, export
│   ├── devices/             # Device table, form, status badge
│   ├── hospitals/         # Hospital card and form
│   ├── layout/              # Sidebar, header, mobile nav
│   ├── sensors/             # Sensor card, chart, grid
│   └── ui/                  # shadcn/ui component library
├── lib/                     # Auth config, Prisma client, utilities
└── types/                   # NextAuth type extensions
```

## Data Model

```
Hospital department → Zone → Device → Sensor → SensorReading
                                    → AlertRule
                                    → Alert
```

Each department in hospitals contains zones, which contain devices. Devices have sensors that produce readings. Sensors can have alert rules that trigger alerts when thresholds are exceeded.
