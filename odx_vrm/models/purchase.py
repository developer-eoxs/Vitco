from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    vrm_id = fields.Many2one(
        'vrm.lead', string='Opportunity', check_company=True,
        domain="[('type', '=', 'opportunity'),('pr_management', '=', 'vrm'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
# ,
