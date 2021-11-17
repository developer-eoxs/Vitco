from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _get_default_ftechnical_delivery_cond(self):
        return """
            <section>
                <div class="te_sidenav_menu">
                    <ul>
                        <section>
                                1. Gauge range :
                        </section>
                        <section>
                                2. Width Tolerance : 
                        </section>
                        <section>
                               3. Length Tolerance:
                        </section>
                    </ul>
                </div>
            </section>
        """

    shipped_via = fields.Char(string="Shipped via")
    technical_delivery_cond = fields.Html(string="Technical Delivery Conditions", translate=True,
                                             default=_get_default_ftechnical_delivery_cond)