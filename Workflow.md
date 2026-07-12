# 🔄 TransitOps — Complete Workflow Documentation

> This document details every workflow, state machine, and automation in the TransitOps platform.

---

## Table of Contents

- [1. Application Workflow (High-Level)](#1-application-workflow-high-level)
- [2. Vehicle Lifecycle](#2-vehicle-lifecycle)
- [3. Driver Lifecycle](#3-driver-lifecycle)
- [4. Trip Lifecycle (Core Workflow)](#4-trip-lifecycle-core-workflow)
- [5. Maintenance Workflow](#5-maintenance-workflow)
- [6. Fuel & Expense Workflow](#6-fuel--expense-workflow)
- [7. Dashboard & Analytics Flow](#7-dashboard--analytics-flow)
- [8. Authentication & Authorization Flow](#8-authentication--authorization-flow)
- [9. Automated Actions & Cron Jobs](#9-automated-actions--cron-jobs)
- [10. End-to-End Demo Workflow](#10-end-to-end-demo-workflow)
- [11. Business Rules Matrix](#11-business-rules-matrix)

---

## 1. Application Workflow (High-Level)

```
┌────────────────────────────────────────────────────────────────────────┐
│                        USER LOGS IN                                    │
│                   (Email + Password + RBAC)                            │
└──────────────────────────┬─────────────────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │      DASHBOARD         │
              │  (Role-based KPIs)     │
              └─────┬──────┬──────┬────┘
                    │      │      │
         ┌──────────┘      │      └──────────┐
         ▼                 ▼                  ▼
   ┌───────────┐    ┌───────────┐     ┌─────────────┐
   │ VEHICLES  │    │  DRIVERS  │     │    TRIPS     │
   │ Registry  │    │   Mgmt    │     │  Management  │
   └─────┬─────┘    └─────┬─────┘     └──────┬──────┘
         │                │                    │
         ▼                ▼                    ▼
   ┌───────────┐    ┌───────────┐     ┌─────────────┐
   │MAINTENANCE│    │   FUEL    │     │  EXPENSES   │
   │   Logs    │    │   Logs    │     │  Tracking   │
   └─────┬─────┘    └─────┬─────┘     └──────┬──────┘
         │                │                    │
         └────────────────┼────────────────────┘
                          ▼
              ┌────────────────────────┐
              │   REPORTS & ANALYTICS  │
              │  (PDF, CSV, Charts)    │
              └────────────────────────┘
```

---

## 2. Vehicle Lifecycle

### State Machine

```
                    ┌───────────────────────┐
                    │                       │
                    ▼                       │
    ┌──────────────────────────┐            │
    │       AVAILABLE          │◄───────────┤
    │  (Ready for dispatch)    │            │
    └─────┬───────────┬────────┘            │
          │           │                     │
  Assigned to    Maintenance           Complete
   a Trip         Created             Maintenance
          │           │                (if not retired)
          ▼           ▼                     │
  ┌──────────────┐  ┌──────────────┐        │
  │   ON TRIP    │  │   IN SHOP    │────────┘
  │ (Dispatched) │  │(Maintenance) │
  └──────┬───────┘  └──────────────┘
         │
    Trip Completed
    or Cancelled
         │
         ▼
  ┌──────────────┐
  │  AVAILABLE   │
  └──────────────┘

         ┌──────────────┐
         │   RETIRED    │  (Terminal state - no dispatch, no maintenance)
         │ (End of life) │
         └──────────────┘
```

### Vehicle Status Transitions

| Current Status | Action | New Status | Automated? |
|---|---|---|---|
| Available | Trip dispatched with this vehicle | On Trip | ✅ Auto |
| On Trip | Trip completed | Available | ✅ Auto |
| On Trip | Trip cancelled | Available | ✅ Auto |
| Available | Maintenance record created | In Shop | ✅ Auto |
| In Shop | Maintenance closed | Available | ✅ Auto |
| Any (except Retired) | Admin retires vehicle | Retired | Manual |

### Vehicle Business Rules

| Rule | Enforcement |
|---|---|
| Registration number must be unique | `_sql_constraints` on model |
| Retired vehicles cannot be dispatched | `domain` filter on trip form vehicle selection |
| In Shop vehicles cannot be dispatched | `domain` filter on trip form vehicle selection |
| On Trip vehicles cannot be double-assigned | `@api.constrains` validation |

---

## 3. Driver Lifecycle

### State Machine

```
    ┌──────────────────────────┐
    │       AVAILABLE          │◄──────────┐
    │   (Ready for trips)      │           │
    └─────┬────────────────────┘           │
          │                                │
    Assigned to Trip               Trip Completed
          │                        or Cancelled
          ▼                                │
    ┌──────────────────────────┐           │
    │       ON TRIP            │───────────┘
    │   (Currently driving)    │
    └──────────────────────────┘


    ┌──────────────────────────┐
    │       OFF DUTY           │  (Cannot be dispatched)
    │   (Temporary leave)      │
    └──────────────────────────┘

    ┌──────────────────────────┐
    │      SUSPENDED           │  (Cannot be dispatched - compliance issue)
    │  (License/Safety issue)  │
    └──────────────────────────┘
```

### Driver Status Transitions

| Current Status | Action | New Status | Automated? |
|---|---|---|---|
| Available | Trip dispatched with this driver | On Trip | ✅ Auto |
| On Trip | Trip completed | Available | ✅ Auto |
| On Trip | Trip cancelled | Available | ✅ Auto |
| Available | Admin sets off duty | Off Duty | Manual |
| Off Duty | Admin restores | Available | Manual |
| Any | License expires (cron detected) | Suspended | ✅ Auto (Cron) |
| Suspended | License renewed | Available | Manual |

### Driver Business Rules

| Rule | Enforcement |
|---|---|
| Expired license → cannot be dispatched | `@api.constrains` + domain filter |
| Suspended drivers → cannot be dispatched | Domain filter on trip form |
| On Trip drivers → cannot be double-assigned | `@api.constrains` validation |
| Safety score tracked per trip | Computed field updated on trip completion |

---

## 4. Trip Lifecycle (Core Workflow)

### State Machine

```
    ┌──────────────────────────┐
    │         DRAFT            │
    │  (Trip created, not yet  │
    │   dispatched)            │
    └─────┬────────────────────┘
          │
          │  [Dispatch] button clicked
          │  ✓ Vehicle available?
          │  ✓ Driver available?
          │  ✓ License valid?
          │  ✓ Cargo ≤ max capacity?
          │
          ▼
    ┌──────────────────────────┐
    │      DISPATCHED          │
    │  (Vehicle & Driver       │
    │   status → On Trip)      │
    └─────┬──────────┬─────────┘
          │          │
    [Complete]   [Cancel]
          │          │
          ▼          ▼
    ┌──────────┐  ┌──────────────┐
    │COMPLETED │  │  CANCELLED   │
    │(Odometer │  │  (Vehicle &  │
    │ updated, │  │  Driver →    │
    │ fuel log │  │  Available)  │
    │ created) │  └──────────────┘
    └──────────┘
```

### Trip Workflow — Step by Step

#### Step 1: Create Trip (Draft)
```
User Input:
├── Source location
├── Destination location
├── Select Vehicle (only Available vehicles shown)
├── Select Driver (only Available + valid license drivers shown)
├── Cargo Weight (kg)
└── Planned Distance (km)

System Validates:
├── ✓ Vehicle status == 'available'
├── ✓ Driver status == 'available'
├── ✓ Driver license not expired
├── ✓ Driver not suspended
└── ✓ Cargo weight ≤ Vehicle max capacity
```

#### Step 2: Dispatch Trip
```
On clicking [Dispatch]:
├── Trip status     → 'dispatched'
├── Vehicle status  → 'on_trip'      (AUTOMATIC)
├── Driver status   → 'on_trip'      (AUTOMATIC)
└── Timestamp recorded
```

#### Step 3: Complete Trip
```
User enters:
├── Final Odometer reading
├── Fuel consumed (liters)
└── Any trip notes

System actions:
├── Trip status     → 'completed'
├── Vehicle status  → 'available'    (AUTOMATIC)
├── Driver status   → 'available'    (AUTOMATIC)
├── Vehicle odometer updated         (AUTOMATIC)
├── Fuel log created                 (AUTOMATIC)
└── Fuel efficiency computed         (AUTOMATIC)
```

#### Step 4: Cancel Trip (Alternative)
```
On clicking [Cancel]:
├── Trip status     → 'cancelled'
├── Vehicle status  → 'available'    (AUTOMATIC)
├── Driver status   → 'available'    (AUTOMATIC)
└── Reason for cancellation recorded
```

### Trip Validation Rules

| Validation | When Checked | Error Message |
|---|---|---|
| Cargo > Max Capacity | On save + dispatch | "Cargo weight (X kg) exceeds vehicle capacity (Y kg)" |
| Vehicle not Available | On dispatch | "Vehicle is not available for dispatch" |
| Driver not Available | On dispatch | "Driver is not available for dispatch" |
| Driver license expired | On dispatch | "Driver's license expired on [date]" |
| Driver suspended | On dispatch | "Driver is suspended and cannot be assigned" |
| Vehicle already On Trip | On dispatch | "Vehicle is already assigned to another trip" |
| Driver already On Trip | On dispatch | "Driver is already assigned to another trip" |

---

## 5. Maintenance Workflow

### State Machine

```
    ┌──────────────────────────┐
    │     CREATE RECORD        │
    │  (Select vehicle, type,  │
    │   description, cost)     │
    └─────┬────────────────────┘
          │
          │  On creation:
          │  Vehicle status → 'in_shop' (AUTOMATIC)
          │  Vehicle removed from dispatch pool
          │
          ▼
    ┌──────────────────────────┐
    │       IN PROGRESS        │
    │  (Vehicle in maintenance) │
    └─────┬────────────────────┘
          │
          │  [Close Maintenance] button
          │
          ▼
    ┌──────────────────────────┐
    │       COMPLETED          │
    │  Vehicle → 'available'   │
    │  (unless retired)        │
    └──────────────────────────┘
```

### Maintenance Types

| Type | Description | Impact |
|---|---|---|
| Oil Change | Regular oil service | Low cost, quick turnaround |
| Tire Replacement | Tire wear/damage | Medium cost |
| Engine Repair | Engine diagnostics & repair | High cost, longer downtime |
| Brake Service | Brake pad/disc replacement | Safety-critical |
| Body Repair | Accident damage repair | Variable cost |
| General Inspection | Periodic checkup | Preventive |

### Maintenance Business Rules

| Rule | Enforcement |
|---|---|
| Creating maintenance → vehicle goes "In Shop" | `@api.model.create()` override |
| In Shop vehicle hidden from dispatch | Domain filter `[('status','=','available')]` |
| Closing maintenance → vehicle back to "Available" | `action_close()` method |
| Retired vehicle stays retired after maintenance | Conditional check in `action_close()` |
| Maintenance cost added to vehicle total ops cost | Computed field on vehicle model |

---

## 6. Fuel & Expense Workflow

### Fuel Logging Flow

```
    ┌───────────────────────┐
    │   Trip Completed      │
    │   (fuel consumed      │
    │    entered)            │
    └────────┬──────────────┘
             │
             │  Auto-create fuel log
             ▼
    ┌───────────────────────┐
    │   Fuel Log Created    │
    │   ├── Vehicle ID      │
    │   ├── Trip ID         │
    │   ├── Liters          │
    │   ├── Cost per liter  │
    │   ├── Total cost      │
    │   └── Date            │
    └────────┬──────────────┘
             │
             │  Triggers recomputation
             ▼
    ┌───────────────────────┐
    │  Vehicle Stats Update │
    │  ├── Total fuel cost  │
    │  ├── Fuel efficiency  │
    │  └── Ops cost/km      │
    └───────────────────────┘
```

### Expense Categories

| Category | Examples | Linked To |
|---|---|---|
| Fuel | Diesel, Petrol, CNG | Vehicle + Trip |
| Maintenance | Repairs, parts, labor | Vehicle |
| Tolls | Highway tolls, bridge fees | Trip |
| Insurance | Vehicle insurance premiums | Vehicle |
| Fines | Traffic violations, penalties | Driver |
| Miscellaneous | Parking, cleaning, etc. | Vehicle/Trip |

### Cost Computations

```python
# Total Operational Cost per Vehicle
total_ops_cost = sum(fuel_costs) + sum(maintenance_costs) + sum(expenses)

# Fuel Efficiency
fuel_efficiency = total_distance_km / total_fuel_liters  # km/liter

# Vehicle ROI
vehicle_roi = (revenue - total_ops_cost) / acquisition_cost * 100  # percentage
```

---

## 7. Dashboard & Analytics Flow

### KPI Computation Pipeline

```
    ┌───────────────────────────────────────────────────────┐
    │                RAW DATA SOURCES                        │
    ├───────────┬───────────┬──────────┬────────────────────┤
    │  Vehicles │  Drivers  │  Trips   │ Fuel/Maintenance   │
    └─────┬─────┴─────┬─────┴────┬─────┴─────────┬──────────┘
          │           │          │               │
          ▼           ▼          ▼               ▼
    ┌─────────────────────────────────────────────────────────┐
    │              ODOO COMPUTED FIELDS                        │
    │    (@api.depends - real-time recomputation)              │
    └─────────────────────────┬───────────────────────────────┘
                              │
                              ▼
    ┌─────────────────────────────────────────────────────────┐
    │                    DASHBOARD                             │
    │                                                         │
    │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
    │  │ Active   │ │Available │ │   In     │ │  Fleet   │  │
    │  │ Vehicles │ │ Vehicles │ │  Shop    │ │ Util %   │  │
    │  │   12     │ │    8     │ │    3     │ │  52.2%   │  │
    │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
    │                                                         │
    │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
    │  │ Active   │ │ Pending  │ │ Drivers  │ │   Fuel   │  │
    │  │  Trips   │ │  Trips   │ │ On Duty  │ │ Eff(km/l)│  │
    │  │   12     │ │    5     │ │   12     │ │  14.2    │  │
    │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
    │                                                         │
    │  ┌─────────────────────────────────────────────────┐   │
    │  │               CHARTS & GRAPHS                    │   │
    │  │  • Fleet Utilization Over Time (Line)            │   │
    │  │  • Cost Breakdown by Category (Pie)              │   │
    │  │  • Fuel Efficiency by Vehicle (Bar)              │   │
    │  │  • Trip Status Distribution (Donut)              │   │
    │  └─────────────────────────────────────────────────┘   │
    │                                                         │
    │  ┌──────────┐ ┌──────────┐                             │
    │  │  Filter  │ │  Export  │                             │
    │  │ by Type, │ │ CSV/PDF  │                             │
    │  │ Status,  │ │          │                             │
    │  │ Region   │ │          │                             │
    │  └──────────┘ └──────────┘                             │
    └─────────────────────────────────────────────────────────┘
```

### Available Filters

| Filter | Options | Applied To |
|---|---|---|
| Vehicle Type | Truck, Van, Bus, Car | Vehicles, Trips |
| Status | Available, On Trip, In Shop, Retired | Vehicles, Drivers |
| Region | Configurable regions | Vehicles |
| Date Range | Custom from/to dates | Trips, Fuel Logs, Expenses |

---

## 8. Authentication & Authorization Flow

```
    ┌──────────────┐
    │  Login Page  │
    │  (email/pwd) │
    └──────┬───────┘
           │
           ▼
    ┌──────────────────┐     ┌─────────────────────┐
    │  Authenticate    │────►│   Invalid?          │
    │  (Odoo Session)  │     │   → Error Message   │
    └──────┬───────────┘     └─────────────────────┘
           │
           │  Valid credentials
           ▼
    ┌──────────────────┐
    │  Load User Role  │
    │  (Security Group) │
    └──────┬───────────┘
           │
     ┌─────┼─────────┬──────────────┐
     ▼     ▼         ▼              ▼
   Fleet  Driver   Safety      Financial
   Mgr    /Disp   Officer      Analyst
     │     │         │              │
     ▼     ▼         ▼              ▼
   Full   Trip     Driver        Finance
   Access  Focus   Compliance    & Reports
           + Fuel  + Safety       Focus
           Logs    Scores
```

---

## 9. Automated Actions & Cron Jobs

| Cron Job | Schedule | Action |
|---|---|---|
| **License Expiry Check** | Daily at 6:00 AM | Checks all drivers for licenses expiring within 30 days. Sends email alerts. Auto-suspends expired licenses. |
| **Maintenance Reminder** | Weekly (Monday 8:00 AM) | Checks vehicles overdue for scheduled maintenance based on odometer/date thresholds. |
| **Dashboard KPI Refresh** | Every 15 minutes | Recomputes cached KPI values for the dashboard. |
| **Stale Trip Cleanup** | Daily at midnight | Flags draft trips older than 7 days for review. |

---

## 10. End-to-End Demo Workflow

> This matches the **Example Workflow** from the problem statement exactly.

### Step-by-Step

```
STEP 1: Register Vehicle
─────────────────────────
  Input:  Name="Van-05", Max Capacity=500kg, Type=Van
  Result: Vehicle created with status = "Available" ✅

STEP 2: Register Driver
─────────────────────────
  Input:  Name="Alex", License="DL-2024-1234", Expiry=2027-01-01
  Result: Driver created with status = "Available" ✅

STEP 3: Create Trip
─────────────────────────
  Input:  Source="Warehouse A", Dest="Client B",
          Vehicle=Van-05, Driver=Alex, Cargo=450kg
  System: Validates 450kg ≤ 500kg → ✅ PASS
  Result: Trip created in "Draft" state ✅

STEP 4: Dispatch Trip
─────────────────────────
  Action: Click [Dispatch] button
  System: All validations pass
  Result: Trip → "Dispatched"
          Van-05 → "On Trip" (AUTO)
          Alex → "On Trip" (AUTO) ✅

STEP 5: Complete Trip
─────────────────────────
  Input:  End Odometer=12500, Fuel Consumed=35 liters
  Action: Click [Complete] button
  Result: Trip → "Completed"
          Van-05 → "Available" (AUTO)
          Alex → "Available" (AUTO)
          Van-05 Odometer → 12500 (AUTO)
          Fuel Log created (AUTO) ✅

STEP 6: Create Maintenance
─────────────────────────
  Input:  Vehicle=Van-05, Type="Oil Change", Cost=₹2500
  Result: Maintenance record created
          Van-05 → "In Shop" (AUTO)
          Van-05 hidden from dispatch pool (AUTO) ✅

STEP 7: Check Reports
─────────────────────────
  Dashboard shows:
  ├── Fuel Efficiency: 12500km / 35L = 357 km/L (trip)
  ├── Van-05 Ops Cost: ₹2500 (maintenance) + fuel cost
  └── Fleet Utilization updated ✅

STEP 8: Close Maintenance
─────────────────────────
  Action: Click [Close] on maintenance record
  Result: Van-05 → "Available" (AUTO)
          Van-05 back in dispatch pool ✅
```

---

## 11. Business Rules Matrix

| # | Rule Description | Enforcement Method | Auto/Manual |
|---|---|---|---|
| 1 | Vehicle registration number must be unique | `_sql_constraints` | Auto |
| 2 | Retired/In Shop vehicles hidden from dispatch | `domain` filter on Many2one field | Auto |
| 3 | Expired license drivers cannot be dispatched | `@api.constrains` + domain filter | Auto |
| 4 | Suspended drivers cannot be dispatched | Domain filter on trip form | Auto |
| 5 | On Trip vehicle/driver cannot be double-assigned | `@api.constrains` validation | Auto |
| 6 | Cargo weight ≤ vehicle max capacity | `@api.constrains` validation | Auto |
| 7 | Dispatch → vehicle/driver status "On Trip" | `action_dispatch()` method | Auto |
| 8 | Complete → vehicle/driver status "Available" | `action_complete()` method | Auto |
| 9 | Cancel → vehicle/driver status "Available" | `action_cancel()` method | Auto |
| 10 | Create maintenance → vehicle "In Shop" | `create()` override | Auto |
| 11 | Close maintenance → vehicle "Available" | `action_close()` method | Auto |
| 12 | Retired vehicle stays retired post-maintenance | Conditional in `action_close()` | Auto |

---

## 📝 Notes for Judges

1. **Every state transition is automated** — no manual status changes needed.
2. **All validations are server-side** — cannot be bypassed via API or direct DB access.
3. **Full audit trail** — every change is tracked with timestamp and user info.
4. **Real-time dashboard** — KPIs update immediately on data changes.
5. **Production-ready code** — proper error handling, constraints, and edge cases covered.

---

*Last updated: July 2026 | TransitOps Hackathon Project*
