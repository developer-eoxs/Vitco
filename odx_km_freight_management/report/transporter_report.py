# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime
from odoo.tools.profiler import profile
from odoo.exceptions import ValidationError
from datetime import date

class ReportTransport(models.AbstractModel):

	_name = 'report.odx_km_freight_management.transporter_report'

	
	def transporting_details(self,data):
		details_qry = ('''SELECT fl.name,sl.name as source_location ,dl.name as dest_location,fl.total_weight from freight_line fl

							left join frm_location sl on sl.id=fl.source_location
							left join frm_location dl on dl.id=fl.dest_location
							where fl.transporter_id = %s and fl.expected_date = '%s'
							''')%(data,date.today())
		self.env.cr.execute(details_qry)
		result = self.env.cr.dictfetchall()
		return result

		
	@api.model
	def _get_report_values(self, docids=None, data=None):
		model = self.env.context.get('active_model')
		docs = self.env['res.partner'].browse(docids)
		return{
			'doc_ids': self.ids,
			'doc_model': 'res.partner',
			'docs': docs,
			'data':data,
			'transporting_details':self.transporting_details
		}

