# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class L10nMxCFDIMetadata(models.Model):
    _name = 'l10n_mx.cfdi_metadata'
    _description = 'Modelo de metadatos'
    _order = 'id desc'
            
    name = fields.Char(
        string="UUID"
    )
    rfc_emisor = fields.Char(
        string="RFC Emisor"
    )
    nombre_emisor = fields.Char(
        string="Emisor"
    )
    rfc_receptor = fields.Char(
        string="RFC Receptor"
    )
    nombre_receptor = fields.Char(
        string="Receptor"
    )
    rfc_pac = fields.Char(
        string="RFC Pac"
    )
    date = fields.Datetime(
        string="Fecha de emisión"
    )
    cert_date = fields.Datetime(
        string="Fecha de certificación SAT"
    )
    total = fields.Float(
        string="Monto"
    )
    type_comprobante = fields.Selection(
        [
            ('I', 'Ingreso'),
            ('E', 'Egreso'),
            ('T', 'Traslado'),
            ('P', 'Pago'),
            ('N', 'Nomina')
        ],
        string="Tipo de documento"
    )
    state = fields.Selection(
        [
            ('1', 'Vigente'),
            ('0', 'Cancelado')
        ], 
        string="Estatus del SAT"
    )
    cancel_date = fields.Datetime(
        string="Fecha de cancelación"
    )
    request_id = fields.Many2one('l10n_mx.cfdi_request', string="Solicitud")

    # @api.model
    # def create(self,values):
    #     record = super(l10n_mx_cfdi_request, self).create(values)

    #     if record.state == '0':
    #         cfdi_document = self.env['l10n_mx.cfdi_document'].search([('name','=',record.name)],limit=1)

    #         if cfdi_document:
    #             cfdi_document.write({
    #                 'cfdi_state': 'Cancelado',
    #                 'cancel_date': record.cancel_date
    #             })
    #     return record
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)

        # Filtrar registros cancelados
        cancelados = [r for r in records if r.state == '0' and r.name]

        if cancelados:
            names = [r.name for r in cancelados]
            documentos = self.env['l10n_mx.cfdi_document'].search([('name', 'in', names)])
            documentos_map = {doc.name: doc for doc in documentos}

            for record in cancelados:
                cfdi_document = documentos_map.get(record.name)
                if cfdi_document:
                    cfdi_document.write({
                        'cfdi_state': 'Cancelado',
                        'cancel_date': record.cancel_date
                    })
                    _logger.info("Documento %s marcado como cancelado", cfdi_document.name)
                else:
                    _logger.warning("No se encontró l10n_mx.cfdi_document con name = %s", record.name)

        return records