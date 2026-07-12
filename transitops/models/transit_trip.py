# Part of TransitOps. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date


class TransitTrip(models.Model):
    _name = 'transit.trip'
    _description = 'Transit Trip'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # -------------------------------------------------------------------------
    # FIELDS
    # -------------------------------------------------------------------------
    name = fields.Char(
        string='Trip Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    source = fields.Char(
        string='Source Location',
        required=True,
        tracking=True,
    )
    destination = fields.Char(
        string='Destination',
        required=True,
        tracking=True,
    )
    vehicle_id = fields.Many2one(
        'transit.vehicle',
        string='Vehicle',
        required=True,
        tracking=True,
        domain="[('status', '=', 'available')]",
    )
    driver_id = fields.Many2one(
        'transit.driver',
        string='Driver',
        required=True,
        tracking=True,
        domain="[('status', '=', 'available'), ('is_license_expired', '=', False)]",
    )
    cargo_weight = fields.Float(
        string='Cargo Weight (kg)',
        required=True,
        tracking=True,
    )
    planned_distance = fields.Float(
        string='Planned Distance (km)',
        required=True,
        tracking=True,
    )
    actual_distance = fields.Float(
        string='Actual Distance (km)',
        tracking=True,
    )
    start_odometer = fields.Float(
        string='Start Odometer (km)',
        tracking=True,
    )
    end_odometer = fields.Float(
        string='End Odometer (km)',
        tracking=True,
    )
    fuel_consumed = fields.Float(
        string='Fuel Consumed (Liters)',
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('dispatched', 'Dispatched'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
    )
    dispatch_date = fields.Datetime(
        string='Dispatch Date',
        tracking=True,
    )
    completion_date = fields.Datetime(
        string='Completion Date',
        tracking=True,
    )
    cancellation_reason = fields.Text(
        string='Cancellation Reason',
    )
    notes = fields.Text(
        string='Trip Notes',
    )

    # -------------------------------------------------------------------------
    # RELATED / COMPUTED FIELDS
    # -------------------------------------------------------------------------
    vehicle_max_capacity = fields.Float(
        string='Vehicle Max Capacity',
        related='vehicle_id.max_capacity',
        readonly=True,
    )
    vehicle_type = fields.Selection(
        related='vehicle_id.vehicle_type',
        string='Vehicle Type',
        readonly=True,
        store=True,
    )
    driver_license_expiry = fields.Date(
        related='driver_id.license_expiry',
        string='Driver License Expiry',
        readonly=True,
    )
    fuel_efficiency = fields.Float(
        string='Trip Fuel Efficiency (km/L)',
        compute='_compute_fuel_efficiency',
        store=True,
        digits=(10, 2),
    )
    color = fields.Integer(
        string='Color Index',
        compute='_compute_color',
    )

    # -------------------------------------------------------------------------
    # RELATIONAL FIELDS
    # -------------------------------------------------------------------------
    fuel_log_ids = fields.One2many(
        'transit.fuel.log', 'trip_id',
        string='Fuel Logs',
    )
    expense_ids = fields.One2many(
        'transit.expense', 'trip_id',
        string='Expenses',
    )

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------
    @api.depends('actual_distance', 'fuel_consumed')
    def _compute_fuel_efficiency(self):
        for trip in self:
            if trip.fuel_consumed > 0:
                trip.fuel_efficiency = trip.actual_distance / trip.fuel_consumed
            else:
                trip.fuel_efficiency = 0.0

    def _compute_color(self):
        color_map = {
            'draft': 3,       # Yellow
            'dispatched': 4,  # Blue
            'completed': 10,  # Green
            'cancelled': 1,   # Red
        }
        for trip in self:
            trip.color = color_map.get(trip.state, 0)

    # -------------------------------------------------------------------------
    # CONSTRAINS
    # -------------------------------------------------------------------------
    @api.constrains('cargo_weight', 'vehicle_id')
    def _check_cargo_weight(self):
        for trip in self:
            if trip.vehicle_id and trip.cargo_weight > trip.vehicle_id.max_capacity:
                raise ValidationError(
                    _("Cargo weight (%.1f kg) exceeds vehicle '%s' maximum "
                      "capacity (%.1f kg)!")
                    % (trip.cargo_weight, trip.vehicle_id.display_name,
                       trip.vehicle_id.max_capacity)
                )

    @api.constrains('cargo_weight')
    def _check_cargo_positive(self):
        for trip in self:
            if trip.cargo_weight <= 0:
                raise ValidationError(
                    _("Cargo weight must be greater than zero.")
                )

    @api.constrains('planned_distance')
    def _check_planned_distance(self):
        for trip in self:
            if trip.planned_distance <= 0:
                raise ValidationError(
                    _("Planned distance must be greater than zero.")
                )

    @api.constrains('end_odometer', 'start_odometer')
    def _check_odometer(self):
        for trip in self:
            if trip.end_odometer and trip.start_odometer:
                if trip.end_odometer < trip.start_odometer:
                    raise ValidationError(
                        _("End odometer (%.1f) cannot be less than start "
                          "odometer (%.1f).")
                        % (trip.end_odometer, trip.start_odometer)
                    )

    # -------------------------------------------------------------------------
    # CRUD OVERRIDES
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'transit.trip'
                ) or _('New')
        return super().create(vals_list)

    # -------------------------------------------------------------------------
    # BUSINESS LOGIC — STATUS TRANSITIONS
    # -------------------------------------------------------------------------
    def action_dispatch(self):
        """
        Dispatch the trip.
        Business Rules:
        - Vehicle must be 'available'
        - Driver must be 'available'
        - Driver license must not be expired
        - Driver must not be 'suspended'
        - Cargo weight must not exceed vehicle capacity
        - Auto-sets vehicle and driver status to 'on_trip'
        """
        for trip in self:
            if trip.state != 'draft':
                raise ValidationError(
                    _("Only draft trips can be dispatched.")
                )

            # Validate vehicle availability
            if trip.vehicle_id.status != 'available':
                raise ValidationError(
                    _("Vehicle '%s' is not available for dispatch. "
                      "Current status: %s")
                    % (trip.vehicle_id.display_name, trip.vehicle_id.status)
                )

            # Validate driver availability
            if trip.driver_id.status != 'available':
                raise ValidationError(
                    _("Driver '%s' is not available for dispatch. "
                      "Current status: %s")
                    % (trip.driver_id.name, trip.driver_id.status)
                )

            # Validate driver license
            if trip.driver_id.is_license_expired:
                raise ValidationError(
                    _("Driver '%s' has an expired license (expired on %s). "
                      "Cannot assign to trip.")
                    % (trip.driver_id.name, trip.driver_id.license_expiry)
                )

            # Validate driver not suspended
            if trip.driver_id.status == 'suspended':
                raise ValidationError(
                    _("Driver '%s' is suspended and cannot be assigned to a trip.")
                    % trip.driver_id.name
                )

            # Validate cargo weight
            if trip.cargo_weight > trip.vehicle_id.max_capacity:
                raise ValidationError(
                    _("Cargo weight (%.1f kg) exceeds vehicle capacity (%.1f kg).")
                    % (trip.cargo_weight, trip.vehicle_id.max_capacity)
                )

            # Record start odometer from vehicle
            trip.start_odometer = trip.vehicle_id.odometer

            # ── AUTO STATUS TRANSITIONS ──
            trip.vehicle_id.status = 'on_trip'
            trip.driver_id.status = 'on_trip'
            trip.state = 'dispatched'
            trip.dispatch_date = fields.Datetime.now()

    def action_complete(self):
        """
        Complete the trip.
        Business Rules:
        - Must be in 'dispatched' state
        - End odometer and fuel consumed must be provided
        - Auto-resets vehicle and driver status to 'available'
        - Updates vehicle odometer
        - Creates a fuel log automatically
        """
        for trip in self:
            if trip.state != 'dispatched':
                raise ValidationError(
                    _("Only dispatched trips can be completed.")
                )

            if not trip.end_odometer:
                raise ValidationError(
                    _("Please enter the final odometer reading before completing.")
                )

            if not trip.fuel_consumed:
                raise ValidationError(
                    _("Please enter the fuel consumed before completing.")
                )

            # Calculate actual distance
            trip.actual_distance = trip.end_odometer - trip.start_odometer

            # Update vehicle odometer
            trip.vehicle_id.odometer = trip.end_odometer

            # ── AUTO STATUS TRANSITIONS ──
            trip.vehicle_id.status = 'available'
            trip.driver_id.status = 'available'
            trip.state = 'completed'
            trip.completion_date = fields.Datetime.now()

            # ── AUTO-CREATE FUEL LOG ──
            self.env['transit.fuel.log'].create({
                'vehicle_id': trip.vehicle_id.id,
                'trip_id': trip.id,
                'liters': trip.fuel_consumed,
                'date': fields.Date.today(),
                'notes': _('Auto-created from trip %s completion') % trip.name,
            })

    def action_cancel(self):
        """
        Cancel the trip.
        Business Rules:
        - Can cancel from draft or dispatched state
        - If dispatched, auto-restores vehicle and driver status to 'available'
        """
        for trip in self:
            if trip.state not in ('draft', 'dispatched'):
                raise ValidationError(
                    _("Only draft or dispatched trips can be cancelled.")
                )

            # If was dispatched, restore statuses
            if trip.state == 'dispatched':
                trip.vehicle_id.status = 'available'
                trip.driver_id.status = 'available'

            trip.state = 'cancelled'

    def action_reset_to_draft(self):
        """Reset a cancelled trip back to draft."""
        for trip in self:
            if trip.state != 'cancelled':
                raise ValidationError(
                    _("Only cancelled trips can be reset to draft.")
                )
            trip.state = 'draft'
