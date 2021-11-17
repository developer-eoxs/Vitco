{
    'name': "Product Custom Steel",
    'summary': """Product Custom Steel""",
    'description': """
    """,
    'author': "OdoxSofthub",
    'website': "http://www.odoxsofthub.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Test',
    'version': '0.1.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'sale', 'purchase', 'stock', 'sale_management', 'utm', 'crm',
                'sale_order_lot_selection', 'stock_restrict_lot','account','sale_stock','odx_steel_production','report_xlsx'],

    # always loaded
    'data': [
        # 'views/login_restriction.xml',
        'security/ir.model.access.csv',
        'views/res_users.xml',
        'data/sequence.xml',
        'data/mail_template_sales.xml',
        'data/gauge_master_data.xml',
        'views/product_view.xml',
        'views/purchase_view.xml',
        'views/res_partner_view.xml',
        'views/surface_finish_view.xml',
        'views/stock_picking_view.xml',
        'views/stock_lot_view.xml',
        'views/stock_lot_pivot_view.xml',
        'views/stock_move_line.xml',
        'views/sale_order_view.xml',
        'views/sale_order_optional_ids.xml',
        'views/portal_template.xml',
        'views/sale_portal_template.xml',
        'views/crm_lead_views.xml',
        'views/stock_quant_view.xml',
        'views/pricelist_view.xml',
        'views/stock_inventory_line.xml',
        'views/purchase_offer_view.xml',
        'views/account_move.xml',
        'views/crm.xml',
        'views/rfq_report.xml',
        'views/transfer_view.xml',
        'views/master.xml',
        'views/additional_specs.xml',
        'report/barcode_generator_lot.xml',
        'report/barcode_lot.xml',
        'report/barcode_picking.xml',
        'report/sale_report_template_custom.xml',
        'report/bol_report.xml',
        'report/bol_report_action.xml',
        'wizard/stock_inventory.xml',
        'wizard/options_sale_wizard.xml',
        'wizard/price_update_wizard.xml',
        'wizard/production_wizard.xml',
        'wizard/import_offer_wizard.xml',
        'wizard/purchase_line_wizard.xml',
        'wizard/sale_report.xml',

    ],
}
