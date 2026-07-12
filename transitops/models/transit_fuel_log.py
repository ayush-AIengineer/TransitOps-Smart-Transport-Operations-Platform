# Part of TransitOps. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TransitFuelLog(models.Model):
    _name = 'transit.fuel.log'
    _description = 'Transit Fuel Log'
    _inherit = ['mail.thread']
    _order = 'date desc'

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
    trip_id = fields.Many2one(
        'transit.trip',
        string='Related Trip',
        tracking=True,
    )
    liters = fields.Float(
        string='Fuel Quantity (Liters)',
        required=True,
        tracking=True,
    )
    price_per_liter = fields.Float(
        string='Price per Liter',
        default=0.0,
    )
    cost = fields.Float(
        string='Total Fuel Cost',
        compute='_compute_cost',
        store=True,
        tracking=True,
    )
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.today,
        tracking=True,
    )
    odometer_at_fill = fields.Float(
        string='Odometer at Fueling',
    )
    fuel_type = fields.Selection(
        selection=[
            ('diesel', 'Diesel'),
            ('petrol', 'Petrol'),
            ('cng', 'CNG'),
            ('electric', 'Electric'),
        ],
        string='Fuel Type',
        default='diesel',
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

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------
    @api.depends('liters', 'price_per_liter')
    def _compute_cost(self):
        for log in self:
            log.cost = log.liters * log.price_per_liter

    # -------------------------------------------------------------------------
    # CONSTRAINS
    # -------------------------------------------------------------------------
    @api.constrains('liters')
    def _check_liters(self):
        for log in self:
            if log.liters <= 0:
                raise ValidationError(
                    _("Fuel quantity must be greater than zero.")
                )

    @api.constrains('price_per_liter')
    def _check_price(self):
        for log in self:
            if log.price_per_liter < 0:
                raise ValidationError(
                    _("Price per liter cannot be negative.")
                )

    # -------------------------------------------------------------------------
    # CRUD OVERRIDES
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'transit.fuel.log'
                ) or _('New')
        return super().create(vals_list)
