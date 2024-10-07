# -*- coding: utf-8 -*-
# File:           res_partner.py
# Author:         Israel Calderón
# Copyright:      (C) 2019 All rights reserved by Madkting
# Created:        2019-08-01
import json 

from datetime import datetime

from odoo import models, api, fields
from urllib import parse
from ..responses import results
from ..log.logger import logger


class MadktingConfig(models.Model):
    _name = 'madkting.config'
    _description = 'Config'

    company_id = fields.Many2one('res.company', string='Company', required=1)
    dbname = fields.Char(string='Dbname', required=1, default="NA")
    stock_quant_available_quantity_enabled = fields.Boolean('Mostrar cantidad disponible', default=True)
    # stock_source = fields.Many2one('stock.location', string="Ubicacion de Stock", domain=[('usage', '=', 'internal')])
    stock_source_multi = fields.Char('Multi Stock Src')
    stock_source_channels = fields.Char('Channels Stock Src')
    webhook_stock_enabled = fields.Boolean('Stock webhooks enabled', default=False)
    webhook_product_mapped = fields.Boolean('Solo envia webhook de productos mapeados', default=True)
    webhook_price_enabled = fields.Boolean('Price webhooks enabled', default=False)
    default_pricelist = fields.Char('Lista de precio para actualizar webhook')
    simple_description_enabled = fields.Boolean('Simple Description product enabled', default=False)
    validate_barcode_exists = fields.Boolean('Validar si el codigo de barras existe', default=True)
    update_order_name = fields.Boolean("Update Order Name with Channel Ref")
    update_order_name_pack = fields.Boolean("Update Order Name with Pack")
    orders_unconfirmed = fields.Boolean('Ordenes sin confirmar', help='Deja las ordenes sin confirmar')
    orders_unconfirmed_by_stock = fields.Boolean('Validar stock para confirmar orden', help='Valida el stock de las ordenes antes de confirmar')
    orders_unconfirmed_by_ff_type = fields.Boolean('Validar fulfillment para confirmar orden', help='Valida el tipo de fulfillment ordenes antes de confirmar')
    orders_unconfirmed_stock_src = fields.Char(string="Ubicaciones para validar stock", help='Ubicaciones de stock para validar stock en ventas')
    orders_unconfirmed_ff_types = fields.Char(string="Tipos de Fulfillment para no confirmar ventas", help='Tipos de Fulfillment para validar ventas')
    # update_parent_list_price = fields.Boolean('Update Parent Price', help='Actualiza el precio del producto padre en caso de tener variantes')
    orders_force_cancel = fields.Boolean('Cancela ordenes con movimientos', help='Si esta habilitada las ordenes se cancelan incluso si tienen movimientos de almacen realizados.', default=True)
    orders_cancel_related_documents = fields.Boolean('Cancela Factura y Pago relacionados', help='Si esta habilitada tambien se cancela la factura y el pago asociado a la orden', default=True)
    orders_line_warehouse_enabled = fields.Boolean('Asigna almacen a las lineas de venta', help='Si esta habilitada se asigna el mismo almacen de la orden a las lineas de venta.', default=False)
    # order_disable_update_empty_fields = fields.Char('Campos que no se actualizan si estan vacios')
    order_remove_tax_default = fields.Boolean('Quitar impuestos default', help='Quita los impuestos default de las lineas de la venta')
    shipping_webhook_enabled = fields.Boolean(string="Enviar webhook de guia envio")
    validate_address_invoice = fields.Boolean(string="Validar direccion de envio para generar factura")
    required_invoice_address_fields = fields.Text('Campos requeridos factura')

    invoice_webhook_enabled = fields.Boolean(string="Enviar webhook de facturas")
    auto_webhook_after_invoice_enabled = fields.Boolean(string="Enviar webhook automaticamente despues de facturar")
    invoice_prefix_id_folio = fields.Boolean(string="Agrega prefijo Id de factura en folio", default=True)
    invoice_separator = fields.Char(string="Separador Serie y Folio", help='Indica el separador para acotar la serie y el folio de la factura')
    invoice_serie = fields.Char(string="Serie de la factura", help='Si esta definida, se utiliza como serie por default para la factura')
    invoice_serie_ticket = fields.Char(string="Serie de la boleta", help='Si esta definida, se utiliza como serie por default para la factura')
    invoice_doc_type = fields.Selection([('ticket', "Nota/Boleta"), ("invoice", "Factura")], default="ticket", string="Tipo de documento facturacion")
    
    
    invoice_partner_vat = fields.Char(string="RFC Cliente de las facturas", help='Si esta definido, se utiliza como VAT/RFC/TAXID por default para la factura')
    invoice_prefix_file = fields.Char(string="Prefijo del archivo", help='Se utiliza para identificar el archivo que va a procesarse por el modulo')
    invoice_prefix_pdf_file = fields.Char(string="Prefijo del archivo PDF", help='Se utiliza para identificar el archivo que va a procesarse por el modulo')
    
    invoice_add_pdf_file = fields.Boolean(string="Adjuntar archivo PDF", help='Se utiliza para adjuntar archivo PDF si existe.')
    invoice_save_pdf_attachment = fields.Boolean(string="Guardar Adjunto PDF", help='Se utiliza para guardar el archivo PDF Generado.')
    invoice_country = fields.Char(string="Codigo de Pais", help='Pais donde se esta emitiendo la factura (ISO 3166-1 alpha-3)')
    invoice_currency = fields.Char(string="Codigo de Moneda", help='Moneda utilizada para facturar (ISO 4227)')

    log_enabled = fields.Boolean('Habilitar log')
    order_detail_enabled = fields.Boolean('Habilitar Detalle de Venta')
    webhook_detail_enabled = fields.Boolean('Habilitar Detalle de Webhooks')

    dropship_enabled = fields.Boolean('Dropshiping Enabled')
    dropship_webhook_enabled = fields.Boolean('Dropshiping Webhook Enabled')
    dropship_stock_enabled = fields.Boolean('Stock Dropshiping Enabled')
    dropship_default_route_id = fields.Many2one('stock.route', string='Ruta Default para Dropshiping')
    dropship_route_id = fields.Many2one('stock.route', string='Ruta para Dropshiping')
    dropship_mto_route_id = fields.Many2one('stock.route', string='Ruta para MTO')
    dropship_picking_type = fields.Many2one('stock.picking.type', string='Dropship Picking Type')

    validate_partner_exists = fields.Boolean('Buscar Partner', help="Valida si existe el partner en odoo antes de crearlo")
    product_shared_catalog_enabled = fields.Boolean("Catalogo de productos compartido", default=False)
    service_url = fields.Char(string="Url servicio", required=1)
    search_state_by_mapping = fields.Boolean(string="Buscar state_name por mapeo")
    search_city_by_mapping = fields.Boolean(string="Buscar city_name por mapeo")
    invoice_unconfirmed = fields.Boolean('Facturas sin confirmar', help='Deja las facturas sin confirmar')
    validate_pack_id_enabled = fields.Boolean('Validar folio carrito', help='Si se habilita se validara el folio carrito al crear las ventas')
    validate_order_duplicated_confirm = fields.Boolean('Validar order duplicada para confirmar', help='Si se habilita se validara que la orden no este duplicada al momento de confirmar')    
    
    @api.model
    def create_config(self, configs):
        """
        The config table is limited to only one record
        :param configs:
        :type configs: dict
        :return:
        """
        current_configs = self.get_config()

        if current_configs:
            return results.error_result('configurations_already_set')

        try:
            config = self.create(configs)
        except Exception as ex:
            logger.exception(ex)
            return results.error_result(ex)
        else:
            return results.success_result(config.copy_data()[0])

    @api.model
    def update_config(self, configs):
        """
        :param configs:
        :type configs: dict
        :return:
        """
        config = self.get_config()

        if not config:
            return results.error_result('configurations_not_set')
        try:
            config.write(configs)
        except Exception as ex:
            logger.exception(ex)
            return results.error_result(ex)
        else:
            return results.success_result(config.copy_data()[0])

    @api.model
    def get(self):
        """
        :return:
        :rtype: dict
        """
        config = self.get_config()

        if not config:
            return results.success_result()

        return results.success_result(config.copy_data()[0])

    def get_config(self, company_id=None):
        """
        Actualiza metodo para obtener configuracion de acuerdo al company del usuario
        :return:
        """
        logger.debug("## GET CONFIG BY COMPANY ##")
        if not company_id:
            company_id = self.env.user.company_id.id
        # logger.debug(company_id)
        config_id = self.search([("company_id", "=", company_id)], limit=1)
        if not config_id:
            logger.debug("No se encontro config por company")
            return
        # logger.debug(config_id)
        return config_id
    