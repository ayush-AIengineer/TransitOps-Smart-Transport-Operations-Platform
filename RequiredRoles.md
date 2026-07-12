# 🔐 TransitOps — Required Roles & Access Control

> Complete documentation of all user roles, security groups, permissions, and access control rules.

---

## Table of Contents

- [1. Role Overview](#1-role-overview)
- [2. Security Group Hierarchy](#2-security-group-hierarchy)
- [3. Detailed Role Definitions](#3-detailed-role-definitions)
- [4. Access Control Matrix (ir.model.access.csv)](#4-access-control-matrix-irmodelaccesscsv)
- [5. Record Rules](#5-record-rules)
- [6. Menu Visibility per Role](#6-menu-visibility-per-role)
- [7. Button & Action Visibility](#7-button--action-visibility)
- [8. Field-Level Access](#8-field-level-access)
- [9. Implementation in Odoo](#9-implementation-in-odoo)
- [10. Demo User Setup](#10-demo-user-setup)
- [11. Role Assignment Workflow](#11-role-assignment-workflow)

---

## 1. Role Overview

TransitOps defines **4 distinct roles** as specified in the problem statement, plus an **Admin** superuser role:

| Role | Code Name | Primary Responsibility | Target User |
|------|-----------|----------------------|-------------|
| 🔵 **Fleet Manager** | `transit_fleet_manager` | Full system control — vehicles, maintenance, fleet lifecycle, operational efficiency | Operations Head, Fleet Supervisor |
| 🟢 **Driver / Dispatcher** | `transit_driver` | Create and manage trips, assign vehicles and drivers, log fuel and expenses | Dispatch Coordinator, Driver Supervisor |
| 🟠 **Safety Officer** | `transit_safety_officer` | Driver compliance, license validity tracking, safety score monitoring | HSE Manager, Compliance Officer |
| 🟣 **Financial Analyst** | `transit_financial_analyst` | Operational expenses, fuel costs, maintenance costs, profitability analysis | Finance Manager, Accounts Head |
| 🔴 **Admin** | `base.group_system` | Full system access including user management and module configuration | IT Admin |

---

## 2. Security Group Hierarchy

```
base.group_user (Internal User)
│
├── transit.group_transit_user (TransitOps User - Base Access)
│   │
│   ├── transit.group_transit_driver (Driver / Dispatcher)
│   │   • Trip CRUD
│   │   • Fuel/Expense Create
│   │   • Vehicle/Driver Read
│   │
│   ├── transit.group_transit_safety (Safety Officer)
│   │   • Driver CRUD
│   │   • Vehicle/Trip Read
│   │   • Reports Read
│   │   • Safety Score Management
│   │
│   ├── transit.group_transit_finance (Financial Analyst)
│   │   • Expense CRUD
│   │   • Fuel Log CRUD
│   │   • Reports Full Access
│   │   • Vehicle/Driver/Trip Read
│   │
│   └── transit.group_transit_manager (Fleet Manager)
│       • FULL CRUD on all models
│       • User Management
│       • Configuration Access
│       • All Reports
│       (inherits all lower-level permissions)
│
└── base.group_system (Admin)
    • Module installation
    • Security configuration
    • Database management
```

### Inheritance Chain

```
Fleet Manager ─── inherits ──→ TransitOps User (base)
Driver/Dispatcher ─── inherits ──→ TransitOps User (base)
Safety Officer ─── inherits ──→ TransitOps User (base)
Financial Analyst ─── inherits ──→ TransitOps User (base)
```

> **Note**: Fleet Manager does NOT inherit from Driver/Safety/Finance. Each role gets its own permissions independently to ensure clean separation of concerns. Fleet Manager gets full access via its own ACL entries.

---

## 3. Detailed Role Definitions

### 🔵 Fleet Manager (`transit.group_transit_manager`)

**Who**: Operations Manager, Fleet Supervisor, Transport Head

**Primary Responsibilities**:
- Oversee all fleet assets and their lifecycle
- Manage vehicle maintenance schedules
- Monitor operational efficiency metrics
- Manage user access within the module
- Configure system settings

**Access Level**: **Full CRUD** on all TransitOps models

| Capability | Access |
|---|---|
| Vehicle Registry | ✅ Create, Read, Update, Delete |
| Driver Management | ✅ Create, Read, Update, Delete |
| Trip Management | ✅ Create, Read, Update, Delete |
| Maintenance Logs | ✅ Create, Read, Update, Delete |
| Fuel Logs | ✅ Create, Read, Update, Delete |
| Expenses | ✅ Create, Read, Update, Delete |
| Dashboard | ✅ Full Access (all KPIs) |
| Reports & Analytics | ✅ Full Access + Export |
| User Management | ✅ Assign roles within TransitOps |
| System Configuration | ✅ Module settings |

---

### 🟢 Driver / Dispatcher (`transit.group_transit_driver`)

**Who**: Dispatch Coordinator, Driver Supervisor, Route Planner

**Primary Responsibilities**:
- Create and manage trip dispatches
- Assign available vehicles and drivers to trips
- Monitor active deliveries in real-time
- Log fuel consumption and trip expenses

**Access Level**: **Trip-Focused** with supporting read access

| Capability | Access |
|---|---|
| Vehicle Registry | 👁 Read Only |
| Driver Management | 👁 Read Only |
| Trip Management | ✅ Create, Read, Update (own trips) |
| Maintenance Logs | 👁 Read Only |
| Fuel Logs | ✅ Create, Read (linked to own trips) |
| Expenses | ✅ Create, Read (linked to own trips) |
| Dashboard | ✅ View (trip-focused KPIs) |
| Reports & Analytics | ❌ No Access |
| User Management | ❌ No Access |
| System Configuration | ❌ No Access |

**Restrictions**:
- Cannot modify vehicle or driver master data
- Cannot delete trips (only cancel via workflow)
- Cannot access financial reports
- Cannot manage maintenance records

---

### 🟠 Safety Officer (`transit.group_transit_safety`)

**Who**: Health, Safety & Environment (HSE) Manager, Compliance Officer

**Primary Responsibilities**:
- Ensure all active drivers have valid licenses
- Monitor driver safety scores
- Track license expiry dates and send alerts
- Suspend non-compliant drivers
- Review trip safety data

**Access Level**: **Driver-Compliance Focused**

| Capability | Access |
|---|---|
| Vehicle Registry | 👁 Read Only |
| Driver Management | ✅ Create, Read, Update (compliance fields) |
| Trip Management | 👁 Read Only |
| Maintenance Logs | 👁 Read Only |
| Fuel Logs | 👁 Read Only |
| Expenses | 👁 Read Only |
| Dashboard | ✅ View (safety-focused KPIs) |
| Reports & Analytics | ✅ Read + Export (safety reports) |
| User Management | ❌ No Access |
| System Configuration | ❌ No Access |

**Special Permissions**:
- Can update driver `status` field (suspend/reinstate)
- Can update driver `safety_score`
- Can update driver license fields
- Cannot modify trip states or vehicle data

---

### 🟣 Financial Analyst (`transit.group_transit_finance`)

**Who**: Finance Manager, Accounts Head, Cost Controller

**Primary Responsibilities**:
- Review and analyze operational expenses
- Track fuel consumption costs across the fleet
- Monitor maintenance spending
- Compute profitability and ROI per vehicle
- Generate financial reports and exports

**Access Level**: **Finance & Analytics Focused**

| Capability | Access |
|---|---|
| Vehicle Registry | 👁 Read Only |
| Driver Management | 👁 Read Only |
| Trip Management | 👁 Read Only |
| Maintenance Logs | 👁 Read Only (cost data focus) |
| Fuel Logs | ✅ Create, Read, Update |
| Expenses | ✅ Create, Read, Update, Delete |
| Dashboard | ✅ View (financial KPIs) |
| Reports & Analytics | ✅ Full Access + Export (CSV/PDF) |
| User Management | ❌ No Access |
| System Configuration | ❌ No Access |

**Special Permissions**:
- Full access to expense and fuel cost data
- Can generate and export financial reports
- Can view ROI and cost breakdown analytics
- Cannot modify vehicle/driver/trip operational data

---

## 4. Access Control Matrix (ir.model.access.csv)

This is the exact Odoo ACL file format:

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
# ═══════════════════════════════════════════════════════════
# FLEET MANAGER - Full Access to Everything
# ═══════════════════════════════════════════════════════════
access_vehicle_manager,transit.vehicle.manager,model_transit_vehicle,transit.group_transit_manager,1,1,1,1
access_driver_manager,transit.driver.manager,model_transit_driver,transit.group_transit_manager,1,1,1,1
access_trip_manager,transit.trip.manager,model_transit_trip,transit.group_transit_manager,1,1,1,1
access_maintenance_manager,transit.maintenance.manager,model_transit_maintenance,transit.group_transit_manager,1,1,1,1
access_fuel_log_manager,transit.fuel.log.manager,model_transit_fuel_log,transit.group_transit_manager,1,1,1,1
access_expense_manager,transit.expense.manager,model_transit_expense,transit.group_transit_manager,1,1,1,1

# ═══════════════════════════════════════════════════════════
# DRIVER / DISPATCHER - Trip Focus + Supporting Read
# ═══════════════════════════════════════════════════════════
access_vehicle_driver,transit.vehicle.driver,model_transit_vehicle,transit.group_transit_driver,1,0,0,0
access_driver_driver,transit.driver.driver,model_transit_driver,transit.group_transit_driver,1,0,0,0
access_trip_driver,transit.trip.driver,model_transit_trip,transit.group_transit_driver,1,1,1,0
access_maintenance_driver,transit.maintenance.driver,model_transit_maintenance,transit.group_transit_driver,1,0,0,0
access_fuel_log_driver,transit.fuel.log.driver,model_transit_fuel_log,transit.group_transit_driver,1,0,1,0
access_expense_driver,transit.expense.driver,model_transit_expense,transit.group_transit_driver,1,0,1,0

# ═══════════════════════════════════════════════════════════
# SAFETY OFFICER - Driver Compliance Focus
# ═══════════════════════════════════════════════════════════
access_vehicle_safety,transit.vehicle.safety,model_transit_vehicle,transit.group_transit_safety,1,0,0,0
access_driver_safety,transit.driver.safety,model_transit_driver,transit.group_transit_safety,1,1,1,0
access_trip_safety,transit.trip.safety,model_transit_trip,transit.group_transit_safety,1,0,0,0
access_maintenance_safety,transit.maintenance.safety,model_transit_maintenance,transit.group_transit_safety,1,0,0,0
access_fuel_log_safety,transit.fuel.log.safety,model_transit_fuel_log,transit.group_transit_safety,1,0,0,0
access_expense_safety,transit.expense.safety,model_transit_expense,transit.group_transit_safety,1,0,0,0

# ═══════════════════════════════════════════════════════════
# FINANCIAL ANALYST - Expense & Analytics Focus
# ═══════════════════════════════════════════════════════════
access_vehicle_finance,transit.vehicle.finance,model_transit_vehicle,transit.group_transit_finance,1,0,0,0
access_driver_finance,transit.driver.finance,model_transit_driver,transit.group_transit_finance,1,0,0,0
access_trip_finance,transit.trip.finance,model_transit_trip,transit.group_transit_finance,1,0,0,0
access_maintenance_finance,transit.maintenance.finance,model_transit_maintenance,transit.group_transit_finance,1,0,0,0
access_fuel_log_finance,transit.fuel.log.finance,model_transit_fuel_log,transit.group_transit_finance,1,1,1,0
access_expense_finance,transit.expense.finance,model_transit_expense,transit.group_transit_finance,1,1,1,1
```

### Permission Legend

| Code | Meaning |
|---|---|
| `1,1,1,1` | Read, Write, Create, Delete (Full CRUD) |
| `1,1,1,0` | Read, Write, Create (No Delete) |
| `1,0,1,0` | Read, Create (No Edit, No Delete) |
| `1,0,0,0` | Read Only |
| `0,0,0,0` | No Access |

---

## 5. Record Rules

Record rules add **row-level security** on top of model-level ACLs:

### Driver/Dispatcher — Own Trips Only

```xml
<record id="rule_trip_driver_own" model="ir.rule">
    <field name="name">Driver: Own Trips Only</field>
    <field name="model_id" ref="model_transit_trip"/>
    <field name="groups" eval="[(4, ref('transit.group_transit_driver'))]"/>
    <field name="domain_force">[('create_uid', '=', user.id)]</field>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="False"/>
</record>
```

### Financial Analyst — All Records Read, Own Expenses Write

```xml
<record id="rule_expense_finance" model="ir.rule">
    <field name="name">Finance: Full Expense Access</field>
    <field name="model_id" ref="model_transit_expense"/>
    <field name="groups" eval="[(4, ref('transit.group_transit_finance'))]"/>
    <field name="domain_force">[(1, '=', 1)]</field>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="True"/>
</record>
```

### Fleet Manager — Global Access (No Restrictions)

```xml
<record id="rule_global_manager" model="ir.rule">
    <field name="name">Manager: Global Access</field>
    <field name="model_id" ref="model_transit_trip"/>
    <field name="groups" eval="[(4, ref('transit.group_transit_manager'))]"/>
    <field name="domain_force">[(1, '=', 1)]</field>
</record>
```

---

## 6. Menu Visibility per Role

| Menu Item | Fleet Manager | Driver/Dispatcher | Safety Officer | Financial Analyst |
|---|:---:|:---:|:---:|:---:|
| **TransitOps** (root) | ✅ | ✅ | ✅ | ✅ |
| ├── **Dashboard** | ✅ | ✅ | ✅ | ✅ |
| ├── **Vehicles** | ✅ | ✅ (read) | ✅ (read) | ✅ (read) |
| │   ├── Vehicle List | ✅ | ✅ | ✅ | ✅ |
| │   └── Vehicle Documents | ✅ | ❌ | ❌ | ❌ |
| ├── **Drivers** | ✅ | ✅ (read) | ✅ | ✅ (read) |
| │   ├── Driver List | ✅ | ✅ | ✅ | ✅ |
| │   └── License Tracking | ✅ | ❌ | ✅ | ❌ |
| ├── **Trips** | ✅ | ✅ | ✅ (read) | ✅ (read) |
| │   ├── All Trips | ✅ | ✅ | ✅ | ✅ |
| │   └── Create Trip | ✅ | ✅ | ❌ | ❌ |
| ├── **Maintenance** | ✅ | ✅ (read) | ✅ (read) | ✅ (read) |
| ├── **Finance** | ✅ | ✅ (limited) | ✅ (read) | ✅ |
| │   ├── Fuel Logs | ✅ | ✅ | ✅ (read) | ✅ |
| │   └── Expenses | ✅ | ✅ (create) | ✅ (read) | ✅ |
| ├── **Reports** | ✅ | ❌ | ✅ | ✅ |
| │   ├── Fleet Report | ✅ | ❌ | ❌ | ✅ |
| │   ├── Safety Report | ✅ | ❌ | ✅ | ❌ |
| │   ├── Cost Report | ✅ | ❌ | ❌ | ✅ |
| │   └── Export (CSV/PDF) | ✅ | ❌ | ✅ | ✅ |
| └── **Configuration** | ✅ | ❌ | ❌ | ❌ |

---

## 7. Button & Action Visibility

| Button/Action | Fleet Manager | Driver/Dispatcher | Safety Officer | Financial Analyst |
|---|:---:|:---:|:---:|:---:|
| **Vehicle Form** | | | | |
| Create Vehicle | ✅ | ❌ | ❌ | ❌ |
| Edit Vehicle | ✅ | ❌ | ❌ | ❌ |
| Retire Vehicle | ✅ | ❌ | ❌ | ❌ |
| **Driver Form** | | | | |
| Create Driver | ✅ | ❌ | ✅ | ❌ |
| Suspend Driver | ✅ | ❌ | ✅ | ❌ |
| Reinstate Driver | ✅ | ❌ | ✅ | ❌ |
| **Trip Form** | | | | |
| Create Trip | ✅ | ✅ | ❌ | ❌ |
| Dispatch Trip | ✅ | ✅ | ❌ | ❌ |
| Complete Trip | ✅ | ✅ | ❌ | ❌ |
| Cancel Trip | ✅ | ✅ | ❌ | ❌ |
| **Maintenance Form** | | | | |
| Create Maintenance | ✅ | ❌ | ❌ | ❌ |
| Close Maintenance | ✅ | ❌ | ❌ | ❌ |
| **Reports** | | | | |
| Export CSV | ✅ | ❌ | ✅ | ✅ |
| Export PDF | ✅ | ❌ | ✅ | ✅ |

---

## 8. Field-Level Access

Certain sensitive fields have restricted write access:

### Vehicle Model

| Field | Fleet Manager | Driver/Dispatcher | Safety Officer | Financial Analyst |
|---|:---:|:---:|:---:|:---:|
| `registration_no` | ✏️ Write | 👁 Read | 👁 Read | 👁 Read |
| `name` | ✏️ Write | 👁 Read | 👁 Read | 👁 Read |
| `vehicle_type` | ✏️ Write | 👁 Read | 👁 Read | 👁 Read |
| `max_capacity` | ✏️ Write | 👁 Read | 👁 Read | 👁 Read |
| `odometer` | ✏️ Write | 👁 Read | 👁 Read | 👁 Read |
| `acquisition_cost` | ✏️ Write | 👁 Read | 👁 Read | 👁 Read |
| `status` | ✏️ Write | 👁 Read | 👁 Read | 👁 Read |

### Driver Model

| Field | Fleet Manager | Driver/Dispatcher | Safety Officer | Financial Analyst |
|---|:---:|:---:|:---:|:---:|
| `name` | ✏️ Write | 👁 Read | ✏️ Write | 👁 Read |
| `license_number` | ✏️ Write | 👁 Read | ✏️ Write | 👁 Read |
| `license_expiry` | ✏️ Write | 👁 Read | ✏️ Write | 👁 Read |
| `safety_score` | ✏️ Write | 👁 Read | ✏️ Write | 👁 Read |
| `status` | ✏️ Write | 👁 Read | ✏️ Write | 👁 Read |
| `contact_number` | ✏️ Write | 👁 Read | ✏️ Write | 👁 Read |

### Trip Model

| Field | Fleet Manager | Driver/Dispatcher | Safety Officer | Financial Analyst |
|---|:---:|:---:|:---:|:---:|
| `source` | ✏️ Write | ✏️ Write | 👁 Read | 👁 Read |
| `destination` | ✏️ Write | ✏️ Write | 👁 Read | 👁 Read |
| `vehicle_id` | ✏️ Write | ✏️ Write | 👁 Read | 👁 Read |
| `driver_id` | ✏️ Write | ✏️ Write | 👁 Read | 👁 Read |
| `cargo_weight` | ✏️ Write | ✏️ Write | 👁 Read | 👁 Read |
| `status` | ✏️ Write | ✏️ Write | 👁 Read | 👁 Read |
| `fuel_consumed` | ✏️ Write | ✏️ Write | 👁 Read | 👁 Read |

---

## 9. Implementation in Odoo

### Security Group XML (`security/transit_security.xml`)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Category -->
    <record id="module_category_transit" model="ir.module.category">
        <field name="name">TransitOps</field>
        <field name="sequence">10</field>
    </record>

    <!-- Base User Group -->
    <record id="group_transit_user" model="res.groups">
        <field name="name">TransitOps User</field>
        <field name="category_id" ref="module_category_transit"/>
        <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
    </record>

    <!-- Driver / Dispatcher -->
    <record id="group_transit_driver" model="res.groups">
        <field name="name">Driver / Dispatcher</field>
        <field name="category_id" ref="module_category_transit"/>
        <field name="implied_ids" eval="[(4, ref('group_transit_user'))]"/>
        <field name="comment">
            Create and manage trips, assign vehicles and drivers,
            monitor active deliveries, log fuel consumption.
        </field>
    </record>

    <!-- Safety Officer -->
    <record id="group_transit_safety" model="res.groups">
        <field name="name">Safety Officer</field>
        <field name="category_id" ref="module_category_transit"/>
        <field name="implied_ids" eval="[(4, ref('group_transit_user'))]"/>
        <field name="comment">
            Ensure driver compliance, track license validity,
            monitor safety scores, suspend non-compliant drivers.
        </field>
    </record>

    <!-- Financial Analyst -->
    <record id="group_transit_finance" model="res.groups">
        <field name="name">Financial Analyst</field>
        <field name="category_id" ref="module_category_transit"/>
        <field name="implied_ids" eval="[(4, ref('group_transit_user'))]"/>
        <field name="comment">
            Review operational expenses, fuel consumption,
            maintenance costs, and profitability analysis.
        </field>
    </record>

    <!-- Fleet Manager (Full Access) -->
    <record id="group_transit_manager" model="res.groups">
        <field name="name">Fleet Manager</field>
        <field name="category_id" ref="module_category_transit"/>
        <field name="implied_ids" eval="[(4, ref('group_transit_user'))]"/>
        <field name="comment">
            Full access to all TransitOps features including
            vehicle lifecycle, maintenance, dispatch, and reporting.
        </field>
    </record>
</odoo>
```

---

## 10. Demo User Setup

### Pre-configured Demo Users

| # | Name | Email | Password | Role | Group |
|---|------|-------|----------|------|-------|
| 1 | Rajesh Kumar | fleet@transitops.com | fleet123 | Fleet Manager | `group_transit_manager` |
| 2 | Priya Singh | driver@transitops.com | driver123 | Driver/Dispatcher | `group_transit_driver` |
| 3 | Amit Sharma | safety@transitops.com | safety123 | Safety Officer | `group_transit_safety` |
| 4 | Neha Patel | finance@transitops.com | finance123 | Financial Analyst | `group_transit_finance` |

### Demo User Data XML

```xml
<!-- Fleet Manager -->
<record id="user_fleet_manager" model="res.users">
    <field name="name">Rajesh Kumar</field>
    <field name="login">fleet@transitops.com</field>
    <field name="password">fleet123</field>
    <field name="groups_id" eval="[(4, ref('transit.group_transit_manager'))]"/>
</record>

<!-- Driver / Dispatcher -->
<record id="user_driver" model="res.users">
    <field name="name">Priya Singh</field>
    <field name="login">driver@transitops.com</field>
    <field name="password">driver123</field>
    <field name="groups_id" eval="[(4, ref('transit.group_transit_driver'))]"/>
</record>

<!-- Safety Officer -->
<record id="user_safety" model="res.users">
    <field name="name">Amit Sharma</field>
    <field name="login">safety@transitops.com</field>
    <field name="password">safety123</field>
    <field name="groups_id" eval="[(4, ref('transit.group_transit_safety'))]"/>
</record>

<!-- Financial Analyst -->
<record id="user_finance" model="res.users">
    <field name="name">Neha Patel</field>
    <field name="login">finance@transitops.com</field>
    <field name="password">finance123</field>
    <field name="groups_id" eval="[(4, ref('transit.group_transit_finance'))]"/>
</record>
```

---

## 11. Role Assignment Workflow

### How to Assign Roles to New Users

```
Step 1: Login as Fleet Manager or Admin
Step 2: Navigate to Settings → Users & Companies → Users
Step 3: Click [Create] or select existing user
Step 4: Scroll to "TransitOps" section in user form
Step 5: Select one of:
        ○ Driver / Dispatcher
        ○ Safety Officer
        ○ Financial Analyst
        ○ Fleet Manager
Step 6: Save → User gets role-appropriate access immediately
```

### Role Change Impact

| Action | Effect |
|---|---|
| Upgrade Driver → Manager | Gains full CRUD on all models |
| Downgrade Manager → Driver | Loses vehicle/driver/maintenance write access |
| Add Safety to Finance user | User gets BOTH safety + finance permissions |
| Remove all TransitOps groups | User loses all TransitOps menu access |

---

## 📝 Security Best Practices

1. **Principle of Least Privilege** — Each role gets only the minimum permissions needed.
2. **Server-Side Enforcement** — All ACLs are enforced at the ORM level, not just UI hiding.
3. **Record Rules** — Row-level security ensures users only see/edit appropriate records.
4. **Audit Trail** — All changes tracked via `mail.thread` for accountability.
5. **No Shared Accounts** — Each user gets their own login and role assignment.
6. **Password Policy** — Enforced via Odoo's built-in password strength requirements.

---

*Last updated: July 2026 | TransitOps Hackathon Project*
