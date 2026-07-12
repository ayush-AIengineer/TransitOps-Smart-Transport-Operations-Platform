# Part of TransitOps. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TransitVehicle(models.Model):
    _name = 'transit.vehicle'
    _description = 'Transit Vehicle'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc'
    _rec_name = 'display_name'

    # -------------------------------------------------------------------------
    # FIELDS
    # -------------------------------------------------------------------------
    name = fields.Char(
        string='Vehicle Name/Model',
        required=True,
        tracking=True,
        help='Name or model of the vehicle (e.g., Tata Ace, Ashok Leyland)',
    )
    registration_no = fields.Char(
        string='Registration Number',
        required=True,
        tracking=True,
        copy=False,
        help='Unique registration number of the vehicle',
    )
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True,
    )
    vehicle_type = fields.Selection(
        selection=[
            ('truck', 'Truck'),
            ('van', 'Van'),
            ('bus', 'Bus'),
            ('car', 'Car'),
            ('mini_truck', 'Mini Truck'),
            ('trailer', 'Trailer'),
        ],
        string='Vehicle Type',
        required=True,
        default='truck',
        tracking=True,
    )
    max_capacity = fields.Float(
        string='Maximum Load Capacity (kg)',
        required=True,
        tracking=True,
        help='Maximum cargo weight this vehicle can carry in kilograms',
    )
    odometer = fields.Float(
        string='Odometer (km)',
        default=0.0,
        tracking=True,
        help='Current odometer reading in kilometers',
    )
    acquisition_cost = fields.Float(
        string='Acquisition Cost',
        tracking=True,
        help='Purchase price of the vehicle',
    )
    status = fields.Selection(
        selection=[
            ('available', 'Available'),
            ('on_trip', 'On Trip'),
            ('in_shop', 'In Shop'),
            ('retired', 'Retired'),
        ],
        string='Status',
        default='available',
        required=True,
        tracking=True,
    )
    region = fields.Char(
        string='Region',
        tracking=True,
        help='Operating region for this vehicle',
    )
    image = fields.Binary(
        string='Vehicle Image',
        attachment=True,
    )
    notes = fields.Text(
        string='Notes',
    )

    # -------------------------------------------------------------------------
    # RELATIONAL FIELDS
    # -------------------------------------------------------------------------
    trip_ids = fields.One2many(
        'transit.trip', 'vehicle_id',
        string='Trips',
    )
    maintenance_ids = fields.One2many(
        'transit.maintenance', 'vehicle_id',
        string='Maintenance Records',
    )
    fuel_log_ids = fields.One2many(
        'transit.fuel.log', 'vehicle_id',
        string='Fuel Logs',
    )
    expense_ids = fields.One2many(
        'transit.expense', 'vehicle_id',
        string='Expenses',
    )

    # -------------------------------------------------------------------------
    # COMPUTED FIELDS
    # -------------------------------------------------------------------------
    total_trips = fields.Integer(
        string='Total Trips',
        compute='_compute_trip_stats',
        store=True,
    )
    total_distance = fields.Float(
        string='Total Distance (km)',
        compute='_compute_trip_stats',
        store=True,
    )
    total_fuel_cost = fields.Float(
        string='Total Fuel Cost',
        compute='_compute_cost_stats',
        store=True,
    )
    total_maintenance_cost = fields.Float(
        string='Total Maintenance Cost',
        compute='_compute_cost_stats',
        store=True,
    )
    total_expense = fields.Float(
        string='Total Expenses',
        compute='_compute_cost_stats',
        store=True,
    )
    total_ops_cost = fields.Float(
        string='Total Operational Cost',
        compute='_compute_cost_stats',
        store=True,
    )
    fuel_efficiency = fields.Float(
        string='Fuel Efficiency (km/L)',
        compute='_compute_fuel_efficiency',
        store=True,
        digits=(10, 2),
    )
    vehicle_roi = fields.Float(
        string='Vehicle ROI (%)',
        compute='_compute_vehicle_roi',
        store=True,
        digits=(10, 2),
    )
    color = fields.Integer(
        string='Color Index',
        compute='_compute_color',
    )

    # -------------------------------------------------------------------------
    # SQL CONSTRAINTS
    # -------------------------------------------------------------------------
    _sql_constraints = [
        (
            'registration_no_unique',
            'UNIQUE(registration_no)',
            'The registration number must be unique! A vehicle with this registration already exists.',
        ),
        (
            'max_capacity_positive',
            'CHECK(max_capacity > 0)',
            'Maximum load capacity must be greater than zero.',
        ),
    ]

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------
    @api.depends('name', 'registration_no')
    def _compute_display_name(self):
        for vehicle in self:
            if vehicle.registration_no and vehicle.name:
                vehicle.display_name = f"[{vehicle.registration_no}] {vehicle.name}"
            else:
                vehicle.display_name = vehicle.name or ''

    @api.depends('trip_ids', 'trip_ids.state', 'trip_ids.actual_distance')
    def _compute_trip_stats(self):
        for vehicle in self:
            completed_trips = vehicle.trip_ids.filtered(lambda t: t.state == 'completed')
            vehicle.total_trips = len(completed_trips)
            vehicle.total_distance = sum(completed_trips.mapped('actual_distance'))

    @api.depends(
        'fuel_log_ids.cost',
        'maintenance_ids.cost',
        'expense_ids.amount',
    )
    def _compute_cost_stats(self):
        for vehicle in self:
            vehicle.total_fuel_cost = sum(vehicle.fuel_log_ids.mapped('cost'))
            vehicle.total_maintenance_cost = sum(
                vehicle.maintenance_ids.filtered(
                    lambda m: m.state == 'done'
                ).mapped('cost')
            )
            vehicle.total_expense = sum(vehicle.expense_ids.mapped('amount'))
            vehicle.total_ops_cost = (
                vehicle.total_fuel_cost
                + vehicle.total_maintenance_cost
                + vehicle.total_expense
            )

    @api.depends('total_distance', 'fuel_log_ids.liters')
    def _compute_fuel_efficiency(self):
        for vehicle in self:
            total_fuel = sum(vehicle.fuel_log_ids.mapped('liters'))
            if total_fuel > 0:
                vehicle.fuel_efficiency = vehicle.total_distance / total_fuel
            else:
                vehicle.fuel_efficiency = 0.0

    @api.depends('total_ops_cost', 'acquisition_cost')
    def _compute_vehicle_roi(self):
        for vehicle in self:
            if vehicle.acquisition_cost > 0:
                # ROI = (Revenue - Costs) / Acquisition Cost * 100
                # Since we don't track revenue directly, we show cost ratio
                vehicle.vehicle_roi = (
                    (vehicle.acquisition_cost - vehicle.total_ops_cost)
                    / vehicle.acquisition_cost * 100
                )
            else:
                vehicle.vehicle_roi = 0.0

    def _compute_color(self):
        color_map = {
            'available': 10,   # Green
            'on_trip': 4,      # Blue
            'in_shop': 2,      # Orange
            'retired': 1,      # Red
        }
        for vehicle in self:
            vehicle.color = color_map.get(vehicle.status, 0)

    # -------------------------------------------------------------------------
    # CONSTRAINS
    # -------------------------------------------------------------------------
    @api.constrains('odometer')
    def _check_odometer(self):
        for vehicle in self:
            if vehicle.odometer < 0:
                raise ValidationError(
                    _("Odometer reading cannot be negative for vehicle '%s'.")
                    % vehicle.name
                )

    # -------------------------------------------------------------------------
    # ACTIONS
    # -------------------------------------------------------------------------
    def action_retire(self):
        """Retire the vehicle - terminal state."""
        for vehicle in self:
            if vehicle.status == 'on_trip':
                raise ValidationError(
                    _("Cannot retire vehicle '%s' while it is on a trip. "
                      "Complete or cancel the trip first.")
                    % vehicle.name
                )
            vehicle.status = 'retired'

    def action_reactivate(self):
        """Reactivate a retired vehicle."""
        for vehicle in self:
            if vehicle.status != 'retired':
                raise ValidationError(
                    _("Only retired vehicles can be reactivated.")
                )
            vehicle.status = 'available'

    def action_view_trips(self):
        """Open trips for this vehicle."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Trips - %s') % self.display_name,
            'res_model': 'transit.trip',
            'view_mode': 'list,form',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id},
        }

    def action_view_maintenance(self):
        """Open maintenance records for this vehicle."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Maintenance - %s') % self.display_name,
            'res_model': 'transit.maintenance',
            'view_mode': 'list,form',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id},
        }

    def action_view_fuel_logs(self):
        """Open fuel logs for this vehicle."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Fuel Logs - %s') % self.display_name,
            'res_model': 'transit.fuel.log',
            'view_mode': 'list,form',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id},
        }
