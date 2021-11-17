# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################

import binascii
import base64
import logging
import xml.etree.ElementTree as etree
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import dump
from xml.dom import minidom
from urllib.parse import  quote_plus
_logger = logging.getLogger(__name__)
try:
    from urllib3.exceptions import HTTPError
    import urllib3
except Exception as e:
    _logger.error("#WKDEBUG-1  python  urllib3 library not installed .")
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.addons.odoo_shipping_service_apps.tools import wk_translit as WT
from odoo.addons.odoo_shipping_service_apps.tools import ensure_str as ES
import sys

def check_length(string):
    if(string and len(string)>35):return string[0:35]
    else:return string

class UPSAPI:
    APIEND = dict(
            test = dict(
                rate='https://www.ups.com/ups.app/xml/Rate',
                ship_confirm = 'https://wwwcie.ups.com/ups.app/xml/ShipConfirm',
                ship_accept = 'https://wwwcie.ups.com/ups.app/xml/ShipAccept',
                void = 'https://wwwcie.ups.com/ups.app/xml/Void' ,
                label_recovery = "https://wwwcie.ups.com/ups.app/xml/LabelRecovery"
            ),
            production = dict(
                rate='https://www.ups.com/ups.app/xml/Rate',
                ship_confirm = 'https://onlinetools.ups.com/ups.app/xml/ShipConfirm',
                ship_accept = 'https://onlinetools.ups.com/ups.app/xml/ShipAccept',
                void = 'https://onlinetools.ups.com/ups.app/xml/Void',
                label_recovery = "https://onlinetools.ups.com/ups.app/xml/LabelRecovery"
            )
    )

    @classmethod
    def get_tracking_link(cls,tracknum):
        ups_tracking_url = "http://wwwapps.ups.com/etracking/tracking.cgi?tracknum="
        tracking_nums = list(map(lambda x: x+"%0D%0A", tracknum.split(sep=',')))
        ups_tracking_url+=''.join(tracking_nums)
        return ups_tracking_url

    @staticmethod
    def check_error(root):
        error = False
        for description in root.getiterator("ResponseStatusDescription"):
            if description.text != 'Success':
                error = True
                break
        if error:return root.findtext('Response/Error/ErrorDescription')

    @staticmethod
    def add_text(elem, text):
        elem.text = text
        return elem

    @staticmethod
    def prettify(elem):
        rough_string = ElementTree.tostring(elem, 'utf-8')
        # reparsed = minidom.parseString(rough_string)
        # return reparsed.toprettyxml(indent="\t")
        return rough_string

    def __init__(self, *args, **kwargs):
        self.ups_access_license_no = kwargs.get('ups_access_license_no')
        self.ups_user_id = kwargs.get('ups_user_id')
        self.ups_password = kwargs.get('ups_password')
        self.ups_shipper_no = kwargs.get('ups_shipper_no')
        self.ups_currency = kwargs.get('ups_currency')
        self.ups_enviroment = kwargs.get('ups_enviroment','test')


    def add_code(self,elem, code):
        self.add_text(SubElement(elem, 'Code'),code)
        return elem

    def contruct_access_request(self):
        AccessRequest = Element("AccessRequest", attrib={"xml:lang": "en-US"})
        self.add_text(SubElement(AccessRequest, 'AccessLicenseNumber'),self.ups_access_license_no)
        self.add_text(SubElement(AccessRequest, 'UserId'),self.ups_user_id)
        self.add_text(SubElement(AccessRequest, 'Password'),self.ups_password)
        self.add_text(SubElement(AccessRequest, 'CurrencyCode'),self.ups_currency)
        return AccessRequest

    def send_request(self,request_for,request_xml):
        try:
            access_request = self.contruct_access_request()
            access_request_xml = self.prettify(access_request)
            http = urllib3.PoolManager()
            api_end = self.APIEND.get(self.ups_enviroment or 'test').get(request_for)
            _logger.info("UPS api_end=%r=="%(api_end))
            response = http.urlopen('POST',api_end, body=access_request_xml+request_xml)
            root = etree.fromstring(response.data)
            error = self.check_error(root)
            return dict(success = 0 if error else 1, error_message=error,root=root)
        except Exception as e:
            _logger.warning(
                "#WKDEBUG---UPS %r Exception-----%r---------"%(request_for,e))
            return dict(success = False, error_message=e)

    def contruct_request(self,request_for):
        Request =Element('Request')
        self.add_text(SubElement(Request, 'RequestAction'),request_for)
        self.add_text(SubElement(Request, 'RequestOption'),'validate')
        TransactionReference = SubElement(Request, 'TransactionReference')
        self.add_text(SubElement(TransactionReference, 'CustomerContext'),request_for)
        return Request

    def contruct_customer_classification(self,pickup_code):
        if pickup_code in ['06', '07', '19', '20']:
            code = '04'
        elif pickup_code == '01':
            code = '01'
        elif pickup_code == '03':
            code = '00'
        else:
            raise ValidationError('Please Check the Pick Up Code')
        CustomerClassification =Element('CustomerClassification')
        self.add_code(CustomerClassification,code)
        return CustomerClassification

    def construct_address(self,addr_type,data):
        AddressRoot = Element(addr_type)
        self.add_text(SubElement(AddressRoot, 'Name'),check_length(data.get('name')))
        self.add_text(SubElement(AddressRoot, 'PhoneNumber'),data.get('phone'))
        self.add_text(SubElement(AddressRoot, 'CompanyName'), (check_length(data.get('company_name')) and check_length(data.get('company_name'))) or (check_length(data.get('name')) and check_length(data.get('name'))))
        self.add_text(SubElement(AddressRoot, 'AttentionName'),check_length(data.get('name')))
        if addr_type=='Shipper':
            self.add_text(SubElement(AddressRoot, 'ShipperNumber'),self.ups_shipper_no)
        Address = SubElement(AddressRoot, 'Address')
        self.add_text(SubElement(Address, 'AddressLine1'),check_length(data.get('street')))
        self.add_text(SubElement(Address, 'AddressLine2'),check_length(data.get('street2')))
        self.add_text(SubElement(Address, 'City'),data.get('city'))
        self.add_text(SubElement(Address, 'StateProvinceCode'),data.get('state_code'))
        self.add_text(SubElement(Address, 'PostalCode'),data.get('zip'))
        self.add_text(SubElement(Address, 'CountryCode'),data.get('country_code'))
        return AddressRoot

    def construct_package_options_xml(self,root_node, data):
        if data.get('cover_amount') or data.get('ups_delivery_confirmation'):
            PackageServiceOptions = SubElement(root_node, 'PackageServiceOptions')
            if data.get('cover_amount') and data.get('currency'):
                InsuredValue = SubElement(PackageServiceOptions, 'InsuredValue')
                self.add_text(SubElement(InsuredValue, 'CurrencyCode'),data.get('currency','NGN'))
                self.add_text(SubElement(InsuredValue, 'MonetaryValue'),'%s'%data.get('cover_amount'))

            if data.get('ups_delivery_confirmation'):
                DeliveryConfirmation = SubElement(PackageServiceOptions, 'DeliveryConfirmation')
                self.add_text(SubElement(DeliveryConfirmation, 'DCISType'),'%s'%data.get('ups_delivery_confirmation'))
        return root_node

    def construct_package_xml(self, data):
        Package = Element('Package')
        self.add_code(SubElement(Package, 'PackagingType'),data.get('packaging_code'))
        self.add_text(SubElement(Package, 'Description'),data.get('name'))

        PackageWeight = SubElement(Package, 'PackageWeight')
        self.add_code(SubElement(PackageWeight, 'UnitOfMeasurement'),data.get('weight_unit'))
        self.add_text(SubElement(PackageWeight, 'Weight'),'%s'%(data.get('weight')))

        Dimensions = SubElement(Package, 'Dimensions')
        self.add_text(SubElement(Dimensions, 'Height'),'%s'%int(round(data.get('height'))))
        self.add_text(SubElement(Dimensions, 'Width'),'%s'%int(round(data.get('width'))))
        self.add_text(SubElement(Dimensions, 'Length'),'%s'%int(round(data.get('length'))))
        self.construct_package_options_xml(Package, data)
        return Package

    def  contruct_rate_shipment(self,data,shipper_data,recipient_data, picking):
        Shipment = Element('Shipment')
        TaxInformationIndicator = SubElement(Shipment, 'TaxInformationIndicator')
        Shipment.append(self.construct_address(addr_type='Shipper',data=shipper_data))
        Shipment.append(self.construct_address(addr_type='ShipTo',data=recipient_data))
        Shipment.append(self.construct_address(addr_type='ShipFrom',data=shipper_data))

        self.add_text(SubElement(Shipment, 'Description'),picking and picking.wk_shipment_description or "")

        if picking and picking.picking_type_code == "incoming":
            self.add_code(SubElement(Shipment, 'ReturnService'),picking.ups_return_service.code)

        self.add_code(SubElement(Shipment, 'Service'),data.get('service_code'))
        PaymentInformation = SubElement(Shipment, 'PaymentInformation')
        Prepaid =  SubElement(PaymentInformation, 'Prepaid')
        BillShipper =   SubElement(Prepaid, 'BillShipper')
        self.add_text(SubElement(BillShipper, 'AccountNumber'),self.ups_shipper_no)
        if data.get('ups_rate_negotiation') == 'yes':
            RateInformation= SubElement(Shipment, 'RateInformation')
            NegotiatedRatesIndicator = SubElement(RateInformation, 'NegotiatedRatesIndicator')
        return Shipment

    def contruct_rate_req(self,data):
        root_node = Element(data.get('request'), attrib={"xml:lang": "en-US"})
        root_node.append(self.contruct_request(data.get('request_for')))
        root_node.append(self.contruct_customer_classification(data.get('pickup_code')))
        self.add_code(SubElement(root_node, 'CurrencyCode'),data.get('currency_code'))

        PickupType = SubElement(root_node, 'PickupType')
        self.add_text(SubElement(PickupType, 'Description'),data.get('pickup_name'))
        self.add_code(PickupType,data.get('pickup_code'))
        return root_node


    def send_rate_request(self,data):
        response = self.send_request('rate',data)
        if response.get('error_message'):return response
        root = response.get('root')
        NegotiatedRates = root.find('RatedShipment/NegotiatedRates')
        if NegotiatedRates != None:
            currency = NegotiatedRates.find(
                'NetSummaryCharges/GrandTotal/CurrencyCode').text
            price = float(NegotiatedRates.find(
                'NetSummaryCharges/GrandTotal/MonetaryValue').text)
        else:
            currency = root.find(
                'RatedShipment/TransportationCharges/CurrencyCode').text
            price = float(
                root.find('RatedShipment/TransportationCharges/MonetaryValue').text)
        return dict(price = price, currency=currency,success=True)


    def contruct_ship_req(self,shipment_digest):
        root_node = Element('ShipmentAcceptRequest', attrib={"xml:lang": "en-US"})
        root_node.append(self.contruct_request('ShipAccept'))
        self.add_text(SubElement(root_node, 'ShipmentDigest'),shipment_digest)
        return root_node

    def send_shipment_confirm(self,data):
        response =  self.send_request('ship_confirm',data)
        if response.get('error_message'):return response
        root = response.get('root')


        for digest_img in root.iter('ShipmentDigest'):
            response = digest_img.text
            return dict(shipment_digest=digest_img.text, success=True)

    def send_ship_request(self,data):
        response =  self.send_request('ship_accept',data)
        if response.get('error_message'):
            return response
        
        root = response.get('root')
   
        NegotiatedRates = root.find('RatedShipment/NegotiatedRates')
        ShipmentCharges = root.find('ShipmentResults/ShipmentCharges')
        currency = None
        amount = None
        if NegotiatedRates != None:
            currency = NegotiatedRates.find('NetSummaryCharges/GrandTotal/CurrencyCode').text
            amount = float(NegotiatedRates.find('NetSummaryCharges/GrandTotal/MonetaryValue').text)
        else:
            currency = ShipmentCharges.find('TotalCharges/CurrencyCode').text
            amount = float(ShipmentCharges.find('TotalCharges/MonetaryValue').text)

        shipment_number_ids = []
        weight = 0
        for shipment_number, weight in zip(root.getiterator("ShipmentIdentificationNumber"), root.getiterator("Weight")):
            shipment_number_ids+=[shipment_number.text]
            weight = weight.text
        tracking_result = dict()

        for image, tracking_number in zip(root.getiterator("GraphicImage"), root.getiterator("TrackingNumber")):
            tracking_result[tracking_number.text]= ('UPS' + str(tracking_number.text) + '.gif', binascii.a2b_base64(image.text))
        return dict(
            shipment_number=shipment_number_ids,weight=weight,
            currency =currency , amount =amount,
            tracking_result=tracking_result
        )

    def contruct_void_req(self,data):
        root_node = Element('VoidShipmentRequest')
        root_node.append(self.contruct_request('Void'))
        self.add_text(SubElement(root_node, 'ShipmentIdentificationNumber'),data.get('ups_shipment_number'))
        # self.add_text(SubElement(void_shipment, 'ShipmentIdentificationNumber'),data.get('ups_shipment_number'))
        # for tracking_number in data.get('carrier_tracking_ref').split(','):
        #     self.add_text(SubElement(void_shipment, 'TrackingNumber'),tracking_number)
        return root_node

    def send_void_request(self,data):
        response =  self.send_request('void',data)
        if response.get('error_message'):return response
        root = response.get('root')
        tracking_number_ids = []
        if root.getiterator("TrackingNumber"):
            for tracking_number in root.getiterator("TrackingNumber"):
                tracking_number_ids+=[tracking_number.text]
        return dict(tracking_number_ids=tracking_number_ids,success=True)

class UPSDeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    def _compute_can_generate_return(self):
        for carrier in self:
            carrier.can_generate_return = True


    @api.model
    def ups_construct_package(self,sdk,root_node, order=None, picking=None, currency=None):
        self.wk_validate_data(order=order, pickings=picking)
        packaging_obj = self.env['product.packaging']

        weight_unit = self.delivery_uom + 'S' if self.delivery_uom else None
        if order:
            package_items = self.wk_get_order_package(order=order)
            items = self.wk_group_by('packaging_id', package_items)
            for order_packaging_id, wk_package_ids in items:
                packaging_id = packaging_obj.browse(order_packaging_id)
                packaging_code = packaging_id.shipper_package_code
                for package_id in wk_package_ids:
                    package_data = dict(
                        weight_unit=weight_unit,
                        currency=currency,
                        name=order.name,
                        description=order.name + ' ' + packaging_id.name,
                        ups_delivery_confirmation=self.ups_delivery_confirmation
                    )
                    package_data.update(package_id)
                    _logger.info("order package_data===%r====="%(package_data))
                    package_data['weight'] = self._get_api_weight(package_data.get('weight'))
                    package_data['packaging_code'] = packaging_code
                    root_node.append(sdk.construct_package_xml(package_data))
        elif picking:
            packaging_ids = self.wk_group_by_packaging(pickings=picking)
            total_package = 0
            for packaging_id, package_ids in packaging_ids.items():
                packaging_code = packaging_id.shipper_package_code
                total_package += len(package_ids)
                for package_id in package_ids:
                    package_data = dict(weight_unit=weight_unit,currency=currency,)
                    pck_data = package_id.read(
                        ['description', 'name', 'shipping_weight', 'cover_amount', 'ups_delivery_confirmation'])
                    pkg_data = package_id.read(['height', 'width', 'length'])
                    package_data.update(pck_data[0])
                    package_data.update(pkg_data[0])
                    _logger.info("package_data===%r====="%(package_data))
                    package_data['packaging_code'] = packaging_code
                    package_data['weight'] = self._get_api_weight(package_data.get('shipping_weight'))
                    root_node.append(sdk.construct_package_xml(package_data))
            picking.number_of_packages = total_package
        return root_node

    @api.model
    def ups_construct_request(self,sdk,currency_code,
        request,request_for,order=None,picking=False,label=None):

        pickup_type = self.ups_pickup_type
        service_type = self.ups_service_type
        root_node = sdk.contruct_rate_req(dict(
            request =request,request_for=request_for,
            currency_code=currency_code,
            pickup_code=pickup_type.code,
            pickup_name=pickup_type.name,
            ))
        shipment_data = dict(
            service_name = service_type.name,service_code = service_type.code,
            ups_rate_negotiation  =self.ups_rate_negotiation,num_pieces = 5 )
        if not label:
            shipper_data =self.get_shipment_shipper_address(order=order,picking=picking)
            recipient_data =  self.get_shipment_recipient_address(order=order,picking=picking)
        elif label:
            recipient_data =self.get_shipment_shipper_address(order=order,picking=picking)
            shipper_data =  self.get_shipment_recipient_address(order=order,picking=picking)
        shipment = sdk.contruct_rate_shipment(shipment_data,shipper_data,recipient_data, picking)
        self.ups_construct_package(sdk,shipment, order=order,  currency=currency_code,picking=picking)
        root_node.append(shipment)
        return root_node

    @api.model
    def ups_get_shipping_price(self, order):
        recipient = order.partner_shipping_id if order.partner_shipping_id else order.partner_id
        shipper = order.warehouse_id.partner_id
        currency_id = self.get_shipment_currency_id(order)
        currency_code = currency_id.name
        price = 0
        # config = self._get_config('ups.config.settings')
        config = self.wk_get_carrier_settings(['ups_access_license_no','ups_user_id','ups_shipper_no','ups_password','prod_environment'])
        config['ups_enviroment'] ='production' if config['prod_environment'] else  'test'    
        config['ups_currency'] = currency_code
        sdk = UPSAPI(**config)
        rate_req = self.ups_construct_request(
            sdk,currency_code,
            request = 'RatingServiceSelectionRequest',request_for='Rate',order=order
        )
        rate_req_xml = sdk.prettify(rate_req)
        response = sdk.send_rate_request(rate_req_xml)
        _logger.debug("===%r===="%(response))
        response['currency_id'] =currency_id
        return response


    @api.model
    def ups_rate_shipment(self, order):
        response = self.ups_get_shipping_price(order)
        _logger.debug("##########11order===%r==%r=="%(order,response))
        if not response.get('error_message'):response['error_message'] = None
        if not response.get('price'):response['price'] = 0
        if not response.get('warning_message'):response['warning_message'] = None
        if not response.get('success'):return response
        price = self.convert_shipment_price(response)
        response['price'] = price
        _logger.debug("##########22order===%r==%r=="%(order,response))
        return response


    @api.model
    def get_ups_shipment_digest(self,sdk, pickings, currency_code, label):
        response = None
        recipient = pickings.partner_id
        shipper = pickings.picking_type_id.warehouse_id.partner_id
        confirm_req = self.ups_construct_request(
            sdk,currency_code,
            request = 'ShipmentConfirmRequest',
            request_for='ShipConfirm',picking=pickings,label = label
        )
        confirm_req_xml = sdk.prettify(confirm_req)
        response = sdk.send_shipment_confirm(confirm_req_xml)
        shipment_digest = response.get('shipment_digest')
        if not(shipment_digest):
            raise ValidationError(response.get('error_message','No Shipment Digest Recive'))
        return shipment_digest



    def ups_send_shipping(self, pickings):
        for obj in self:
            result = {'exact_price': 0, 'weight': 0, "date_delivery": None,
                    'tracking_number': '', 'attachments': []}
            currency_id = obj.get_shipment_currency_id(pickings=pickings)
            currency_code = currency_id.name

            # config = obj._get_config('ups.config.settings')
            config = self.wk_get_carrier_settings(['ups_access_license_no','ups_user_id','ups_shipper_no','ups_password','prod_environment'])
            config['ups_enviroment'] ='production' if config['prod_environment'] else  'test'
            config['ups_currency'] = currency_code
            sdk = UPSAPI(**config)
            shipment_digest = obj.get_ups_shipment_digest(sdk, pickings, currency_code, label = False)
            if shipment_digest:
                ship_req = sdk.contruct_ship_req(shipment_digest)
                ship_req_xml = sdk.prettify(ship_req)
                response = sdk.send_ship_request(ship_req_xml)
                if response.get('error_message'):
                    raise ValidationError(response.get('error_message'))
                shipment_number = response.get('shipment_number')
                tracking_result = response.get('tracking_result')
                amount = response.get('amount')
                currency =  response.get('currency')
                if shipment_number:
                    shipment_number = ','.join(shipment_number)
                    if pickings.ups_shipment_number:
                        pickings.ups_shipment_number +=shipment_number
                    else:
                        pickings.ups_shipment_number =shipment_number

                result['weight'] = response.get('weight')
                if amount:
                    if currency_id.name == currency:
                        result['exact_price'] += amount
                    else:
                        currency = currency_id.search([('name', '=', currency)], limit=1)
                        result['exact_price'] += currency.compute(amount, currency_id)
                if tracking_result:
                    result['tracking_number'] = ','.join(tracking_result.keys())
                    result['attachments'] = list(tracking_result.values())

            return result


    @api.model
    def ups_get_tracking_link(self, picking):
        return UPSAPI.get_tracking_link(picking.carrier_tracking_ref)


    @api.model
    def ups_cancel_shipment(self, pickings):
        # config = self._get_config('ups.config.settings')
        currency_id = self.get_shipment_currency_id(pickings=pickings)
        currency_code = currency_id.name
        # config = self._get_config('ups.config.settings')
        config = self.wk_get_carrier_settings(['ups_access_license_no','ups_user_id','ups_shipper_no','ups_password','prod_environment'])
        config['ups_enviroment'] ='production' if config['prod_environment'] else  'test'
        config['ups_currency'] = currency_code
        sdk = UPSAPI(**config)
        picking = pickings.read(['ups_shipment_number','carrier_tracking_ref'])[0]
        void_req = sdk.contruct_void_req(picking)
        void_req_xml = sdk.prettify(void_req)
        response = sdk.send_void_request(void_req_xml)
        if response.get('success'):
            pickings.message_post(body='{} of Tracking reference is successfully voided'.format(
                response.get('tracking_number_ids')), subject="UPS Shipment Voided:")
            pickings.ups_shipment_number = False
        else:
            raise ValidationError( response.get('error_message') or 'UPS Void Shipment Feature Not Available Right Now Please Go through UPS Online for Void Shipment! .')


    @api.model
    def ups_get_return_label(self,pickings, tracking_number, origin_date):
        result = {'exact_price': 0, 'weight': 0, "date_delivery": None,
                  'tracking_number': '', 'attachments': []}
        currency_id = self.get_shipment_currency_id(pickings=pickings)
        currency_code = currency_id.name

        # config = self._get_config('ups.config.settings')
        config = self.wk_get_carrier_settings(['ups_access_license_no','ups_user_id','ups_shipper_no','ups_password','prod_environment'])
        config['ups_enviroment'] ='production' if config['prod_environment'] else  'test'
        config['ups_currency'] = currency_code
        sdk = UPSAPI(**config)
        shipment_digest = self.get_ups_shipment_digest(sdk, pickings, currency_code, label=True)
        if shipment_digest:
            ship_req = sdk.contruct_ship_req(shipment_digest)
            ship_req_xml = sdk.prettify(ship_req)
            response = sdk.send_ship_request(ship_req_xml)
            if response.get('error_message'):
                raise ValidationError(response.get('error_message'))
            shipment_number = response.get('shipment_number')
            tracking_result = response.get('tracking_result')
            amount = response.get('amount')
            currency =  response.get('currency')
            if shipment_number:
                shipment_number = ','.join(shipment_number)
                if pickings.ups_shipment_number:
                    pickings.ups_shipment_number +=shipment_number
                else:
                    pickings.ups_shipment_number =shipment_number

            result['weight'] = response.get('weight')
            if amount:
                if currency_id.name == currency:
                    result['exact_price'] += amount
                else:
                    currency = currency_id.search([('name', '=', currency)], limit=1)
                    result['exact_price'] += currency.compute(amount, currency_id)
            if tracking_result:
                result['tracking_number'] = ','.join(tracking_result.keys())
                result['attachments'] = list(tracking_result.values())

        pickings.carrier_price = result.get('exact_price')
        pickings.carrier_tracking_ref = result.get('tracking_number') and result.get('tracking_number').strip(',')
        pickings.label_genrated = True
        pickings.date_delivery = result.get('date_delivery')
        pickings.weight_shipment = float(result.get('weight'))
        msg = ("Return Shipment sent to carrier %s for expedition with tracking number %s") % (
            pickings.carrier_id.delivery_type, pickings.carrier_tracking_ref)

        my_attachments_ids = []

        for i in range(len(result['attachments'])):
            my_attachment = self.env['ir.attachment'].create({
                'datas': base64.b64encode(result['attachments'][i][1]),
                'name': self.get_return_label_prefix() + "-stock_picking_id-"+ str(pickings.id),
                'res_model': 'stock.picking',
                'res_id' : pickings.id 
            })

            my_attachments_ids.append(my_attachment.id)
        
        pickings.return_label_ids = my_attachments_ids

        pickings.message_post(
            body=msg,
            subject="Attachments of tracking",
            attachment_ids=my_attachments_ids
        )


