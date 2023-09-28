# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError , UserError


class account_move(models.Model):
    _inherit = 'account.move'
    # _description = 'Herencia a Asientos Contables'
    _description = 'Journal entries'
    
    @api.onchange('partner_id')
    def onchange_partner_id_for_efos(self):
        for rec in self:
            if rec.partner_id.vat != False:
                efos_ids = rec.env['l10n_mx.efos'].search([('rfc','=',rec.partner_id.vat)])
                for efos in efos_ids:
                    efos.partner_id = rec.partner_id.id
            if rec.partner_id.efos_status != False:
                # return {
                #     'warning': {
                #         'title': 'Advertencia: Contacto marcado como EFOS',
                #         'message': 'El contacto seleccionado está registrado como Empresa que Factura Operaciones Simuladas (EFOS) ante el SAT, ingrese al contacto para ver más detalles. \nNo se recomienda continuar con la factura, continue bajo su propio riesgo.'
                #     }
                # }
                return {
                    'warning': {
                        'title': 'Warning: Partner marked as EFOS',
                        'message': 'The selected contact is registered as a Company that Invoices Simulated Operations (EFOS) before the SAT, enter the contact to see more details. \nIt is not recommended to continue with the invoice, continue at your own risk.'
                    }
                }