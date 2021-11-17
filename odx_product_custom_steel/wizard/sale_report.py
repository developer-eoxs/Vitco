from odoo import models, fields, api, _
from datetime import datetime, date, timedelta

from odoo.exceptions import UserError, ValidationError
import io as io
from io import BytesIO
import base64
import pandas as pd
import xlsxwriter


class OdxSaleReport(models.TransientModel):
    _name = 'odx.sale.report'
    _description = 'Sale Report'

    date_from = fields.Date(string='From Date', required=True,
                            default=lambda self: self._context.get('date_from', datetime.today().replace(day=1)))
    date_to = fields.Date(string='To Date', required=True)
    excel_file = fields.Binary(string='Report', readonly="1")
    file_name = fields.Char(string='Excel File', readonly="1")

    @api.onchange('date_from')
    def last_day_of_month(self):
        if self.date_from:
            any_day = datetime.strptime(str(self.date_from), '%Y-%m-%d')
            next_month = any_day.replace(day=28) + timedelta(days=4)  # this will never fail
            to_date = next_month - timedelta(days=next_month.day)
            to_date = to_date.strftime('%Y-%m-%d')
            self.date_to = to_date

    def generate(self):
        data = self.generate_data(self.date_from, self.date_to)
        data_cols = ['sales_order', 'plant', 'plant_name', 'so_date', 'material_description', 'customer',
                     'ship_to_party', 'thickness', 'width', 'cut_length', 'so_qty', 'inv_qty', 'balance_dispatch']
        dataframe_summary = pd.DataFrame(data, columns=data_cols)
        dataframe_summary.columns = dataframe_summary.columns.str.title().str.replace(r"[\"_',]", ' ')

        date_from = str(self.date_from)
        date_to = str(self.date_to)
        title = 'Sales Report ' + str(datetime.strptime(date_from, '%Y-%m-%d').strftime('%d-%m-%Y'))
        if date_to:
            title = title + " To " + str(datetime.strptime(date_to, '%Y-%m-%d').strftime('%d-%m-%Y'))

        filename = 'SalesReport.xlsx'
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        fp = BytesIO()
        writer.book.filename = fp
        dataframe_summary.to_excel(writer, sheet_name='Sheet1', startrow=2, index=False, header=True)
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        title_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'fg_color': '#356DB2',
            'border': 1})
        title_format.set_align('vcenter')
        title_format.set_font_size(16)
        title_format.set_font_color('#FFFFFF')
        header_style = workbook.add_format({
            'bold': True,
            'align': 'center',
            'fg_color': '#D2d6d6',
            'text_wrap': True,
            'border': 0})
        header_style_left = workbook.add_format({
            'bold': True,
            'align': 'left',
            'fg_color': '#D2d6d6',
            'text_wrap': True,
            'border': 0})
        tot_format = workbook.add_format({
            'bold': True,
            'align': 'left',
            'fg_color': '#D2d6d6',
            'text_wrap': True,
            'border': 1})

        tot_format1 = workbook.add_format({
            'bold': True,
            'align': 'right',
            'num_format': '#,##0.00',
            'fg_color': '#D2d6d6',
            'text_wrap': True,
            'border': 1})
        tot_format1.set_align('vcenter')
        tot_format1_text = workbook.add_format({
            'bold': True,
            'align': 'left',
            'num_format': '#,##0.00',
            'fg_color': '#87CEFF',
            'border': 1})
        no_color_tot_format1 = workbook.add_format({
            'bold': True,
            'align': 'right',
            'num_format': '#,##0.00',
            'border': 0})
        no_color_tot_format1_text = workbook.add_format({
            'bold': True,
            'align': 'left',
            'border': 0})
        filter_format = workbook.add_format({
            'bold': True,
            'align': 'left',
            'num_format': '#,##0.00',
            'border': 0})
        address_format1 = workbook.add_format({
            'align': 'left',
            'bold': True,
            'text_wrap': True,
            'font_size': 9,
            'border': 0})

        row_num_style = workbook.add_format({'num_format': '#,##0.000'})
        worksheet.merge_range('A1:M2', title, title_format)
        dataframe_summary = dataframe_summary.rename(columns={'Inv Qty': 'Dispatch(Inv.Qty.)'})
        dataframe_summary = dataframe_summary.rename(columns={'Width': 'Width (in)'})
        dataframe_summary = dataframe_summary.rename(columns={'Thickness': 'Thickness (in)'})
        dataframe_summary = dataframe_summary.rename(columns={'Cut Length': 'Cut Length (in)'})
        dataframe_summary = dataframe_summary.rename(columns={'So Qty': 'So Qty (lbs)'})
        dataframe_summary = dataframe_summary.rename(columns={'Inv Qty': 'Inv Qty (lbs)'})
        dataframe_summary = dataframe_summary.rename(columns={'Balance Dispatch': 'Balance Dispatch (lbs)'})
        for col_num, value in enumerate(dataframe_summary.columns.values):
            size = len(value) + 6
            if value == 'Customer':
                size += 7
            worksheet.set_column(col_num, col_num, size)
            worksheet.write(2, col_num, value, header_style)
        row_num_style = workbook.add_format({'num_format': '#,##0.000'})
        worksheet.set_column('H:H', 20, row_num_style)
        worksheet.set_column('I:I', 20, row_num_style)
        worksheet.set_column('J:J', 20, row_num_style)
        writer.save()
        excel_file = base64.encodestring(fp.getvalue())
        self.write({'excel_file': excel_file, 'file_name': filename})
        fp.close()

        return {
            'name': 'Sales Report',
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': 'odx.sale.report',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    def generate_data(self, date_from, date_to):
        where_qry = " WHERE so.date_order >='" + str(date_from) + "'"
        if date_to:
            where_qry = where_qry + " and so.date_order <='" + str(date_to) + "'"
        data_qry = ('''SELECT  so.name as sales_order,
					sl.complete_name as plant,
					sw.name as plant_name,
					to_char(so.date_order,'DD-MM-YYYY') as so_date,
					--so.date_order as so_date, 
					sol.name as material_description,
					rp.id as partner_id,
					rp.name as customer,
					ship_rp.name as ship_to_party,
					-- sol.thickness_in as thickness,
					COALESCE(sol.thickness_in, 0) as thickness,
					-- sol.width_in as width,
					COALESCE(sol.width_in, 0) as width,
					-- sol.length_in as cut_length,
					COALESCE(sol.length_in, 0) as cut_length,
					sol.product_uom_qty as so_qty,
					sol.qty_invoiced as inv_qty,
					sol.product_uom_qty-sol.qty_delivered as balance_dispatch
					from sale_order_line sol
					left join sale_order so on so.id=sol.order_id
					left join stock_warehouse sw on sw.id=so.warehouse_id
					left join res_partner rp on rp.id=so.partner_id
					left join res_partner ship_rp on ship_rp.id=so.partner_shipping_id
					left join stock_location sl on sl.id =sw.lot_stock_id
				%s 
				
				order by so.name
				''') % (where_qry)
        self.env.cr.execute(data_qry)
        data = self.env.cr.dictfetchall()
        return data
