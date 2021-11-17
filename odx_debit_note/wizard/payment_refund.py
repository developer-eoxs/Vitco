# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _


class OdxPaymentReturn(models.TransientModel):
	"""
	Account move reversal wizard, it cancel an account move by reversing it.
	"""
	_name = 'odx.payment.return'
	_description = 'Payment Return'

	date = fields.Date(string='Reversal date', default=fields.Date.context_today, required=True)
	reason = fields.Char(string='Reason')
	amount = fields.Float(string="Return Amount")
	payment_id = fields.Many2one('account.payment', string="Payment")
	reconcile = fields.Boolean(string="Reconcile")
	
	@api.model
	def default_get(self, fields):
		res = super(OdxPaymentReturn, self).default_get(fields)
		active_id = self.env.context.get('active_id')
		record = self.env['account.payment'].search([('id','=',active_id)])
		res.update({
			'payment_id': record.id,
		})
		return res

	# def post(self):
	# 	print ("pppppppppppppppppppppp")
	# 	print ("pppppppppppppppppppppp")
	# 	print ("pppppppppppppppppppppp")
	# 	print ("pppppppppppppppppppppp")
	# 	ref = str(self.reason)+"-"+str(self.payment_id.name)
	# 	if self.payment_id.partner_type == 'customer':
	# 		in_type = 'out_bund'
	# 	else :
	# 		in_type = 'in_bund'

	# 	invoice_vals = {
	# 		'payment_type': in_type,
	# 		'partner_id': self.payment_id.partner_id.id,
	# 		'invoice_origin': self.payment_id.name,
	# 		'invoice_line_ids': [(0, 0, {
	# 			'account_id': self.payment_id.journal_id.default_debit_account_id.id,
	# 			'quantity': 1,
	# 			'price_unit': self.amount,
	# 		})],
	# 	}
	# 	invoice_id = self.env['account.payment'].create(invoice_vals)
	# 	invoice_id.post()
	# 	move_ids = self.payment_id.mapped('move_line_ids.move_id')
	# 	print ("mmmmmmmmmmmmmmmmmmmmmm",move_ids)
	# 	move_list = []
	# 	for move in move_ids:
	# 		print ("moveeeeeeeeeeeeeeeeeeee")
	# 		print ("moveeeeeeeeeeeeeeeeeeee")
	# 		print ("moveeeeeeeeeeeeeeeeeeee")
	# 		move_list.append(move.id)
	# 	move_list.append(invoice_id.id)
	# 	lines = self.env['account.move.line'].search([('move_id','in',move_list),('account_id.internal_type','=','receivable')])
	# 	print ("linesssssssssssss",lines)
	# 	# print (c)
	# 	lines.reconcile()
	# 	print ("innnnnnnnnnnnnn",invoice_id)

	def post(self):
		print ("pppppppppppppppppppppp")
		print ("pppppppppppppppppppppp")
		print ("pppppppppppppppppppppp")
		print ("pppppppppppppppppppppp")
		if self.payment_id.partner_type == 'customer':
			in_type = 'outbound'
		else :
			in_type = 'inbound'
		ref = str(self.reason)+"-"+str(self.payment_id.name)
		new_payment = self.payment_id.copy()
		new_payment.write({'payment_type':in_type,'amount':self.amount,'communication':ref, 'payment_date':self.date, 'payment_return':True})
		new_payment.post()
		if self.reconcile:
			move_ids = self.payment_id.mapped('move_line_ids.move_id')
			new_move_ids = new_payment.mapped('move_line_ids.move_id')
			move_ls = []
			for move in move_ids:
				move_ls.append(move.id)
			for move in new_move_ids:
				move_ls.append(move.id)
			lines = self.env['account.move.line'].search([('move_id','in',move_ls),('account_id.internal_type','=','receivable')])
			print ("linesssssssssssss",lines)
			# print (c)
			lines.reconcile()



