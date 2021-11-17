# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HrContract(models.Model):
	_inherit = 'hr.contract'

	schedule_pay = fields.Selection([
			('monthly', 'Monthly'),
			('quarterly', 'Quarterly'),
			('semi-annually', 'Semi-annually'),
			('annually', 'Annually'),
			('weekly', 'Weekly'),
			('hourly', 'Hourly'),
			('bi-weekly', 'Bi-weekly'),
			('bi-monthly', 'Bi-monthly'),
		], string='Scheduled Pay', index=True, default='monthly',
		help="Defines the frequency of the wage payment.")

class HrPayslipWorkedDays(models.Model):
	_inherit = 'hr.payslip.worked_days'

	import_from_attendance = fields.Boolean(
		string='Imported From Timesheet',
		default=False,
	)
	
class HrPayslip(models.Model):
	_inherit = "hr.payslip"

	def button_import_attendance(self):
		for payslip in self:
			payslip._import_attendance()

	def _import_attendance(self):
		self.ensure_one()
		wd_obj = self.env["hr.payslip.worked_days"]
		day_obj = self.env["hr.attendance"]
		date_from = self.date_from
		date_to = self.date_to

		criteria1 = [
			("payslip_id", "=", self.id),
			("import_from_attendance", "=", True),
		]
		wd_obj.search(criteria1).unlink()

		res = {
			"name": _("Attendance"),
			"code": "ATTN",
			"number_of_days": 0.0,
			"number_of_hours": 0.0,
			"contract_id": self.contract_id.id,
			"import_from_attendance": True,
			"payslip_id": self.id,
		}

		criteria2 = [
			("check_in", ">=", date_from),
			("check_out", "<=", date_to),
			("employee_id", "=", self.employee_id.id),
		]

		for day in day_obj.search(criteria2):
			if day.worked_hours >= 0.0:
				res["number_of_days"] += 1
				res["number_of_hours"] += day.worked_hours
		wd_obj.create(res)

		for line in self.worked_days_line_ids:
			if line.code == 'WORK100':
				line.unlink()