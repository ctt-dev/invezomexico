# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError , UserError

class WizardMoveDocument(models.TransientModel):
    _name = 'l10n_mx.cfdi_document_wizard'
    _description = 'Wizard para vincular documento cfdi a moves'
    
    move_id = fields.Integer(
        string="Factura"
    )
    picking_id = fields.Integer(
        string="Traslado"
    )
    payment_id = fields.Integer(
        string="Pago"
    )
    move_id_type = fields.Char(
        string="Tipo de factura"
    )
    @api.depends('move_id_type')
    def compute_tipo_comprobante(self):
        for rec in self:
            tipo_comprobante = False
            if rec.move_id_type == "in_invoice":
                tipo_comprobante = "I"
            elif rec.move_id_type == "in_refund":
                tipo_comprobante = "E"
            elif rec.move_id_type == 'picking':
                tipo_comprobante = "T"
            elif rec.move_id_type == 'payment':
                tipo_comprobante = "P"
            rec.tipo_comprobante = tipo_comprobante    
    
    tipo_comprobante = fields.Char(
        string="Tipo de comprobante",
        compute=compute_tipo_comprobante,
        store=True
    )
    date = fields.Date(
        string="Fecha"
    )
    cfdi_document=fields.Many2one(
        'l10n_mx.cfdi_document',
        string="Documento cfdi"
    )
    total=fields.Float(
        string="Total",
        related='cfdi_document.total'
    )
    cfdi_state=fields.Char(
        string="Estado CFDI",
        related='cfdi_document.cfdi_state'
    )
    emisor=fields.Char(
        string="Emisor",
        related='cfdi_document.emisor'
    )
    folio = fields.Char(
        string="Folio",
        related='cfdi_document.folio'
    )
    metadata=fields.Text(
        string="Metadata",
        related='cfdi_document.metadata_pretty'
    )
    
    partner_id_vat = fields.Char(
        string="RFC"
    )
    
    def event_wizard(self):
        if self.cfdi_document:

            if self.move_id:
                model = 'account.move'
                search_id = self.move_id
            elif self.picking_id:
                model = 'stock.picking'
                search_id = self.picking_id
            else:
                model = 'account.payment'
                search_id = self.payment_id
            
            partner_bills = self.env[model].search([('cfdi_document.uuid','=',self.cfdi_document.uuid)])
            if len(partner_bills) > 0:
                raise ValidationError("El UUID del documento que seleccionó ya se encuentra relacionado. Se recomienda revisar el listado de los documentos vinculados relacionados a el RFC ''" + str(self.cfdi_document.rfc_emisor) + "'' para continuar...")
                
            move = self.env[model].search([('id','=',search_id)])
            if self.cfdi_document.rfc_emisor != move.partner_id.vat:
                raise UserError("RFC de documento CFDI no corresponde al del proveedor")

            if model == 'account.move':
                if self.cfdi_document.total != move.amount_total:
                    if round(abs(self.cfdi_document.total - move.amount_total),2) > self.env.company.dif_allowed:
                        raise UserError("La diferencia entre el total del asiento contable y el CFDI relacionado es mayor a $" + "{:.2f}".format(self.env.company.dif_allowed) + " pesos.")
            
            move.write({
                'cfdi_document':self.cfdi_document.id
            })
            
            self.cfdi_document.write({
                'link_state':'link'
            })
        else:
            raise UserError("Seleccione un documento")

    def event_picking_wizard(self):
        pass
            
    @api.onchange('date')
    def onchange_date(self):
        self.cfdi_document = False