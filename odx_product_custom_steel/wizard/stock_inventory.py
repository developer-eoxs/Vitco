import time
import datetime
import tempfile
import binascii
import xlrd
import io

from stdnum.exceptions import ValidationError

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import date, datetime, timedelta
# import datetime
from odoo.exceptions import Warning, UserError
from odoo import models, fields, exceptions, api, _
import logging
import time

_logger = logging.getLogger(__name__)

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


# class StockInventory(models.Model):
#     _inherit = "stock.inventory"
#
#     custom_name = fields.Char(string="Name")
#
# class InventoryLine(models.Model):
#     _inherit = "stock.inventory.line"
#
#     difference_qty = fields.Float('Difference', compute='_compute_difference_qty',
#                                   help="Indicates the gap between the product's theoretical quantity and its newest quantity.",
#                                   readonly=True, digits='Product Unit of Measure', search="_search_difference_qty")
#
#     @api.depends('product_qty', 'theoretical_qty')
#     def _compute_difference_qty(self):
#         for line in self:
#             line.difference_qty = line.product_qty


class gen_stock_order(models.TransientModel):
    _name = "gen.stock.order"

    file_to_upload = fields.Binary('File')
    import_option = fields.Selection([('xls', 'XLS File'), ('csv', 'CSV File')], string='Select', default='xls')
    sample_field = fields.Char(string="Sample")

    def find_company(self, company):
        comp_obj = self.env['res.company']
        company_id = comp_obj.search([('name', '=', company)])
        if company_id:
            return company_id

    def check_product(self, default_code):
        product = default_code.split('.')[0]
        product_ids = self.env['product.product'].search([('default_code', '=', product)])

        if product_ids:
            product_id = product_ids[0]
            return product_id
        else:
            raise Warning(_('Wrong Product %s') % default_code)

    def check_product_category(self, default_code):

        product = default_code.split('.')[0]
        product_ids = self.env['product.product'].search([('default_code', '=', product)])
        if product_ids:
            product_id = product_ids[0]
            return product_id.categ_id
        else:
            raise Warning(_('Wrong Product %s') % default_code)

    def get_vendor(self, vendor, mill_sr_no, mill):
        mill_id = mill.split('.')[0]
        new_partner = self.env['res.partner'].search([('id', '=', mill_id)])
        # partner_obj = self.env['res.partner']
        # new_partner = partner_obj.create({
        #     'name': vendor,
        #     'vendor_serial_number': mill_sr_no,
        #     'child_ids': [(0, 0, {
        #         'name': mill,
        #         'type': 'delivery',
        #     })]
        # })
        if new_partner:
            return new_partner

    def find_location(self, location, company):
        comp_obj = self.env['res.company']
        company_id = comp_obj.search([('name', '=', company)])

        location = self.env['stock.location'].search([('name', '=', location), ('company_id', '=', company_id.id)])

        if location:
            return location

    def get_formatted_date(self, date_received):
        if date_received:
            date_rec = datetime.strptime(str(date_received), "%d/%m/%Y").strftime("%Y-%m-%d")

            return date_rec

    def make_stock_lot(self, values):
        mat = ''
        length = 0
        # bill_lading = heat_no = tag_no = part_no = lift_no = ''
        default_code = values.get('default_code')
        vendor = values.get('vendor')
        mill_sr_no = values.get('mill_sr_no')
        mill = values.get('mill')
        date_recieved = values.get('date_received')
        date_removed = values.get('date_removed')
        category_id = self.check_product_category(default_code)
        vendor_id = self.get_vendor(vendor, mill_sr_no, mill)
        stock_lot_obj = self.env['stock.production.lot']
        # sequence = self.env['ir.sequence'].next_by_code('stock.lot.serial.custom')
        sequence = values.get('coil_number')
        company_id = self.find_company(values.get('company'))
        date_rec_formatted = self.get_formatted_date(date_recieved)
        product_id = self.check_product(default_code)
        length = float(values.get('length_in'))

        bill_lading = values.get('bill_of_lading')
        heat_no = values.get('heat_number')
        tag_no = values.get('tag_number')
        part_no = values.get('part_number')
        lift_no = values.get('lift_number')

        heat_no_pr1 = values.get('heat_number_pr1')
        tag_no_pr1 = values.get('tag_number_pr1')
        part_no_pr1 = values.get('part_number_pr1')
        lift_no_pr1 = values.get('lift_number_pr1')

        if bill_lading:
            bill_lading = bill_lading.split('.')[0]

        if heat_no:
            heat_no = heat_no.split('.')[0]
        if tag_no:
            tag_no = tag_no.split('.')[0]
        if part_no:
            part_no = part_no.split('.')[0]
        if lift_no:
            lift_no = lift_no.split('.')[0]

        if heat_no_pr1:
            heat_no_pr1 = heat_no_pr1.split('.')[0]
        if tag_no_pr1:
            tag_no_pr1 = tag_no_pr1.split('.')[0]
        if part_no_pr1:
            part_no_pr1 = part_no_pr1.split('.')[0]
        if lift_no_pr1:
            lift_no_pr1 = lift_no_pr1.split('.')[0]

        if length > 0:
            mat = 'sheets'
        else:
            mat = 'coil'

        if product_id:
            line = stock_lot_obj.create({
                'name': str(sequence),
                'product_id': product_id.id,
                'sub_category_id': category_id.id,
                'category_id': category_id.parent_id.id,
                'company_id': company_id.id or self.env.company.id,
                'bill_of_lading': bill_lading,
                'vendor_id': vendor_id.parent_id.id if vendor_id.parent_id else vendor_id.id,
                'vendor_location_id': vendor_id.id,
                'vendor_serial_number': mill_sr_no,
                # 'vendor_serial_number': vendor_id.vendor_serial_number,
                # 'product': line[4],
                # 'location': line[4],
                'width_in': values.get('width_in'),
                'width_mm': values.get('width_mm'),
                'thickness_in': values.get('thickness_in'),
                'thickness_mm': values.get('thickness_mm'),
                'thickness_spec': values.get('thickness_spec'),
                'length_in': values.get('length_in'),
                'length_mm': values.get('length_mm'),
                'weight_lb': values.get('weight_lb'),
                'weight_kg': values.get('weight_kg'),
                'piw': values.get('piw'),
                'rockwell': values.get('rockwell'),
                'yield_mpa': values.get('yield_mpa'),
                'yield_psi': values.get('yield_psi'),
                'yield_ksi': values.get('yield_ksi'),
                'elongation': values.get('elongation'),
                'tensile_mpa': values.get('tensile_mpa'),
                'tensile_psi': values.get('tensile_psi'),
                'tensile_ksi': values.get('tensile_ksi'),
                'date_received': date_rec_formatted,
                # 'date_removed': date_rem,
                'po_number': values.get('po_number'),
                'internet_serial': values.get('internet_serial'),
                'packing_slip_no': values.get('packing_slip_no'),
                'comp_c': values.get('comp_c'),
                'comp_mn': values.get('comp_mn'),
                'comp_p': values.get('comp_p'),
                'comp_s': values.get('comp_s'),
                'comp_si': values.get('comp_si'),
                'comp_al': values.get('comp_al'),
                'comp_cr': values.get('comp_cr'),
                'comp_nb': values.get('comp_nb'),
                'comp_ti': values.get('comp_ti'),
                'comp_ca': values.get('comp_ca'),
                'comp_n': values.get('comp_n'),
                'comp_ni': values.get('comp_ni'),
                'comp_cu': values.get('comp_cu'),
                'comp_v': values.get('comp_v'),
                'comp_b': values.get('comp_b'),
                'comp_co': values.get('comp_co'),
                'comp_mo': values.get('comp_mo'),
                'comp_sn': values.get('comp_sn'),

                'pass_oil': values.get('pass_oil'),
                'finish': values.get('finish'),
                'temper': values.get('temper'),
                'category': values.get('category'),
                'coating': values.get('coating'),
                'heat_number': heat_no,
                'lift_number': lift_no,
                'part_number': part_no,
                'tag_number': tag_no,

                'heat_number_pr1': heat_no_pr1,
                'lift_number_pr1': lift_no_pr1,
                'part_number_pr1': part_no_pr1,
                'tag_number_pr1': tag_no_pr1,
                'grade': values.get('grade'),
                'quality': values.get('quality'),
                'material_type': mat,

            })

        if line:
            line._onchange_width()
            line._onchange_thickness()
            line._onchange_length()
            # line._onchange_yield()
            # line._onchange_tensile()
            return line

    def make_stock_line(self, values, stock_id):
        sale_line_obj = self.env['stock.inventory.line']
        location = self.find_location(values.get('location'), values.get('company'))
        print(location)
        if values.get('default_code'):
            default_code = values.get('default_code')
            if self.check_product(default_code) != None:
                product_id = self.check_product(default_code)
                lot_id = self.make_stock_lot(values)
                if product_id:
                    line = sale_line_obj.create({
                        'product_id': product_id.id,
                        'product_qty': values.get('weight_lb'),
                        'location_id': location.id,
                        'inventory_id': stock_id.id,
                        'prod_lot_id': lot_id.id,

                    })

        return values

    def make_stock_inventory(self, values):
        stock_obj = self.env['stock.inventory']
        company_id = self.find_company(values.get('company'))
        if company_id:
            company = company_id.id
        else:
            company = False
            # company = values.get('company')

        stock_search = False
        if values.get('name'):
            stock_search = stock_obj.search([
                ('name', '=', values.get('name'))])

        if stock_search:
            stock_search = stock_search[0]
            stock_id = stock_search
        else:
            stock_id = stock_obj.create({
                'name': values.get('name'),
                'company_id': company,
                # 'company_id': company_id.id or False,
            })
        line = self.make_stock_line(values, stock_id)
        return stock_id

    def import_sale_order(self):
        if self.import_option == 'csv':

            keys = ['name', 'company', 'default_code', 'quantity', 'location', 'coil_number', 'bill_of_lading',
                    'product', 'sub_product', 'width_in', 'width_mm', 'thickness_in',
                    'thickness_mm', 'thickness_spec', 'length_in', 'length_mm', 'weight_lb', 'weight_kg', 'heat_number',
                    'lift_number', 'part_number', 'tag_number', 'grade',
                    'quality', 'piw', 'rockwell', 'yield_mpa', 'yield_psi', 'yield_ksi', 'elongation', 'tensile_mpa',
                    'tensile_psi', 'tensile_ksi', 'date_removed', 'date_received', 'vendor', 'mill',
                    'po_number', 'internet_serial', 'packing_slip_no', 'comp_c', 'comp_mn', 'comp_p', 'comp_s',
                    'comp_si', 'comp_al', 'comp_cr', 'comp_nb', 'comp_ti', 'comp_ca',
                    'comp_n', 'comp_ni', 'comp_cu', 'comp_v', 'comp_b', 'comp_co', 'comp_mo', 'comp_sn',
                    'pass_oil', 'finish', 'temper', 'category', 'coating', 'mill_sr_no', 'heat_number_pr1',
                    'lift_number_pr1', 'part_number_pr1', 'tag_number_pr1', ]
            try:
                csv_data = base64.b64decode(self.file_to_upload)
                data_file = io.StringIO(csv_data.decode("utf-8"))
                data_file.seek(0),
                file_reader = []
                csv_reader = csv.reader(data_file, delimiter=',')
                file_reader.extend(csv_reader)
            except Exception:
                raise exceptions.Warning(_("Invalid file!"))
            values = {}
            lines = []
            for i in range(len(file_reader)):
                field = map(str, file_reader[i])
                values = dict(zip(keys, field))
                if values:
                    if i == 0:
                        continue
                    else:
                        res = self.make_stock_inventory(values)
        else:
            try:
                fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                fp.write(binascii.a2b_base64(self.file_to_upload))
                fp.seek(0)
                values = {}
                workbook = xlrd.open_workbook(fp.name)
                sheet = workbook.sheet_by_index(0)
            except Exception:
                raise exceptions.ValidationError(_("Invalid file!"))
            lines = []
            for row_no in range(sheet.nrows):
                val = {}
                if row_no <= 0:
                    fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
                else:
                    line = list(
                        map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value),
                            sheet.row(row_no)))

                    if len(line) < 68:
                        raise UserError(
                            _("Please Check the import template.Some of the required columns are not present "))
                    values = {
                        'name': line[0],
                        'company': line[1],
                        'default_code': line[2],
                        'quantity': line[3],
                        'location': line[4],
                        'coil_number': line[5],
                        'bill_of_lading': line[6],
                        # 'product': line[7],
                        # 'sub_product': line[8],
                        'width_in': line[9],
                        'width_mm': line[10],
                        'thickness_in': line[11],
                        'thickness_mm': line[12],
                        'thickness_spec': line[13],
                        'length_in': line[14],
                        'length_mm': line[15],
                        'weight_lb': line[16],
                        'weight_kg': line[17],
                        'heat_number': line[18],
                        'lift_number': line[19],
                        'part_number': line[20],
                        'tag_number': line[21],
                        'grade': line[22],
                        'quality': line[23],
                        'piw': line[24],
                        'rockwell': line[25],
                        'yield_mpa': line[26],
                        'yield_psi': line[27],
                        'yield_ksi': line[28],

                        'elongation': line[29],
                        'tensile_mpa': line[30],
                        'tensile_psi': line[31],
                        'tensile_ksi': line[32],

                        'date_removed': line[33],
                        'date_received': line[34],
                        'vendor': line[35],
                        'mill': line[36],
                        'po_number': line[37],
                        'internet_serial': line[38],
                        'packing_slip_no': line[39],
                        'comp_c': line[40],
                        'comp_mn': line[41],
                        'comp_p': line[42],
                        'comp_s': line[43],
                        'comp_si': line[44],
                        'comp_al': line[45],
                        'comp_cr': line[46],
                        'comp_nb': line[47],
                        'comp_ti': line[48],
                        'comp_ca': line[49],
                        'comp_n': line[50],
                        'comp_ni': line[51],
                        'comp_cu': line[52],
                        'comp_v': line[53],
                        'comp_b': line[54],
                        'comp_co': line[55],
                        'comp_mo': line[56],
                        'comp_sn': line[57],
                        'pass_oil': line[58],
                        'finish': line[59],
                        'temper': line[60],
                        'category': line[61],
                        'coating': line[62],
                        'mill_sr_no': line[63],
                        'heat_number_pr1': line[64],
                        'lift_number_pr1': line[65],
                        'part_number_pr1': line[66],
                        'tag_number_pr1': line[67],
                    }

                    res = self.make_stock_inventory(values)
                    # self.sample_field = line[0] if line[0] else self.sample_field

    # keys = ['name', 'company', 'default_code', 'quantity', 'location']
    #     try:
    #         csv_data = base64.b64decode(self.file_to_upload)
    #         data_file = io.StringIO(csv_data.decode("utf-8"))
    #         data_file.seek(0),
    #         file_reader = []
    #         csv_reader = csv.reader(data_file, delimiter=',')
    #         file_reader.extend(csv_reader)
    #     except Exception:
    #         raise exceptions.Warning(_("Invalid file!"))
    #     values = {}
    #     lines = []
    #     for i in range(len(file_reader)):
    #         field = map(str, file_reader[i])
    #         values = dict(zip(keys, field))
    #         if values:
    #             if i == 0:
    #                 continue
    #             else:
    #                 res = self.make_stock_inventory(values)
    # else:
