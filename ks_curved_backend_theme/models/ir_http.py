from odoo import models
from odoo.http import request


class KsIrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super(KsIrHttp, self).session_info()
        if request.env.user.has_group('base.group_user'):
            result['show_effect'] = request.env['ir.config_parameter'].sudo().get_param('base_setup.show_effect')
        return result
