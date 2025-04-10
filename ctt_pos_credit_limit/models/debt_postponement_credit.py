from odoo import models, fields, api, _
import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
_logger = logging.getLogger(__name__)
import datetime


# class ctt_pos__credit_limit(models.Model):
#     _name = 'ctt_pos__credit_limit.ctt_pos__credit_limit'
#     _description = 'ctt_pos__credit_limit.ctt_pos__credit_limit'

class DebtPostponement(models.Model): 
    _name = 'ctt_pos_credit_limit.debt_postponement'
    _description = 'ctt_pos_credit_limit.debt_postponement'
    
    partner = fields.Many2one(
        "res.partner",
        string="Cliente", required=True
    )

    limit_date = fields.Datetime(string = "Fecha Limite", required=True)

    authorized = fields.Many2one("hr.employee", string="Autorizó", required=True)
    request = fields.Many2one("hr.employee", string="Solicitó", required=True)
    motive = fields.Text(string="Motivo")

    # @api.model
    def create(self, vals_list):
        res = super(DebtPostponement, self).create(vals_list)
        if 'partner' in vals_list:
            partner = self.env['res.partner'].browse(vals_list['partner'])
            partner.message_post(body="Se creó convenio de deuda con fecha a "+str(self.limit_date),
                      type="comment")
        return res
    # @api.model
    def write(self, vals_list):
        res = super(DebtPostponement, self).write(vals_list)
        for rec in self:
            rec.partner.message_post(body="Se modificó convenio de deuda con fecha a "+str(rec.limit_date),
                  type="comment")
        return res

    