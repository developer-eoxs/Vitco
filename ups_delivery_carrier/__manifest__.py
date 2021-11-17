# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "UPS Shipping Integration",
  "summary"              :  """Integrate UPS shipping functionality directly within Odoo ERP applications to deliver increased logistical efficiencies.""",
  "category"             :  "Website/Shipping Logistics",
  "version"              :  "1.0.7",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "maintainer"           :  "Aditya Sharma",
  "website"              :  "https://store.webkul.com/Odoo-Website-UPS-Shipping-Integration.html",
  "description"          :  """http://webkul.com/blog/odoo-website-ups-shipping-integration/
  UPS Shipping API Integration as Odoo UPS Delivery Method .
  Provide Shipping Label Generation and Shipping Rate Calculator For Website as Well Odoo BackEnd""",
  "depends"              :  ['odoo_shipping_service_apps'],
  "data"                 :  [
                             'views/ups_delivery_carrier.xml',
                             'views/product_packaging.xml',
                             'security/ir.model.access.csv',
                             'data/data.xml',
                             'data/delivery_demo.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "price"                :  149,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
  "external_dependencies":  {'python': ['urllib3']},
}