# 🚛 TransitOps — Smart Transport Operations Platform

<div align="center">

![TransitOps](https://img.shields.io/badge/TransitOps-Smart%20Fleet%20Management-0066FF?style=for-the-badge&logo=truck&logoColor=white)
![Odoo](https://img.shields.io/badge/Built%20With-Odoo%2018-714B67?style=for-the-badge&logo=odoo&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-LGPL--3-green?style=for-the-badge)

**A centralized fleet & transport operations platform that digitizes vehicle, driver, dispatch, maintenance, and expense management with enforced business rules and real-time operational insights.**

[Problem Statement](#-problem-statement) • [Solution Architecture](#-solution-architecture) • [Features](#-features) • [Tech Stack](#-tech-stack) • [Quick Start](#-quick-start) • [API](#-api-endpoints) • [Team](#-team)

</div>

---

## 📋 Problem Statement

Logistics companies still rely on **spreadsheets and manual logbooks** to manage transport operations, leading to:

| Pain Point | Business Impact |
|---|---|
| 🔴 Scheduling conflicts | Missed deliveries, SLA violations |
| 🔴 Underutilized vehicles | Wasted CAPEX, low fleet ROI |
| 🔴 Missed maintenance | Breakdowns, safety hazards |
| 🔴 Expired driver licenses | Legal liability, compliance risk |
| 🔴 Inaccurate expense tracking | Budget overruns, profit leaks |
| 🔴 Poor operational visibility | Delayed decisions, no forecasting |

**TransitOps** solves ALL of these by providing a **single-pane-of-glass** platform for end-to-end fleet operations.

---

## 🧠 Why This Solution Wins (Hackathon Strategy)

> **As a 30+ hackathon winner, here's the strategic thinking behind every architectural decision:**

### 🎯 Key Differentiators

1. **Odoo as the Platform** — Instead of building from scratch, we leverage Odoo 18's mature framework to get authentication, RBAC, ORM, reporting, and a beautiful UI out of the box. This lets us focus 100% on business logic and domain-specific features.

2. **Event-Driven Status Machine** — All status transitions (Vehicle, Driver, Trip) are enforced via Odoo's `onchange`, `constrains`, and `write` overrides — making the system **self-healing** and **tamper-proof**.

3. **Automated Business Rules as Code** — Every mandatory rule from the problem statement is a Python `@api.constrains` decorator or an overridden `write`/`create` method. Zero manual enforcement needed.

4. **Real-Time KPI Dashboard** — Not just static numbers — live-computed KPIs using Odoo's `compute` fields with `store=True` for performance.

5. **Full Audit Trail** — Odoo's built-in `mail.thread` mixin gives us automatic tracking of every field change, status transition, and user action.

6. **One-Click PDF Reports** — Leveraging Odoo's QWeb report engine for professional PDF exports of trips, maintenance logs, and analytics.

7. **Modular Architecture** — Each domain (vehicles, drivers, trips, maintenance, fuel) is a separate Odoo model but interconnected via relational fields and automated actions.

---

## 🏗 Solution Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TransitOps Platform                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Vehicle  │  │  Driver  │  │   Trip   │  │Dashboard │   │
│  │ Registry │  │  Mgmt    │  │  Mgmt    │  │  & KPIs  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │              │              │              │         │
│  ┌────┴──────────────┴──────────────┴──────────────┴─────┐  │
│  │           Business Rules Engine (Python)               │  │
│  │  • Status Machine  • Validation  • Auto-Transitions    │  │
│  └────┬──────────────────────────────────────────────┬───┘  │
│       │                                              │       │
│  ┌────┴─────┐  ┌──────────┐  ┌──────────┐  ┌───────┴────┐ │
│  │Mainten-  │  │  Fuel &  │  │ Reports  │  │   RBAC &   │ │
│  │  ance    │  │ Expenses │  │& Analytics│  │   Auth     │ │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘ │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Odoo 18 Framework (ORM • QWeb • REST API • Mail Thread)    │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL 15+                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### ✅ Mandatory Deliverables (All Implemented)

| # | Feature | Status | Details |
|---|---------|--------|---------|
| 1 | **Responsive Web Interface** | ✅ | Odoo's OWL-based responsive UI |
| 2 | **Authentication + RBAC** | ✅ | 4 roles: Fleet Manager, Driver, Safety Officer, Financial Analyst |
| 3 | **Vehicle CRUD** | ✅ | Registration, type, capacity, odometer, cost, status tracking |
| 4 | **Driver CRUD** | ✅ | Profiles, license tracking, safety scores, status management |
| 5 | **Trip Management** | ✅ | Full lifecycle: Draft → Dispatched → Completed → Cancelled |
| 6 | **Auto Status Transitions** | ✅ | Vehicle & Driver status auto-update on dispatch/complete/cancel |
| 7 | **Maintenance Workflow** | ✅ | Auto "In Shop" status, dispatch pool removal, restore on close |
| 8 | **Fuel & Expense Tracking** | ✅ | Fuel logs, tolls, misc expenses, auto cost computation |
| 9 | **Dashboard with KPIs** | ✅ | Active/Available vehicles, trips, drivers, fleet utilization % |
| 10 | **Charts & Visual Analytics** | ✅ | Fuel efficiency, fleet utilization, cost breakdowns |

### 🌟 Bonus Features

| # | Feature | Status | Details |
|---|---------|--------|---------|
| 1 | **PDF Export** | ✅ | QWeb-based professional PDF reports |
| 2 | **Email Reminders** | ✅ | Automated alerts for expiring driver licenses |
| 3 | **Vehicle Document Management** | ✅ | Attach insurance, registration, permits to vehicles |
| 4 | **Search, Filters & Sorting** | ✅ | Advanced search domains on all list views |
| 5 | **Dark Mode** | ✅ | Odoo 18 native dark mode support |
| 6 | **CSV Export** | ✅ | One-click CSV export on all list views |

### 🚀 Extra Features (Hackathon Edge)

| # | Feature | Details |
|---|---------|---------|
| 1 | **Audit Trail** | Full change tracking via `mail.thread` on all models |
| 2 | **Smart Filters** | Pre-built filters: "Expiring Licenses", "Low Safety Score", "High Cost Vehicles" |
| 3 | **Kanban Views** | Visual kanban boards for trips and maintenance |
| 4 | **Scheduled Actions** | Cron jobs for license expiry checks and maintenance reminders |
| 5 | **Vehicle ROI Calculator** | Auto-computed ROI = (Revenue − (Maintenance + Fuel)) / Acquisition Cost |
| 6 | **Color-Coded Status** | Visual status indicators across all views |

---

## 🛠 Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Framework** | Odoo 18 (Community) | Mature ERP framework with built-in auth, ORM, views, reporting |
| **Backend** | Python 3.10+ | Odoo's server-side language, clean & readable |
| **Frontend** | OWL (Odoo Web Library) + QWeb | Component-based reactive UI framework |
| **Database** | PostgreSQL 15+ | Robust RDBMS with full ACID compliance |
| **Reporting** | QWeb Templates | Server-side PDF/HTML report generation |
| **API** | Odoo JSON-RPC / REST | Built-in API for external integrations |
| **Cron** | Odoo Scheduled Actions | For license expiry checks, maintenance alerts |

---

## 📁 Project Structure

```
transitops/
├── __init__.py
├── __manifest__.py              # Module manifest (metadata, dependencies, data files)
├── models/
│   ├── __init__.py
│   ├── transit_vehicle.py       # Vehicle Registry model
│   ├── transit_driver.py        # Driver Management model
│   ├── transit_trip.py          # Trip Management model
│   ├── transit_maintenance.py   # Maintenance Logs model
│   ├── transit_fuel_log.py      # Fuel Logging model
│   ├── transit_expense.py       # Expense Tracking model
│   └── transit_dashboard.py     # Dashboard KPI computations
├── views/
│   ├── vehicle_views.xml        # Vehicle list, form, kanban, search views
│   ├── driver_views.xml         # Driver views
│   ├── trip_views.xml           # Trip views with lifecycle buttons
│   ├── maintenance_views.xml    # Maintenance views
│   ├── fuel_log_views.xml       # Fuel log views
│   ├── expense_views.xml        # Expense views
│   ├── dashboard_views.xml      # Dashboard with KPIs & charts
│   └── menu_views.xml           # Menu structure & navigation
├── security/
│   ├── ir.model.access.csv      # Access control lists per role
│   └── transit_security.xml     # Security groups & record rules
├── data/
│   ├── demo_data.xml            # Sample vehicles, drivers, trips
│   ├── scheduled_actions.xml    # Cron jobs (license expiry, reminders)
│   └── email_templates.xml      # Email templates for notifications
├── reports/
│   ├── trip_report.xml          # Trip PDF report template
│   ├── vehicle_report.xml       # Vehicle status report
│   ├── maintenance_report.xml   # Maintenance history report
│   └── analytics_report.xml    # Analytics & cost report
├── static/
│   └── description/
│       └── icon.png             # Module icon
└── README.md
```

---

## 🗄 Database Schema (Entity Relationship)

```
┌──────────────────┐     ┌──────────────────┐
│  transit.vehicle  │     │  transit.driver   │
├──────────────────┤     ├──────────────────┤
│ id               │     │ id               │
│ name             │     │ name             │
│ registration_no  │◄──┐ │ license_number   │
│ vehicle_type     │   │ │ license_category │
│ max_capacity     │   │ │ license_expiry   │
│ odometer         │   │ │ contact_number   │
│ acquisition_cost │   │ │ safety_score     │
│ status           │   │ │ status           │
│ region           │   │ └──────┬───────────┘
└──────┬───────────┘   │        │
       │               │        │
       ▼               │        ▼
┌──────────────────┐   │ ┌──────────────────┐
│transit.maintenance│   │ │  transit.trip     │
├──────────────────┤   │ ├──────────────────┤
│ id               │   │ │ id               │
│ vehicle_id  ─────┼───┘ │ vehicle_id       │
│ maintenance_type │     │ driver_id        │
│ description      │     │ source           │
│ cost             │     │ destination      │
│ start_date       │     │ cargo_weight     │
│ end_date         │     │ planned_distance │
│ status           │     │ actual_distance  │
└──────────────────┘     │ fuel_consumed    │
                         │ status (lifecycle)│
       ┌─────────────────┤ start_odometer   │
       │                 │ end_odometer     │
       ▼                 └──────────────────┘
┌──────────────────┐
│ transit.fuel.log │     ┌──────────────────┐
├──────────────────┤     │ transit.expense  │
│ id               │     ├──────────────────┤
│ vehicle_id       │     │ id               │
│ trip_id          │     │ vehicle_id       │
│ liters           │     │ trip_id          │
│ cost             │     │ expense_type     │
│ date             │     │ amount           │
└──────────────────┘     │ date             │
                         │ description      │
                         └──────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 15+
- Odoo 18 Community Edition
- Git

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-team/transitops.git

# 2. Navigate to your Odoo addons directory
cp -r transitops /path/to/odoo/addons/

# 3. Update Odoo module list
python odoo-bin -c odoo.conf -u transitops -d your_database

# 4. Restart Odoo server
python odoo-bin -c odoo.conf

# 5. Go to Apps → Search "TransitOps" → Install
```

### Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Fleet Manager | fleet@transitops.com | fleet123 |
| Driver / Dispatcher | driver@transitops.com | driver123 |
| Safety Officer | safety@transitops.com | safety123 |
| Financial Analyst | finance@transitops.com | finance123 |

---

## 🔐 Role-Based Access Control

| Permission | Fleet Manager | Driver/Dispatcher | Safety Officer | Financial Analyst |
|------------|:---:|:---:|:---:|:---:|
| Dashboard (View) | ✅ | ✅ | ✅ | ✅ |
| Vehicle CRUD | ✅ | 👁 Read | 👁 Read | 👁 Read |
| Driver CRUD | ✅ | 👁 Read | ✅ | 👁 Read |
| Trip CRUD | ✅ | ✅ | 👁 Read | 👁 Read |
| Maintenance CRUD | ✅ | 👁 Read | 👁 Read | 👁 Read |
| Fuel & Expenses | ✅ | ✅ Create | 👁 Read | ✅ |
| Reports & Analytics | ✅ | ❌ | ✅ | ✅ |
| User Management | ✅ | ❌ | ❌ | ❌ |

---

## 📊 Business Rules Enforcement

All mandatory business rules are enforced at the **model level** (not UI), ensuring data integrity regardless of access method:

```python
# Example: Cargo weight validation
@api.constrains('cargo_weight', 'vehicle_id')
def _check_cargo_weight(self):
    for trip in self:
        if trip.cargo_weight > trip.vehicle_id.max_capacity:
            raise ValidationError(
                f"Cargo weight ({trip.cargo_weight} kg) exceeds "
                f"vehicle capacity ({trip.vehicle_id.max_capacity} kg)!"
            )

# Example: Auto status transition on dispatch
def action_dispatch(self):
    self.ensure_one()
    self.vehicle_id.status = 'on_trip'
    self.driver_id.status = 'on_trip'
    self.state = 'dispatched'
```

---

## 📈 KPI Dashboard Metrics

| KPI | Computation |
|-----|-------------|
| **Active Vehicles** | Count where status = 'on_trip' |
| **Available Vehicles** | Count where status = 'available' |
| **In Maintenance** | Count where status = 'in_shop' |
| **Active Trips** | Count where state = 'dispatched' |
| **Pending Trips** | Count where state = 'draft' |
| **Drivers On Duty** | Count where status = 'on_trip' |
| **Fleet Utilization %** | (Active Vehicles / Total Non-Retired) × 100 |
| **Fuel Efficiency** | Total Distance / Total Fuel Consumed |
| **Vehicle ROI** | (Revenue − (Maintenance + Fuel)) / Acquisition Cost |

---

## 🧪 Testing the Workflow

Follow the **Example Workflow** from the problem statement:

1. **Register Vehicle** → Create 'Van-05', capacity 500 kg, status = Available
2. **Register Driver** → Create 'Alex' with valid license
3. **Create Trip** → Cargo weight = 450 kg (system validates ≤ 500 kg ✅)
4. **Dispatch Trip** → Vehicle & Driver auto-switch to "On Trip"
5. **Complete Trip** → Enter final odometer + fuel → both reset to "Available"
6. **Create Maintenance** → Oil Change → Vehicle auto-switches to "In Shop"
7. **Check Reports** → Operational cost and fuel efficiency update automatically

---

## 📄 License

This project is licensed under the **LGPL-3.0 License** — see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

Built with ❤️ for the Odoo Hackathon

---

<div align="center">

**⭐ If you found this useful, give us a star! ⭐**

*TransitOps — Because your fleet deserves better than a spreadsheet.*

</div>
