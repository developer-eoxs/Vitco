from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request


class CutPriceForm(http.Controller):
    @http.route(['/custom/cut_price'], type='json', auth="public", website=True)
    def get_cut_price(self, **kw):
        total_price = 0
        # thickness_value=0
        input_qty = float(kw.get('qty'))
        input_width = float(kw.get('width'))
        input_length = float(kw.get('length'))*12
        input_thickness = float(kw.get('thickness'))
        # input_thickness2 = float(kw.get('thickness2'))
        pro_variant = kw.get('pro_variant')
        # if input_thickness1:
        #     thickness_value +=input_thickness1
        # elif (input_thickness2):
        #     thickness_value += input_thickness2
        # else:
        #     thickness_value = 0

        product_selected = request.env['product.template'].sudo().search(
            [('id', '=', pro_variant)], limit=1)
        total_price = (input_length * input_width * input_thickness * 0.284) * input_qty * product_selected.lst_price
        price_values = {'total_price': total_price}

        return price_values
