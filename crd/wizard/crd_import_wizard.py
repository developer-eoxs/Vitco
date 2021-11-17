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


class ImportCrd(models.TransientModel):
    _name = "import.crd.wizard"

    file_to_upload = fields.Binary('File')
    import_option = fields.Selection([('xls', 'XLS File'), ('csv', 'CSV File')], string='Select', default='xls')
    sample_field = fields.Char(string="Sample")
    crd_id = fields.Many2one('customer.relation', string="Purchase Order")

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

    def make_customer_relation_line(self, values):
        crd_line_obj = self.env['customer.relation.lines']

        default_code = values.get('default_code')
        company_id = self.find_company(values.get('company'))
        category_id = self.check_product_category(default_code)
        product_id = self.check_product(default_code)

        self.crd_id.write({
            'crd_product_ids': [(0, 0, {
                'sub_category_id': category_id.id,
                'product_id': product_id.id,
                'company_id': self.env.company.id,
                'category_id': category_id.parent_id.id,
                'width_upper_in': values.get('width_upper_in'),
                'width_lower_in': values.get('width_lower_in'),
                'thickness_upper_in': values.get('thickness_upper_in'),
                'thickness_lower_in': values.get('thickness_lower_in'),

            })]
        })

    def import_crd_recieved(self):
        if self.import_option == 'csv':

            keys = ['category', 'sub_category', 'default_code', 'sub_product',
                    'width_lower_in', 'width_upper_in', 'thickness_lower_in', 'thickness_upper_in', ]
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
                        res = self.make_customer_relation_line(values)
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
                    #
                    if len(line) < 8:
                        raise UserError(
                            _("Please Check the import template.Some of the required columns are not present "))
                    values = {
                        # 'category': line[0],
                        # 'sub_product': line[1],
                        'default_code': line[2],
                        # 'default_code': line[3],
                        'width_lower_in': line[4],
                        'width_upper_in': line[5],
                        'thickness_lower_in': line[6],
                        'thickness_upper_in': line[7],
                    }

                    res = self.make_customer_relation_line(values)
