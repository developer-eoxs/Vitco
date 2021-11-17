# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)

Confirmation = [('delivery', 'Delivery'),('verbal', 'Verbal'),]

PackDeliveryConfirmation = [
    ('1', 'Delivery Confirmation '),
    ('2', 'Delivery Confirmation Signature Required'),
    ('3', 'Delivery Confirmation Adult Signature Required'),
]

Boolean = [('yes', 'Yes'),('no', 'NO')]

class ChooseDeliveryPackage(models.TransientModel):
    _inherit = "choose.delivery.package"
    ups_delivery_confirmation = fields.Selection(
        selection=PackDeliveryConfirmation, string='Delivery Confirmation')
    def get_shipping_fields(self):
        return super(ChooseDeliveryPackage,self).get_shipping_fields()+['ups_delivery_confirmation']


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"
    ups_delivery_confirmation = fields.Selection(
        selection=PackDeliveryConfirmation, string='Delivery Confirmation')


class ProductPackage(models.Model):
    _inherit = 'product.package'
    delivery_type = fields.Selection(
        selection_add=[('ups', 'UPS')]
    )


class ProductPackaging(models.Model):
    _inherit = 'product.packaging'
    package_carrier_type = fields.Selection(selection_add=[('ups', 'UPS')])


class ShippingUps(models.Model):
    _inherit = "delivery.carrier"
    delivery_type = fields.Selection(
        selection_add=[('ups', 'UPS')]
    )
    ups_service_type = fields.Many2one(
        comodel_name='delivery.carrier.ups.service', 
        string='UPS Service'
    )
    ups_pickup_type = fields.Many2one(
        comodel_name='delivery.carrier.ups.pickup', 
        string='UPS Pickup'
    )
    ups_rate_negotiation = fields.Selection(
        selection=Boolean, 
        string='Rate Negotiation', 
        default='no'
    )
    ups_delivery_confirmation = fields.Selection(
        selection=PackDeliveryConfirmation,
        string='Default Delivery Confirmation'
    )
    ups_access_license_no = fields.Char(
        string='License Number',
    )
    ups_user_id = fields.Char(
        string='UPS User ID',
    )
    ups_shipper_no = fields.Char(
        string='Shipper Number',
    )
    ups_password = fields.Char(
        string='UPS Password',
    )
    ups_return_service_type = fields.Many2one(
        comodel_name = "delivery.carrier.ups.return.service",
        string = "UPS Return Service Type"
        )
    
    # @api.model
    # def _get_config(self,key):
    #     if key=='ups.config.settings':
    #         data  = self.read(['ups_access_license_no','ups_user_id','ups_shipper_no','ups_password','prod_environment'])[0]
    #         data['ups_enviroment'] ='production' if data['prod_environment'] else  'test'  
    #         _logger.info("==%r===="%data)
    #         return data
    #     return super(ShippingUps,self)._get_config(key)
    

class ShippingupsService(models.Model):
    _name = "delivery.carrier.ups.service"
    _description = "Delivery Carrier Ups Service"
    name = fields.Char(string="Name", required=1)
    code = fields.Char(string="Code", required=1)
    label_height = fields.Integer(
        string='Height',
        default =6,
        required=1
    )
    label_width = fields.Integer(
        string='Width',
        default =4,
        required=1
    )


class WKShippingupsPickup(models.Model):
    _name = "delivery.carrier.ups.pickup"
    _description = "Delivery Carrier Ups Pickup"
    name = fields.Char(string="Name", required=1)
    code = fields.Char(string="Code", required=1)


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    ups_shipment_number = fields.Char(
        string='UPS Shipment Identification Number', copy=False)
    
    wk_shipment_description = fields.Text(string="UPS Shipment Description")
    ups_return_service = fields.Many2one(comodel_name = "delivery.carrier.ups.return.service")

    # code = fields.Selection([
    #     ('incoming', 'Vendors'),
    #     ('outgoing', 'Customers'),
    #     ('internal', 'Internal')], related='picking_type_id.code',
    #     readonly=True)

    @api.onchange("delivery_type")
    def funk(self):
        self.ups_return_service = self.carrier_id.ups_return_service_type.id

class UPSReturnService(models.Model):
    _name = "delivery.carrier.ups.return.service"
    _description = "Delivery Carrier Ups Return Service"
    name = fields.Char(string="Name", required=1)
    code = fields.Char(string="Code", required=1)