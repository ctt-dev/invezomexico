# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError, Warning

class res_partner(models.Model):
    _inherit = 'res.partner'
    _description = 'Herencia a contactos'
    
    efos_ids = fields.One2many(
        'l10n_mx.efos',
        'partner_id',
        string="EFOS"
    )
    
    @api.depends('efos_ids','efos_ids.partner_id','efos_ids.status')
    def compute_efos_status(self):
        for rec in self:
            efos_status = False
            for efos in rec.efos_ids:
                efos_status = efos.status
            rec.efos_status = efos_status
    efos_status = fields.Char(
        string="Situación del contribuyente",
        compute=compute_efos_status,
        store=True
    )
    
    @api.model
    def create(self, values):
        record = super(res_partner, self).create(values)
        if 'vat' in values:
            efos_ids = self.env['l10n_mx.efos'].search([('rfc','=',values['vat'])])
            for efos in efos_ids:
                efos.partner_id = record.id
        return record
    
    def write(self, values):
        for rec in self:
            record = super(res_partner, rec).write(values)
            if 'vat' in values:
                efos_ids = self.env['l10n_mx.efos'].search([('rfc','=',values['vat'])])
                for efos in efos_ids:
                    efos.partner_id = rec.id
            return record