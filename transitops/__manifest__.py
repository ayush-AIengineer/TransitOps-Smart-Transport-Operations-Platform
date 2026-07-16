# Part of TransitOps. See LICENSE file for full copyright and licensing details.
{
    'name': 'TransitOps - Smart Transport Operations Platform',
    'version': '18.0.1.0.0',
    'category': 'Transport/Fleet',
    'summary': 'End-to-end transport operations: vehicles, drivers, trips, maintenance & analytics',
    'description': """
TransitOps - Smart Transport Operations Platform
=================================================

A centralized fleet & transport operations platform that digitizes vehicle, 
driver, dispatch, maintenance, and expense management with enforced business 
rules and real-time operational insights.

Key Features:
-------------
* Vehicle Registry with full lifecycle management
* Driver Management with license & safety tracking
* Trip Management with automated status transitions
* Maintenance Workflow with auto status changes
* Fuel & Expense tracking with cost computations
* Dashboard with real-time KPIs and analytics
* Role-Based Access Control (4 roles)
* PDF/CSV Reports and exports
* Email reminders for license expiry
* Full audit trail on all operations
    """,
    'author': 'TransitOps Team',
    'website': 'https://github.com/ayush-AIengineer/TransitOps-Smart-Transport-Operations-Platform',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'web',
    ],
    'data': [
        # Security (must load first)
        'security/transit_security.xml',
        'security/ir.model.access.csv',

        # Views
        'views/vehicle_views.xml',
        'views/driver_views.xml',
        'views/trip_views.xml',
        'views/maintenance_views.xml',
        'views/fuel_log_views.xml',
        'views/expense_views.xml',
        'views/dashboard_views.xml',
        'views/menu_views.xml',

        # Data
        'data/scheduled_actions.xml',
        'data/email_templates.xml',

        # Reports
        'reports/trip_report.xml',
        'reports/vehicle_report.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'assets': {},
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 1,
}
