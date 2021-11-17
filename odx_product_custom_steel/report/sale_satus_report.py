from dateutil.relativedelta import relativedelta

from odoo import models, fields
from datetime import datetime, timedelta
import xlsxwriter
from odoo.fields import datetime
import io


class SaleStatusReport(models.AbstractModel):
    _name = 'report.sale_status_mt_report_xlsx.report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wiz):
        # date_to = fields.Date.today()
        # date_from = fields.Date.today()
        date_to = wiz.date_to
        date_from = wiz.date_from

        top_heading_format = workbook.add_format({'align': 'center',
                                                  'valign': 'vcenter',
                                                  'bold': True, 'size': 16,
                                                  'fg_color': '#356DB2',
                                                  'border': 1,
                                                  'font_color': '#FFFFFF'

                                                  })
        heading_format = workbook.add_format({'align': 'center',
                                              'valign': 'vcenter',
                                              'bold': True, 'size': 12,
                                              'fg_color': '#D2d6d6',
                                              'border': 1

                                              })
        sub_heading_format = workbook.add_format({'align': 'left',
                                                  'valign': 'vcenter',
                                                  'bold': False, 'size': 12,
                                                  'font_color': '#000000',
                                                  'border': 1
                                                  })
        value_format = workbook.add_format({'align': 'left',
                                            'valign': 'vcenter',
                                            'bold': False, 'size': 11,
                                            'font_color': '#000000'
                                            })

        col_format = workbook.add_format({'valign': 'left',
                                          'align': 'left',
                                          'bold': True,
                                          'size': 10,
                                          'font_color': '#000000'
                                          })

        col_format.set_text_wrap()
        worksheet = workbook.add_worksheet('Sales Order Status and Material Tracking')
        row = 1

        title = 'Sales Order Status and Material Tracking ' + datetime.strptime(str(date_from), '%Y-%m-%d').strftime(
            '%d-%m-%Y')
        if date_to:
            title = title + " To " + datetime.strptime(str(date_to), '%Y-%m-%d').strftime('%d-%m-%Y')

        worksheet.merge_range('A1:AD2', title, top_heading_format)
        row += 2
        worksheet.write(row, 0, "Sl.No", heading_format)
        worksheet.write(row, 1, "Sales Order", heading_format)
        worksheet.write(row, 2, "Customer", heading_format)
        worksheet.write(row, 3, "Sub Category", heading_format)
        worksheet.write(row, 4, "Thk(in)", heading_format)
        worksheet.write(row, 5, "Width(in)", heading_format)
        worksheet.write(row, 6, "Cut length(in)", heading_format)
        worksheet.write(row, 7, "Quantity", heading_format)
        worksheet.write(row, 8, "Dispatched", heading_format)
        worksheet.write(row, 9, "Bal. Dispatch", heading_format)
        worksheet.write(row, 10, "WH", heading_format)
        worksheet.merge_range('L4:N4', "Pickling", heading_format)
        worksheet.merge_range('O4:Q4', "Cold Rolling", heading_format)
        worksheet.merge_range('R4:T4', "Degreasing", heading_format)
        worksheet.merge_range('U4:W4', "Annealing", heading_format)
        worksheet.merge_range('X4:Z4', "Temper Rolling", heading_format)
        worksheet.merge_range('AA4:AC4', "CPL", heading_format)

        row += 1
        worksheet.write(row, 11, "Coil No", sub_heading_format)
        worksheet.write(row, 12, "Qnty", sub_heading_format)
        worksheet.write(row, 13, "W/H", sub_heading_format)

        worksheet.write(row, 14, "Coil No", sub_heading_format)
        worksheet.write(row, 15, "Qnty", sub_heading_format)
        worksheet.write(row, 16, "W/H", sub_heading_format)

        worksheet.write(row, 17, "Coil No", sub_heading_format)
        worksheet.write(row, 18, "Qnty", sub_heading_format)
        worksheet.write(row, 19, "W/H", sub_heading_format)

        worksheet.write(row, 20, "Coil No", sub_heading_format)
        worksheet.write(row, 21, "Qnty", sub_heading_format)
        worksheet.write(row, 22, "W/H", sub_heading_format)

        worksheet.write(row, 23, "Coil No", sub_heading_format)
        worksheet.write(row, 24, "Qnty", sub_heading_format)
        worksheet.write(row, 25, "W/H", sub_heading_format)

        worksheet.write(row, 26, "Coil No", sub_heading_format)
        worksheet.write(row, 27, "Qnty", sub_heading_format)
        worksheet.write(row, 28, "W/H", sub_heading_format)

        row += 2

        order_line_list = self.env['sale.order'].search(
            [('date_order', '>=', date_from), ('date_order', '<', date_to)])
        print(len(order_line_list))

        sl_no = 1

        if order_line_list:
            for order in order_line_list:
                if len(order.mapped('order_line').mapped('job_lot_ids')) > 0:
                    print(order)
                    for ol in order.order_line:
                        balance_qty = 0
                        balance_qty = ol.product_uom_qty - ol.qty_delivered
                        worksheet.write(row, 0, sl_no)
                        worksheet.write(row, 1, order.name)
                        worksheet.write(row, 2, order.partner_id.name)
                        worksheet.write(row, 3, ol.sub_category_id.name)
                        worksheet.write(row, 4, ol.thickness_in)
                        worksheet.write(row, 5, ol.width_in)
                        worksheet.write(row, 6, ol.length_in)
                        worksheet.write(row, 7, ol.product_uom_qty)
                        worksheet.write(row, 8, ol.qty_delivered)
                        worksheet.write(row, 9, balance_qty)
                        worksheet.write(row, 10, order.warehouse_id.name)
                        #
                        for job in ol.job_lot_ids.mapped('multi_lot_line_ids'):

                            if job.job_order_ref_id.operation == "pickling":
                                worksheet.write(row, 11, job.lot_id.name)
                                worksheet.write(row, 12, job.product_qty)
                                worksheet.write(row, 13, order.warehouse_id.name)
                                row += 1

                            elif job.job_order_ref_id.operation == "cr":
                                worksheet.write(row, 14, job.lot_id.name)
                                worksheet.write(row, 15, job.product_qty)
                                worksheet.write(row, 16, order.warehouse_id.name)
                                row += 1

                            elif job.job_order_ref_id.operation == "degreasing":
                                worksheet.write(row, 17, job.lot_id.name)
                                worksheet.write(row, 18, job.product_qty)
                                worksheet.write(row, 19, order.warehouse_id.name)
                                row += 1

                            elif job.job_order_ref_id.operation == "annealing":
                                worksheet.write(row, 20, job.lot_id.name)
                                worksheet.write(row, 21, job.product_qty)
                                worksheet.write(row, 22, order.warehouse_id.name)
                                row += 1

                            elif job.job_order_ref_id.operation == "tr":
                                worksheet.write(row, 23, job.lot_id.name)
                                worksheet.write(row, 24, job.product_qty)
                                worksheet.write(row, 25, order.warehouse_id.name)
                                row += 1

                            else:
                                worksheet.write(row, 26, job.lot_id.name)
                                worksheet.write(row, 27, job.product_qty)
                                worksheet.write(row, 28, order.warehouse_id.name)
                                row += 1

                        for jo in ol.job_lot_ids.mapped('job_line_ids'):
                            if jo.job_ref_id.operation == "pickling":
                                worksheet.write(row, 11, jo.finished_lot_id.name)
                                worksheet.write(row, 12, jo.product_qty)
                                worksheet.write(row, 13, order.warehouse_id.name)
                                row += 1

                            elif jo.job_ref_id.operation == "cr":
                                worksheet.write(row, 14, jo.finished_lot_id.name)
                                worksheet.write(row, 15, jo.product_qty)
                                worksheet.write(row, 16, order.warehouse_id.name)
                                row += 1

                            elif jo.job_ref_id.operation == "degreasing":
                                worksheet.write(row, 17, jo.finished_lot_id.name)
                                worksheet.write(row, 18, jo.product_qty)
                                worksheet.write(row, 19, order.warehouse_id.name)
                                row += 1

                            elif jo.job_ref_id.operation == "annealing":
                                worksheet.write(row, 20, jo.finished_lot_id.name)
                                worksheet.write(row, 21, jo.product_qty)
                                worksheet.write(row, 22, order.warehouse_id.name)
                                row += 1

                            elif jo.job_ref_id.operation == "tr":
                                worksheet.write(row, 23, jo.finished_lot_id.name)
                                worksheet.write(row, 24, jo.product_qty)
                                worksheet.write(row, 25, order.warehouse_id.name)
                                row += 1

                            else:
                                worksheet.write(row, 26, jo.finished_lot_id.name)
                                worksheet.write(row, 27, jo.product_qty)
                                worksheet.write(row, 28, order.warehouse_id.name)
                                row += 1

                        sl_no += 1
                        row+=1

        #             worksheet.write(row_no - 3, 6, total_vertical_one, sub_heading_format)
        #             worksheet.write(row_no - 3, 7, total_vertical_two, sub_heading_format)
        #             worksheet.write(row_no - 3, 8, total_vertical_three, sub_heading_format)
        #             worksheet.write(row_no - 3, 9, total_vertical_four, sub_heading_format)
        #             worksheet.write(row_no - 3, 10, total_vertical_five, sub_heading_format)
        #             # worksheet.write(row_no - 3, 11, total_vertical_one, sub_heading_format)
        #
        #             net_total = total_vertical_one + total_vertical_two + total_vertical_three + \
        #                         total_vertical_four + total_vertical_five
        #             worksheet.write(row_no - 3, 11, net_total, heading_format)
        #             row += 2

