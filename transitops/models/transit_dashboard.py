# Part of TransitOps. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class TransitDashboard(models.Model):
    _name = 'transit.dashboard'
    _description = 'Transit Dashboard KPIs'
    _auto = False  # No database table — purely computed

    # -------------------------------------------------------------------------
    # This is a transient-like model used by the dashboard view.
    # All data is computed on-the-fly from other models.
    # -------------------------------------------------------------------------

    name = fields.Char(string='Name', default='Dashboard')

    # Vehicle KPIs
    total_vehicles = fields.Integer(string='Total Vehicles')
    active_vehicles = fields.Integer(string='Active Vehicles (On Trip)')
    available_vehicles = fields.Integer(string='Available Vehicles')
    in_maintenance = fields.Integer(string='Vehicles in Maintenance')
    retired_vehicles = fields.Integer(string='Retired Vehicles')

    # Trip KPIs
    active_trips = fields.Integer(string='Active Trips')
    pending_trips = fields.Integer(string='Pending Trips')
    completed_trips = fields.Integer(string='Completed Trips')

    # Driver KPIs
    total_drivers = fields.Integer(string='Total Drivers')
    drivers_on_duty = fields.Integer(string='Drivers On Duty')
    available_drivers = fields.Integer(string='Available Drivers')
    suspended_drivers = fields.Integer(string='Suspended Drivers')

    # Fleet KPIs
    fleet_utilization = fields.Float(string='Fleet Utilization (%)')
    avg_fuel_efficiency = fields.Float(string='Avg Fuel Efficiency (km/L)')
    total_ops_cost = fields.Float(string='Total Operational Cost')

    def init(self):
        """Create the SQL view for dashboard."""
        self.env.cr.execute("""
            DROP VIEW IF EXISTS transit_dashboard;
            CREATE OR REPLACE VIEW transit_dashboard AS (
                SELECT
                    1 as id,
                    'Dashboard' as name,

                    -- Vehicle KPIs
                    (SELECT COUNT(*) FROM transit_vehicle) as total_vehicles,
                    (SELECT COUNT(*) FROM transit_vehicle WHERE status = 'on_trip') as active_vehicles,
                    (SELECT COUNT(*) FROM transit_vehicle WHERE status = 'available') as available_vehicles,
                    (SELECT COUNT(*) FROM transit_vehicle WHERE status = 'in_shop') as in_maintenance,
                    (SELECT COUNT(*) FROM transit_vehicle WHERE status = 'retired') as retired_vehicles,

                    -- Trip KPIs
                    (SELECT COUNT(*) FROM transit_trip WHERE state = 'dispatched') as active_trips,
                    (SELECT COUNT(*) FROM transit_trip WHERE state = 'draft') as pending_trips,
                    (SELECT COUNT(*) FROM transit_trip WHERE state = 'completed') as completed_trips,

                    -- Driver KPIs
                    (SELECT COUNT(*) FROM transit_driver) as total_drivers,
                    (SELECT COUNT(*) FROM transit_driver WHERE status = 'on_trip') as drivers_on_duty,
                    (SELECT COUNT(*) FROM transit_driver WHERE status = 'available') as available_drivers,
                    (SELECT COUNT(*) FROM transit_driver WHERE status = 'suspended') as suspended_drivers,

                    -- Fleet Utilization
                    CASE
                        WHEN (SELECT COUNT(*) FROM transit_vehicle WHERE status != 'retired') > 0
                        THEN ROUND(
                            (SELECT COUNT(*) FROM transit_vehicle WHERE status = 'on_trip')::numeric /
                            (SELECT COUNT(*) FROM transit_vehicle WHERE status != 'retired')::numeric * 100, 1
                        )
                        ELSE 0
                    END as fleet_utilization,

                    -- Avg Fuel Efficiency
                    COALESCE(
                        (SELECT ROUND(AVG(fuel_efficiency)::numeric, 2)
                         FROM transit_vehicle
                         WHERE fuel_efficiency > 0),
                        0
                    ) as avg_fuel_efficiency,

                    -- Total Ops Cost
                    COALESCE(
                        (SELECT SUM(total_ops_cost) FROM transit_vehicle),
                        0
                    ) as total_ops_cost
            );
        """)

    @api.model
    def get_dashboard_data(self):
        """Return dashboard data as a dictionary for the client-side dashboard."""
        Vehicle = self.env['transit.vehicle']
        Driver = self.env['transit.driver']
        Trip = self.env['transit.trip']
        FuelLog = self.env['transit.fuel.log']
        Maintenance = self.env['transit.maintenance']

        # Vehicle counts
        total_vehicles = Vehicle.search_count([])
        non_retired = Vehicle.search_count([('status', '!=', 'retired')])
        active_vehicles = Vehicle.search_count([('status', '=', 'on_trip')])
        available_vehicles = Vehicle.search_count([('status', '=', 'available')])
        in_maintenance = Vehicle.search_count([('status', '=', 'in_shop')])
        retired_vehicles = Vehicle.search_count([('status', '=', 'retired')])

        # Trip counts
        active_trips = Trip.search_count([('state', '=', 'dispatched')])
        pending_trips = Trip.search_count([('state', '=', 'draft')])
        completed_trips = Trip.search_count([('state', '=', 'completed')])

        # Driver counts
        total_drivers = Driver.search_count([])
        drivers_on_duty = Driver.search_count([('status', '=', 'on_trip')])
        available_drivers = Driver.search_count([('status', '=', 'available')])
        suspended_drivers = Driver.search_count([('status', '=', 'suspended')])

        # Fleet utilization
        fleet_utilization = (
            (active_vehicles / non_retired * 100) if non_retired > 0 else 0
        )

        # Vehicle type distribution for chart
        vehicle_types = Vehicle.read_group(
            domain=[],
            fields=['vehicle_type'],
            groupby=['vehicle_type'],
        )

        # Trip status distribution for chart
        trip_statuses = Trip.read_group(
            domain=[],
            fields=['state'],
            groupby=['state'],
        )

        # Monthly fuel costs for chart
        fuel_monthly = FuelLog.read_group(
            domain=[],
            fields=['date', 'cost:sum'],
            groupby=['date:month'],
            orderby='date:month',
        )

        return {
            'total_vehicles': total_vehicles,
            'active_vehicles': active_vehicles,
            'available_vehicles': available_vehicles,
            'in_maintenance': in_maintenance,
            'retired_vehicles': retired_vehicles,
            'active_trips': active_trips,
            'pending_trips': pending_trips,
            'completed_trips': completed_trips,
            'total_drivers': total_drivers,
            'drivers_on_duty': drivers_on_duty,
            'available_drivers': available_drivers,
            'suspended_drivers': suspended_drivers,
            'fleet_utilization': round(fleet_utilization, 1),
            'vehicle_types': vehicle_types,
            'trip_statuses': trip_statuses,
            'fuel_monthly': fuel_monthly,
        }
