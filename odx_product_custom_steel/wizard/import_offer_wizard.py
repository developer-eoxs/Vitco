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


class ImportOffer(models.TransientModel):
    _name = "import.offer.wizard"

    file_to_upload = fields.Binary('File')
    import_option = fields.Selection([('xls', 'XLS File'), ('csv', 'CSV File')], string='Select', default='xls')
    sample_field = fields.Char(string="Sample")
    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Order")

    def make_purchase_offer(self, values):
        offer_obj = self.env['purchase.offer']
        batch = values.get('batch')
        if batch:
            batch = batch.split('.')[0]

        line = offer_obj.create({
            'name': values.get('name'),
            'bids': values.get('bids'),
            'product_group': values.get('product_group'),
            'material': values.get('material'),
            'batch': batch,
            'gauge': values.get('gauge'),
            'width_in': values.get('width_in'),
            'weight_lbs': values.get('weight_lbs'),
            'ordered_grade': values.get('ordered_grade'),
            'comment': values.get('comment'),
            'notes': values.get('notes'),
            'length_ft': values.get('length_ft'),
            'inner_dia': values.get('inner_dia'),
            'outer_dia': values.get('outer_dia'),
            'heat_number': values.get('heat_number'),

            'comp_c': values.get('comp_c'),
            'comp_mn': values.get('comp_mn'),
            'comp_p': values.get('comp_p'),
            'comp_s': values.get('comp_s'),
            'comp_si': values.get('comp_si'),
            'comp_al': values.get('comp_al'),
            'comp_al_total': values.get('comp_al_total'),
            'comp_ti': values.get('comp_ti'),
            'comp_nb': values.get('comp_nb'),
            'comp_b': values.get('comp_b'),
            'comp_cu': values.get('comp_cu'),
            'comp_as': values.get('comp_as'),
            'comp_co': values.get('comp_co'),
            'comp_cr': values.get('comp_cr'),
            'comp_mo': values.get('comp_mo'),
            'comp_n': values.get('comp_n'),
            'comp_ni': values.get('comp_ni'),
            'comp_pb': values.get('comp_pb'),
            'comp_v': values.get('comp_v'),

        })
        self.purchase_order_id.write({
            'offering_ids': [(0, 0, {
                'name': values.get('name'),
                'bids': values.get('bids'),
                'product_group': values.get('product_group'),
                'material': values.get('material'),
                'batch': batch,
                'gauge': values.get('gauge'),
                'width_in': values.get('width_in'),
                'weight_lbs': values.get('weight_lbs'),
                'ordered_grade': values.get('ordered_grade'),
                'comment': values.get('comment'),
                'notes': values.get('notes'),
                'length_ft': values.get('length_ft'),
                'inner_dia': values.get('inner_dia'),
                'outer_dia': values.get('outer_dia'),
                'heat_number': values.get('heat_number'),

                'comp_c': values.get('comp_c'),
                'comp_mn': values.get('comp_mn'),
                'comp_p': values.get('comp_p'),
                'comp_s': values.get('comp_s'),
                'comp_si': values.get('comp_si'),
                'comp_al': values.get('comp_al'),
                'comp_al_total': values.get('comp_al_total'),
                'comp_ti': values.get('comp_ti'),
                'comp_nb': values.get('comp_nb'),
                'comp_b': values.get('comp_b'),
                'comp_cu': values.get('comp_cu'),
                'comp_as': values.get('comp_as'),
                'comp_co': values.get('comp_co'),
                'comp_cr': values.get('comp_cr'),
                'comp_mo': values.get('comp_mo'),
                'comp_n': values.get('comp_n'),
                'comp_ni': values.get('comp_ni'),
                'comp_pb': values.get('comp_pb'),
                'comp_v': values.get('comp_v'),

            })]
        })

        if line:
            return line

    def import_offer_recieved(self):
        if self.import_option == 'csv':

            keys = ['name','bids', 'product_group', 'material',
                    'batch', 'gauge', 'width_in','length_ft', 'weight_lbs', 'ordered_grade', 'comment', 'notes',
                    'inner_dia', 'outer_dia', 'heat_number', 'c', 'comp_mn', 'comp_p', 'comp_s', 'comp_si',
                    'comp_al',
                    'comp_al_total', 'comp_ti', 'comp_nb', 'comp_b', 'comp_cu', 'comp_as', 'comp_co', 'comp_cr',
                    'comp_mo',
                    'comp_n', 'comp_ni', 'comp_pb', 'comp_v']
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
                        res = self.make_purchase_offer(values)
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
                    if len(line) < 34:
                        raise UserError(
                            _("Please Check the import template.Some of the required columns are not present "))
                    values = {
                        'name': line[0],
                        'bids': line[1],
                        'product_group': line[2],
                        'material': line[3],
                        'batch': line[4],
                        'gauge': line[5],
                        'width_in': line[6],
                        'length_ft': line[7],
                        'weight_lbs': line[8],
                        'ordered_grade': line[9],
                        'comment': line[10],
                        'notes': line[11],
                        'inner_dia': line[12],
                        'outer_dia': line[13],
                        'heat_number': line[14],

                        'comp_c': line[15],
                        'comp_mn': line[16],
                        'comp_p': line[17],
                        'comp_s': line[18],
                        'comp_si': line[19],
                        'comp_al': line[20],
                        'comp_al_total': line[21],
                        'comp_ti': line[22],
                        'comp_nb': line[23],
                        'comp_b': line[24],
                        'comp_cu': line[25],
                        'comp_as': line[26],
                        'comp_co': line[27],
                        'comp_cr': line[28],
                        'comp_mo': line[29],
                        'comp_n': line[30],
                        'comp_ni': line[31],
                        'comp_pb': line[32],
                        'comp_v': line[33],

                    }

                    res = self.make_purchase_offer(values)
