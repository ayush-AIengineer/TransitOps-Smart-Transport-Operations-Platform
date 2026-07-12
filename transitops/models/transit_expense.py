# Part of TransitOps. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TransitExpense(models.Model):
    _name = 'transit.expense'
    _description = 'Transit Expense'
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
        tracking=True,
    )
    trip_id = fields.Many2one(
        'transit.trip',
        string='Related Trip',
        tracking=True,
    )
    expense_type = fields.Selection(
        selection=[
            ('toll', 'Toll'),
            ('parking', 'Parking'),
            ('insurance', 'Insurance'),
            ('fine', 'Traffic Fine'),
            ('cleaning', 'Cleaning'),
            ('permit', 'Permit/License Fee'),
            ('loading', 'Loading/Unloading'),
            ('other', 'Other'),
        ],
        string='Expense Type',
        required=True,
        tracking=True,
    )
    amount = fields.Float(
        string='Amount',
        required=True,
        tracking=True,
    )
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.today,
        tracking=True,
    )
    description = fields.Text(
        string='Description',
    )
    receipt = fields.Binary(
        string='Receipt',
        attachment=True,
    )
    receipt_filename = fields.Char(
        string='Receipt Filename',
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
    # CONSTRAINS
    # -------------------------------------------------------------------------
    @api.constrains('amount')
    def _check_amount(self):
        for expense in self:
            if expense.amount <= 0:
                raise ValidationError(
                    _("Expense amount must be greater than zero.")
                )

    # -------------------------------------------------------------------------
    # CRUD OVERRIDES
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'transit.expense'
                ) or _('New')
        return super().create(vals_list)
