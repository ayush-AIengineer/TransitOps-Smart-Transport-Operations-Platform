# Part of TransitOps. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, timedelta


class TransitDriver(models.Model):
    _name = 'transit.driver'
    _description = 'Transit Driver'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc'

    # -------------------------------------------------------------------------
    # FIELDS
    # -------------------------------------------------------------------------
    name = fields.Char(
        string='Driver Name',
        required=True,
        tracking=True,
    )
    license_number = fields.Char(
        string='License Number',
        required=True,
        tracking=True,
        copy=False,
    )
    license_category = fields.Selection(
        selection=[
            ('lmv', 'LMV - Light Motor Vehicle'),
            ('hmv', 'HMV - Heavy Motor Vehicle'),
            ('hgmv', 'HGMV - Heavy Goods Motor Vehicle'),
            ('transport', 'Transport'),
            ('hazardous', 'Hazardous Goods'),
        ],
        string='License Category',
        required=True,
        default='hmv',
        tracking=True,
    )
    license_expiry = fields.Date(
        string='License Expiry Date',
        required=True,
        tracking=True,
    )
    contact_number = fields.Char(
        string='Contact Number',
        tracking=True,
    )
    email = fields.Char(
        string='Email',
    )
    safety_score = fields.Float(
        string='Safety Score',
        default=100.0,
        tracking=True,
        help='Safety score out of 100. Decreases on incidents, increases on clean trips.',
    )
    status = fields.Selection(
        selection=[
            ('available', 'Available'),
            ('on_trip', 'On Trip'),
            ('off_duty', 'Off Duty'),
            ('suspended', 'Suspended'),
        ],
        string='Status',
        default='available',
        required=True,
        tracking=True,
    )
    image = fields.Binary(
        string='Driver Photo',
        attachment=True,
    )
    address = fields.Text(
        string='Address',
    )
    date_of_joining = fields.Date(
        string='Date of Joining',
        default=fields.Date.today,
    )
    notes = fields.Text(
        string='Notes',
    )

    # -------------------------------------------------------------------------
    # RELATIONAL FIELDS
    # -------------------------------------------------------------------------
    trip_ids = fields.One2many(
        'transit.trip', 'driver_id',
        string='Trips',
    )

    # -------------------------------------------------------------------------
    # COMPUTED FIELDS
    # -------------------------------------------------------------------------
    total_trips = fields.Integer(
        string='Total Completed Trips',
        compute='_compute_trip_stats',
        store=True,
    )
    total_distance = fields.Float(
        string='Total Distance Driven (km)',
        compute='_compute_trip_stats',
        store=True,
    )
    is_license_expired = fields.Boolean(
        string='License Expired',
        compute='_compute_license_status',
        store=True,
    )
    is_license_expiring_soon = fields.Boolean(
        string='License Expiring Soon',
        compute='_compute_license_status',
        store=True,
        help='True if license expires within 30 days',
    )
    days_until_expiry = fields.Integer(
        string='Days Until License Expiry',
        compute='_compute_license_status',
        store=True,
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
            'license_number_unique',
            'UNIQUE(license_number)',
            'The license number must be unique! A driver with this license already exists.',
        ),
        (
            'safety_score_range',
            'CHECK(safety_score >= 0 AND safety_score <= 100)',
            'Safety score must be between 0 and 100.',
        ),
    ]

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------
    @api.depends('trip_ids', 'trip_ids.state', 'trip_ids.actual_distance')
    def _compute_trip_stats(self):
        for driver in self:
            completed_trips = driver.trip_ids.filtered(lambda t: t.state == 'completed')
            driver.total_trips = len(completed_trips)
            driver.total_distance = sum(completed_trips.mapped('actual_distance'))

    @api.depends('license_expiry')
    def _compute_license_status(self):
        today = date.today()
        for driver in self:
            if driver.license_expiry:
                delta = (driver.license_expiry - today).days
                driver.days_until_expiry = delta
                driver.is_license_expired = delta < 0
                driver.is_license_expiring_soon = 0 <= delta <= 30
            else:
                driver.days_until_expiry = 0
                driver.is_license_expired = False
                driver.is_license_expiring_soon = False

    def _compute_color(self):
        color_map = {
            'available': 10,   # Green
            'on_trip': 4,      # Blue
            'off_duty': 3,     # Yellow
            'suspended': 1,    # Red
        }
        for driver in self:
            if driver.is_license_expired:
                driver.color = 1  # Red for expired
            elif driver.is_license_expiring_soon:
                driver.color = 2  # Orange for expiring soon
            else:
                driver.color = color_map.get(driver.status, 0)

    # -------------------------------------------------------------------------
    # CONSTRAINS
    # -------------------------------------------------------------------------
    @api.constrains('license_expiry')
    def _check_license_expiry(self):
        for driver in self:
            if driver.license_expiry and driver.license_expiry < date.today():
                # Don't raise error, but auto-suspend
                if driver.status not in ('suspended', 'on_trip'):
                    driver.status = 'suspended'

    # -------------------------------------------------------------------------
    # ACTIONS
    # -------------------------------------------------------------------------
    def action_suspend(self):
        """Suspend the driver due to compliance issues."""
        for driver in self:
            if driver.status == 'on_trip':
                raise ValidationError(
                    _("Cannot suspend driver '%s' while on a trip. "
                      "Complete or cancel the trip first.")
                    % driver.name
                )
            driver.status = 'suspended'

    def action_reinstate(self):
        """Reinstate a suspended or off-duty driver."""
        for driver in self:
            if driver.is_license_expired:
                raise ValidationError(
                    _("Cannot reinstate driver '%s'. Their license expired on %s. "
                      "Please update the license expiry date first.")
                    % (driver.name, driver.license_expiry)
                )
            driver.status = 'available'

    def action_off_duty(self):
        """Set driver to off duty."""
        for driver in self:
            if driver.status == 'on_trip':
                raise ValidationError(
                    _("Cannot set driver '%s' to off duty while on a trip.")
                    % driver.name
                )
            driver.status = 'off_duty'

    def action_view_trips(self):
        """Open trips for this driver."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Trips - %s') % self.name,
            'res_model': 'transit.trip',
            'view_mode': 'list,form',
            'domain': [('driver_id', '=', self.id)],
            'context': {'default_driver_id': self.id},
        }

    # -------------------------------------------------------------------------
    # CRON METHODS
    # -------------------------------------------------------------------------
    @api.model
    def _cron_check_license_expiry(self):
        """Cron job: Check for expiring/expired licenses and take action."""
        today = date.today()
        threshold = today + timedelta(days=30)

        # Auto-suspend expired licenses
        expired_drivers = self.search([
            ('license_expiry', '<', today),
            ('status', '!=', 'suspended'),
            ('status', '!=', 'on_trip'),
        ])
        for driver in expired_drivers:
            driver.status = 'suspended'
            driver.message_post(
                body=_("Driver automatically suspended: License expired on %s.")
                % driver.license_expiry,
                message_type='notification',
            )

        # Send warning for expiring soon
        expiring_drivers = self.search([
            ('license_expiry', '>=', today),
            ('license_expiry', '<=', threshold),
            ('status', '!=', 'suspended'),
        ])
        template = self.env.ref(
            'transitops.email_template_license_expiry_warning',
            raise_if_not_found=False,
        )
        if template:
            for driver in expiring_drivers:
                template.send_mail(driver.id, force_send=False)
                driver.message_post(
                    body=_("Warning: License expiring on %s (%d days remaining).")
                    % (driver.license_expiry, driver.days_until_expiry),
                    message_type='notification',
                )
