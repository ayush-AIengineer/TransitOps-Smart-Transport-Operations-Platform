# Part of TransitOps. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TransitMaintenance(models.Model):
    _name = 'transit.maintenance'
    _description = 'Transit Maintenance Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc'

    # -------------------------------------------------------------------------
    # FIELDS
    # -------------------------------------------------------------------------
    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    vehicle_id = fields.Many2one(
        'transit.vehicle',
        string='Vehicle',
        required=True,
        tracking=True,
    )
    maintenance_type = fields.Selection(
        selection=[
            ('oil_change', 'Oil Change'),
            ('tire_replacement', 'Tire Replacement'),
            ('engine_repair', 'Engine Repair'),
            ('brake_service', 'Brake Service'),
            ('body_repair', 'Body Repair'),
            ('general_inspection', 'General Inspection'),
            ('electrical', 'Electrical Work'),
            ('transmission', 'Transmission Service'),
            ('other', 'Other'),
        ],
        string='Maintenance Type',
        required=True,
        tracking=True,
    )
    description = fields.Text(
        string='Description',
        tracking=True,
    )
    cost = fields.Float(
        string='Cost',
        required=True,
        tracking=True,
    )
    start_date = fields.Date(
        string='Start Date',
        required=True,
        default=fields.Date.today,
        tracking=True,
    )
    end_date = fields.Date(
        string='End Date',
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ('in_progress', 'In Progress'),
            ('done', 'Completed'),
        ],
        string='Status',
        default='in_progress',
        required=True,
        tracking=True,
    )
    technician = fields.Char(
        string='Technician/Vendor',
    )
    notes = fields.Text(
        string='Notes',
    )

    # -------------------------------------------------------------------------
    # RELATED FIELDS
    # -------------------------------------------------------------------------
    vehicle_registration = fields.Char(
        related='vehicle_id.registration_no',
        string='Vehicle Registration',
        readonly=True,
        store=True,
    )
    vehicle_status = fields.Selection(
        related='vehicle_id.status',
        string='Vehicle Status',
        readonly=True,
    )

    # -------------------------------------------------------------------------
    # COMPUTED FIELDS
    # -------------------------------------------------------------------------
    duration_days = fields.Integer(
        string='Duration (Days)',
        compute='_compute_duration',
        store=True,
    )
    color = fields.Integer(
        string='Color Index',
        compute='_compute_color',
    )

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------
    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for record in self:
            if record.start_date and record.end_date:
                record.duration_days = (record.end_date - record.start_date).days
            else:
                record.duration_days = 0

    def _compute_color(self):
        for record in self:
            record.color = 2 if record.state == 'in_progress' else 10

    # -------------------------------------------------------------------------
    # CONSTRAINS
    # -------------------------------------------------------------------------
    @api.constrains('cost')
    def _check_cost(self):
        for record in self:
            if record.cost < 0:
                raise ValidationError(
                    _("Maintenance cost cannot be negative.")
                )

    @api.constrains('end_date', 'start_date')
    def _check_dates(self):
        for record in self:
            if record.end_date and record.start_date:
                if record.end_date < record.start_date:
                    raise ValidationError(
                        _("End date cannot be before start date.")
                    )

    # -------------------------------------------------------------------------
    # CRUD OVERRIDES
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            # Generate sequence
            if record.name == _('New'):
                record.name = self.env['ir.sequence'].next_by_code(
                    'transit.maintenance'
                ) or _('New')

            # ── AUTO STATUS TRANSITION ──
            # Creating maintenance record → Vehicle status becomes 'In Shop'
            if record.vehicle_id.status == 'on_trip':
                raise ValidationError(
                    _("Cannot create maintenance for vehicle '%s' while it is "
                      "on a trip. Complete or cancel the trip first.")
                    % record.vehicle_id.display_name
                )
            if record.vehicle_id.status != 'retired':
                record.vehicle_id.status = 'in_shop'
                record.vehicle_id.message_post(
                    body=_("Vehicle moved to 'In Shop' for maintenance: %s")
                    % record.maintenance_type,
                    message_type='notification',
                )
        return records

    # -------------------------------------------------------------------------
    # ACTIONS
    # -------------------------------------------------------------------------
    def action_close(self):
        """
        Close/Complete the maintenance record.
        Business Rules:
        - Sets maintenance state to 'done'
        - Restores vehicle status to 'available' (unless retired)
        """
        for record in self:
            if record.state != 'in_progress':
                raise ValidationError(
                    _("Only in-progress maintenance records can be closed.")
                )

            record.state = 'done'
            record.end_date = fields.Date.today()

            # ── AUTO STATUS TRANSITION ──
            # Close maintenance → Vehicle back to 'Available' (unless retired)
            if record.vehicle_id.status == 'in_shop':
                # Check if there are other active maintenance records
                other_active = self.search([
                    ('vehicle_id', '=', record.vehicle_id.id),
                    ('state', '=', 'in_progress'),
                    ('id', '!=', record.id),
                ])
                if not other_active:
                    record.vehicle_id.status = 'available'
                    record.vehicle_id.message_post(
                        body=_("Vehicle restored to 'Available' after "
                               "maintenance completion."),
                        message_type='notification',
                    )
