from odoo import models, fields, api, _
import logging
import json
from odoo import exceptions
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__) 
from datetime import datetime, date
import unicodedata

class sale_order_inherit(models.Model):
    _inherit = 'sale.order'
    _description = 'Orden de venta'

    
    marketplace = fields.Many2one(
        "llantas_config.marketplaces",
        string="Marketplace",
        tracking=True,
        store=True,
        
    )
    
    @api.depends('marketplace','marketplace.name')
    def _compute_marketplace_name(self):
        for rec in self:
            marketplace_name = ""
            # raise UserError('.....' + str(rec.marketplace.name))
            if rec.marketplace.id:
                marketplace_name = rec.marketplace.name
            rec.marketplace_name = marketplace_name
    marketplace_name = fields.Char(
        string="Marketplace",
        compute=_compute_marketplace_name,
        store=True,
    )

    marketplace_name2 = fields.Char(
        string="Canal de venta",
        related="marketplace.name",
        store=True,
    )
    
    comision=fields.Float(
        string="Comisión",
        tracking=True,
    )
    envio=fields.Float(
        string="Envio",
        tracking=True,
    )

    comprador_id=fields.Many2one(
        "hr.employee",
        string="Comprador",
        tracking=True,
        store=True,
    )

    folio_venta=fields.Char(
        string="No. Venta",
        tracking=True,
        store=True,

    )


    json_data = fields.Text(string="JSON Data")

    @api.model
    def create(self, values):
        if 'channel_order_reference' in values:
            values['folio_venta'] = values['channel_order_reference']
        elif 'channel_order_id' in values and not values.get('folio_venta'):
            # Si el valor no viene en `values`, tomar el valor actual de `rec`
            values['folio_venta'] = values['channel_order_id']

        if 'yuju_seller_shipping_cost' in values:
            values['envio'] = values['yuju_seller_shipping_cost']
        if 'yuju_marketplace_fee' in values:
            values['comision'] = values['yuju_marketplace_fee']
                
        # Verificación de unicidad de 'folio_venta'
        if 'folio_venta' in values:
            venta_ids = self.search([
                ('folio_venta', '=', values['folio_venta']),
                ('folio_venta', '!=', False)
            ])
            if venta_ids:
                raise UserError('El número de venta debe ser único.')
    
        # Asignar 'guia' si se ha proporcionado 'yuju_carrier_tracking_ref'
        if 'yuju_carrier_tracking_ref' in values:
            values['guia'] = values['yuju_carrier_tracking_ref']
        
        # Verificación de unicidad de 'guia'
        guia = values.get('guia')
        if guia:
            ventas = self.search([
                ('guia', '=', guia),
                ('guia', '!=', False)
            ])
            if ventas:
                raise UserError('El número de guía debe ser único.')
    
        # Actualizar marketplace en create
        channel = values.get('channel')
        if channel:
            # Quitar espacios y acentos
            channel = self.remove_accents(channel.strip())
    
            # Buscar el marketplace usando solo el nombre
            marketplace_record = self.env['llantas_config.marketplaces'].search([
                ('company_id', '=', values.get('company_id')),
                ('name', '=', channel)
            ], limit=1)
    
            # Si no se encuentra, dejar el valor de 'marketplace' como False
            values['marketplace'] = marketplace_record.id if marketplace_record else False
    
        # Llamada al método create del super para crear el registro
        return super(sale_order_inherit, self).create(values)



    def remove_accents(self, input_str):
        # Normalizar la cadena eliminando los acentos
        nfkd_form = unicodedata.normalize('NFKD', input_str)
        return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
        
    def write(self, values):
        for rec in self:
            # Actualizar marketplace en write
            if rec.channel:
                # Quitar espacios y acentos
                channel = self.remove_accents(rec.channel.strip())

                # Obtener las claves de selección para 'yuju_tag'
                yuju_tag_selection = dict(self.env['llantas_config.marketplaces'].fields_get(allfields=['yuju_tag'])['yuju_tag']['selection'], limit=1)

                # Revisar si el canal proporcionado coincide con alguna clave en el campo 'yuju_tag'
                yuju_tag_key = None
                for key, label in yuju_tag_selection.items():
                    if self.remove_accents(label.lower()) == channel.lower():
                        yuju_tag_key = key
                        break

                # Si no se encontró una clave para el tag 'channel', buscar solo por name
                if not yuju_tag_key:
                    marketplace_record = self.env['llantas_config.marketplaces'].search([
                        ('name', '=', channel),
                        ('company_id', '=', rec.company_id.id)
                    ], limit=1)
                else:
                    # Buscar el marketplace usando coincidencia exacta de nombre o el tag 'yuju_tag'
                    marketplace_record = self.env['llantas_config.marketplaces'].search([
                        ('company_id', '=', rec.company_id.id),
                        '|',
                        ('yuju_tag', '=', yuju_tag_key),  # Priorizar coincidencia exacta en el tag
                        ('name', '=', channel)  # Luego, comparación exacta con el nombre
                    ], limit=1)

                if not marketplace_record:
                    raise UserError(f"No se encontró el marketplace con el nombre o tag '{channel}' para la empresa actual.")
                else:
                    values['marketplace'] = marketplace_record.id
                    values['fee_import'] = marketplace_record.fee_marketplace

            # Actualización del carrier
            if 'yuju_carrier' in values:
                yuju_carrier = values.get('yuju_carrier', '').strip()
                if yuju_carrier:
                    carrier_record = rec.env['llantas_config.carrier'].search([
                        ('name', 'ilike', yuju_carrier),
                    ], limit=1)

                    if carrier_record:
                        values['llantas_config_carrier_id'] = carrier_record.id
                    else:
                        raise UserError(f"No se encontró el carrier con el nombre '{yuju_carrier}' para la empresa actual.")
                else:
                    values['llantas_config_carrier_id'] = False

            # Verificación de unicidad de folio_venta
            if 'folio_venta' in values:
                venta_ids = rec.env['sale.order'].search([
                    ('folio_venta', '=', values['folio_venta']),
                    ('id', '!=', rec.id),
                    ('folio_venta', '!=', False)
                ])
                if venta_ids:
                    raise UserError('El número de venta debe ser único.')


            if 'yuju_carrier_tracking_ref' in values:
                values['guia'] = values['yuju_carrier_tracking_ref']
            elif rec.yuju_carrier_tracking_ref and not values.get('guia'):
                # Si el valor no viene en `values`, tomar el valor actual de `rec`
                values['guia'] = rec.yuju_carrier_tracking_ref

            if 'channel_order_reference' in values:
                values['folio_venta'] = values['channel_order_reference']
            elif rec.channel_order_reference and not values.get('folio_venta'):
                # Si el valor no viene en `values`, tomar el valor actual de `rec`
                values['folio_venta'] = rec.channel_order_id


            # Verificar unicidad de 'guia'
            guia = values.get('guia')
            if guia:
                ventas = self.env['sale.order'].search([
                    ('guia', '=', guia),
                    ('id', '!=', rec.id),  # Excluir el registro actual
                    ('guia', '!=', False)
                ])
                if ventas:
                    raise UserError('El número de guía debe ser único.')

        # Llamada al método write del super para guardar los cambios
        result = super(sale_order_inherit, self).write(values)

        return result


    
    
    purchase_order = fields.Char(string="Purchase Order")
    
    link_venta=fields.Char(
        string="Link de venta",
        tracking=True,
    )

    link_facturacion=fields.Char(
        string="Link de facturacion",
        tracking=True,
        compute="_compute_link"
    )

    @api.depends('folio_venta', 'company_id.url_autofacturacion')
    def _compute_link(self):
        for order in self:
            try:
                if order.folio_venta:
                    if order.company_id.url_autofacturacion:
                        order.link_facturacion = f"{order.company_id.url_autofacturacion}/autofacturador/{order.folio_venta}"
                    else:
                        order.link_facturacion = ""
                else:
                    order.link_facturacion = ""
            except Exception as e:
                order.link_facturacion = ""
                _logger.error(f"Error computing link_facturacion for sale.order({order.id}): {e}")
                raise UserError(f"An error occurred while computing the invoicing link: {e}")
            
    status_ventas=fields.Many2one(
        "llantas_config.status_ventas",
        string="Estatus",
        tracking=True,
    
    )

    status_venta=fields.One2many(
        "llantas_config.status_ventas",
        "name",
        string="Estatus",
        tracking=True,

    )

    ventas_status = fields.Selection([
        ('01','Pendiente'),
        ('02','Debito en curso'),
        ('03','Traspaso'),
        ('04','Guia pendiente'),
        ('05','Enviado'),
        ('06','Entregado'),
        ('07','Cerrado'),
        ('08','Incidencia'),
        ('09','Devolución'),
        ('10','Cancelado por stock'),
        ('11','Cancelado por el cliente'),
        ('12','Cancelado'),], 
        string="Estado de la venta", 
        default='01', 
        tracking=True, 
        store=True)

    lineas_orden = fields.Many2one(
        "sale.order.line",
        string="lineas",
    )

    fecha_venta=fields.Datetime(
        string="Fecha venta",
        default=fields.Datetime.now,
        tracking=True,
        store=True
    )

    mostrar_comision=fields.Boolean(
        related="marketplace.mostrar_comision",
    )

    mostrar_envio=fields.Boolean(
        related="marketplace.mostrar_envio",
    )

    es_killer = fields.Boolean(
        string="Es killer?",
        default=False,
        compute='_compute_es_killer',
        store=True,
    )

    @api.depends('order_line.is_killer')
    def _compute_es_killer(self):
        for rec in self:
            rec.es_killer = any(line.is_killer for line in rec.order_line)

    @api.onchange('marketplace', 'comision', 'iva', 'envio', 'guia', 'folio_venta', 'marketplace_name', 'partner_id', 'comprador_id', 'fecha_venta')
    def _onchange_sale(self):
        for rec in self:
            tab = self.env['llantas_config.ctt_llantas'].search([('sale_id','=',rec.id)])
            if tab:
                tab.write({
                    'partner_name': rec.partner_id.id,
                    'marketplace': rec.marketplace,
                    'fecha': rec.fecha_venta,
                    'comprador_id':rec.comprador_id.id,
                    'comprador_name':rec.comprador_id.name,
                    'comision':rec.comision,
                    'envio':rec.envio,
                    'marketplace_name':rec.marketplace.name,
                    'tipo_factura': rec.tipo_factura,
                    'no_recoleccion': rec.guia,
                    'numero_guia' : rec.yuju_carrier_tracking_ref
                })
        
    

    def action_confirm(self):
        res = super(sale_order_inherit, self).action_confirm()
        if self.marketplace.id:
            if self.marketplace.category_id.id:
                if self.marketplace.category_id not in self.partner_id.category_id:
                    self.partner_id.category_id += self.marketplace.category_id
        for line in self.order_line:
            if line.costo_proveedor != 0.00:
                if line.product_id.product_tmpl_id.es_paquete == True:
                    line.write({'costo_proveedor_2': ((line.costo_proveedor * float(line.product_id.product_tmpl_id.pkg_type)) * line.product_uom_qty)})
                else:
                    line.write({'costo_proveedor_2': line.costo_proveedor})
                line.compute_costo_proveedor_total()
        return res

    # def _prepare_invoice(self):
    #     inv = super(sale_order_inherit, self)._prepare_invoice()
    #     if self.marketplace.id:
    #         if self.marketplace.diarios_id.id:
    #             if self.marketplace.diarios_id not in self.journal_id:
    #                 self.journal_id = self.marketplace.diarios_id
    #     return inv
    
    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        if self.company_id and getattr(self.company_id, 'name', '') != 'ADRONE':
            if self.marketplace.id:
                if self.marketplace.diarios_id.id:
                    invoice_vals.update({'journal_id': self.marketplace.diarios_id.id})
        return invoice_vals

    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'folio_venta': False,
            'guia':False
        })
        return super(sale_order_inherit, self).copy(default)
        
    # user = self.env.user
    
    def create_purchase_for_sale_order(self):
        for rec in self:
            if rec.state == 'sale':
                for line in rec.order_line:
                    # Verifica las condiciones iniciales antes de crear la orden de compra
                    if rec.amount_total < (line.product_uom_qty * line.costo_proveedor) and rec.es_killer == False:
                        raise UserError("La creación de la orden de compra no es posible en este momento debido a que el total de la orden de compra excede el total de la orden de venta asociada.")
                    
                    if line.qty_available_today > 0:
                        raise UserError("Actualmente, no es posible generar una orden de compra debido a que hay productos disponibles en stock. Se recomienda revisar el inventario existente antes de generar una nueva orden de compra.")
                    
                    # Procede con la creación o actualización de la orden de compra
                    else:
                        if line.proveedor_id:
                            # Busca la moneda
                            moneda = self.env['res.currency'].search([('name', '=', rec.currency_id.name)])
                            if not moneda:
                                raise UserError("Moneda no encontrada")
                            id_de_la_moneda = moneda.id
                            
                            # Si no existen líneas de orden de compra previas, crea una nueva orden de compra
                            if not line.purchase_line_ids:
                                # Crea la nueva orden de compra
                                nueva_cotizacion_compra = self.env['purchase.order'].create({
                                    'partner_id': line.proveedor_id.partner_id.id,
                                    'currency_id': id_de_la_moneda,
                                    'company_id': self.env.company.id,
                                    'picking_type_id': self.warehouse_id.in_type_id.id,
                                    'auto_sale_order_id': self.id,
                                })
                                
                                # Si el producto no es un paquete
                                if not line.product_id.product_tmpl_id.es_paquete:
                                    # Crea la línea de orden de compra
                                    purchase_line = self.env['purchase.order.line'].create({
                                        'order_id': nueva_cotizacion_compra.id,
                                        'product_id': line.product_id.id,
                                        'name': line.product_id.name,
                                        'product_qty': line.product_qty,
                                        'product_uom': line.product_uom.id,
                                        'price_unit': line.costo_proveedor,
                                        'sale_order_id': rec.id,
                                        'codigo_proveedor': line.codigo_proveedor,
                                    })
                                    
                                    # Actualiza la relación entre la línea de venta y la nueva línea de compra
                                    line.write({'purchase_line_ids': [(4, purchase_line.id)]})
                                    
                                    # Llama a la función compute_orden_compra
                                    llantas = self.env['llantas_config.ctt_llantas'].search([('sale_id', '=', rec.id)], limit=1)
                                    if llantas:
                                        llantas.compute_orden_compra()
    
                                    # Crea la notificación
                                    if rec.user_id and rec.user_id.parent_id:
                                        self.env['mail.message'].create({
                                            'model': 'sale.order',
                                            'res_id': self.id,
                                            'message_type': 'notification',
                                            'subtype_id': 2,
                                            'email_from': self.user_id.login,
                                            'author_id': self.user_id.parent_id.id,
                                            'body': "Orden de compra generada"
                                        })
                                
                                # Si el producto es un paquete, maneja la lista de materiales
                                else:
                                    lmateriales = self.env['mrp.bom.line'].search([('parent_product_tmpl_id', '=', line.product_id.product_tmpl_id.id)])
                                    if lmateriales:
                                        for lmat in lmateriales:
                                            # Crea líneas de compra para los materiales
                                            purchase_line = self.env['purchase.order.line'].create({
                                                'order_id': nueva_cotizacion_compra.id,
                                                'product_id': lmat.product_id.id,
                                                'name': lmat.product_id.product_tmpl_id.name,
                                                'product_qty': lmat.product_qty,
                                                'product_uom': line.product_uom.id,
                                                'price_unit': line.costo_proveedor,
                                                'sale_order_id': rec.id,
                                                'codigo_proveedor': line.codigo_proveedor,
                                            })
                                            # Actualiza la relación
                                            line.write({'purchase_line_ids': [(4, purchase_line.id)]})
                                            
                                            # Llama a la función compute_orden_compra
                                            llantas = self.env['llantas_config.ctt_llantas'].search([('sale_id', '=', rec.id)], limit=1)
                                            if llantas:
                                                llantas.compute_orden_compra()
    
                                            # Crea la notificación
                                            if rec.user_id and rec.user_id.parent_id:
                                                self.env['mail.message'].create({
                                                    'model': 'sale.order',
                                                    'res_id': self.id,
                                                    'message_type': 'notification',
                                                    'subtype_id': 2,
                                                    'email_from': self.user_id.login,
                                                    'author_id': self.user_id.parent_id.id,
                                                    'body': "Orden de compra generada"
                                                })
                                    else:
                                        raise UserError('Este paquete no tiene lista de materiales, favor de agregarla.')
                            
                            # Si ya existen líneas de compra, actualiza la orden de compra existente
                            else:
                                purchase_id = False
                                for purchase_line in line.purchase_line_ids:
                                    purchase_id = purchase_line.order_id
                                purchase_id.write({
                                    'partner_id': line.proveedor_id.partner_id.id,
                                    'currency_id': id_de_la_moneda,
                                    'company_id': self.env.company.id,
                                    'picking_type_id': self.warehouse_id.in_type_id.id,
                                })
    
                                for purchase_line in purchase_id.order_line:
                                    if purchase_line.sale_line_id.id == line.id:
                                        lmateriales = self.env['mrp.bom.line'].search([('parent_product_tmpl_id', '=', line.product_id.product_tmpl_id.id)])
                                        if lmateriales:
                                            for lmat in lmateriales:
                                                purchase_line.write({
                                                    'product_id': lmat.product_id.id,
                                                    'name': lmat.product_id.product_tmpl_id.name,
                                                    'product_qty': lmat.product_qty,
                                                    'product_uom': line.product_uom.id,
                                                    'price_unit': line.costo_proveedor,
                                                })
                                        else:
                                            purchase_line.write({
                                                'product_id': line.product_id.id,
                                                'name': line.product_id.name,
                                                'product_qty': line.product_qty,
                                                'product_uom': line.product_uom.id,
                                                'price_unit': line.costo_proveedor,
                                                'codigo_proveedor': line.codigo_proveedor,
                                            })
    
                                # Llama a la función compute_orden_compra tras actualizar la orden de compra
                                llantas = self.env['llantas_config.ctt_llantas'].search([('sale_id', '=', rec.id)], limit=1)
                                if llantas:
                                    llantas.compute_orden_compra()
    
                                # Crea la notificación de actualización
                                if rec.user_id:
                                    self.env['mail.message'].create({
                                        'model': 'sale.order',
                                        'res_id': self.id,
                                        'message_type': 'notification',
                                        'subtype_id': 2,
                                        'email_from': self.user_id.login,
                                        'author_id': self.user_id.id,
                                        'body': "Orden de compra actualizada"
                                    })

    


    detailed_info = fields.Html(
        string="Información de entrega",
        compute='_compute_detailed_info',
        inverse='_set_detailed_info',
        # store=True
    )

    traspaso_name=fields.Char(
        string="Traspaso",
        related="picking_ids.name",
        tracking=True
    )
    
    
    guia=fields.Char(
        string="Guía de rastreo",
        tracking=True
    )
    
    # @api.model
    # def create(self, values):
    #     guia = values.get('guia', self.guia)
    #     if guia:
    #         ventas = rec.env['sale.order'].search([
    #                 ('guia', '=', guia),
    #                 ('guia', 'not in', [False, ""]),
    #                 ('guia', '!=', False),])
    #         if len(ventas) > 0:
    #             raise UserError('El número de guía debe ser único.')
    #     return super(sale_order_inherit, self).create(values)
    
    link_guia=fields.Char(
        string="Link guia",
        tracking=True
    )

    estado_traspaso = fields.Selection([
        ('draft','Borrador'),
        ('waiting','En espera de otra operación'),
        ('confirmed','En espera'),
        ('assigned','Listo'),
        ('done','Hecho'),
        ('cancel','Cancelado'),
    ], string="Estado publicación", related="picking_ids.state", tracking=True, store=True)

    llantas_config_carrier_id=fields.Many2one(
        "llantas_config.carrier",
        string="Carrier", 
        tracking=True
    )

    @api.depends('picking_ids', 'picking_ids.carrier_tracking_ref')
    def _compute_detailed_info(self):
        for rec in self:
            detailed_info = "<table class='table'>"
            detailed_info += "<tr>"
            detailed_info += "<th>Entrega</th>"
            detailed_info += "<th>Carrier</th>"
            detailed_info += "<th>Guía</th>"
            detailed_info += "<th>Link</th>"
            detailed_info += "<th>Estado</th>"
            detailed_info += "</tr>"
            
            for orden in rec.picking_ids:
                detailed_info += "<tr>"
                detailed_info += "<td>{}</td>".format(orden.display_name)
                detailed_info += "<td>{}</td>".format(orden.carrier.display_name)
                detailed_info += "<td>{}</td>".format(orden.carrier_tracking_ref)
                detailed_info += "<td>{}</td>".format(orden.link_guia)
                detailed_info += "<td>{}</td>".format(orden.state)
                detailed_info += "</tr>"

            detailed_info += "</table>"
            rec.detailed_info = detailed_info

    def _set_detailed_info(self):
        for rec in self:
            # Verifica si el campo 'carrier_tracking_ref' pertenece a 'stock.picking'
            if rec.picking_ids:
                # Tomamos el primer registro de picking_ids y actualizamos su carrier_tracking_ref
                picking = rec.picking_ids[0]
                picking.write({'carrier_tracking_ref': rec.detailed_info})
            # Puedes agregar el código aquí para procesar la entrada del usuario si es necesario
            # Puedes acceder al valor ingresado por el usuario con rec.detailed_info
            pass


    detailed_name=fields.Char(
        string="Folio entrega",
        related="picking_ids.name",
    )

    def crear_actividad(self):
        for rec in self:
            if rec.comprador_id:
                actividad_tipo_id = self.env.ref('mail.mail_activity_data_todo').id
                model_sale_order_id = self.env.ref('sale.model_sale_order').id
                
                existing_activity = rec.env['mail.activity'].search([
                    ('res_model', '=', 'sale.order'),
                    ('res_id', '=', rec.id),
                    ('activity_type_id', '=', actividad_tipo_id),
                    ('user_id', '=', rec.comprador_id.user_id.id if rec.comprador_id.user_id.id else False)
                ])
    
                if not existing_activity:
                    if rec.comprador_id.user_id.id:
                        rec.env['mail.activity'].create({
                            'res_model': 'sale.order',
                            'res_model_id': model_sale_order_id,
                            'res_id': rec.id,
                            'activity_type_id': actividad_tipo_id,
                            'summary': 'Orden de venta pendiente',
                            'date_deadline': fields.Datetime.now(),
                            'user_id': rec.comprador_id.user_id.id,
                            'note': '',
                        })
                    else:
                        raise UserError("Debe seleccionar un usuario de compras válido")
                else:
                    pass

    tipo_factura = fields.Selection([
        ('01','Publico en general'),
        ('02','Cliente')], string="Tipo de facturación", store=True, tracking=True)

    def compute_orden_compra(self):
        for rec in self:
            purchase_orders = rec._get_purchase_orders()
            if purchase_orders:
                rec.purchase_order_id = purchase_orders[0].id  # Asignar el primer pedido de compra
            else:
                rec.purchase_order_id = False

    purchase_order_id = fields.Many2one(
        'purchase.order',
        compute='compute_orden_compra',
        string='Orden de compra',
        store=True,
    )

    fee_import = fields.Float(string='Fee Import', compute='compute_fee_import', store=True)

    fee_sale = fields.Float(
        string="Cargo por venta",
        compute="_compute_amounts",
        store=True,
    )

    
    def normalize_string(self, s):
        """Elimina acentos y convierte a minúsculas."""
        return ''.join(
            c for c in unicodedata.normalize('NFD', s)
            if unicodedata.category(c) != 'Mn'
        ).lower()


    def compute_fee_import(self):
        for rec in self:
            fee = 0.0  # Valor por defecto si no se encuentra tarifa
    
            if rec.marketplace and rec.yuju_order_data and rec.yuju_marketplace_fee == 0.00:
                # Buscamos el marketplace en la misma compañía
                marketplace = self.env['llantas_config.marketplaces'].search([
                    ('name', 'ilike', rec.marketplace.name),
                    ('company_id', '=', rec.company_id.id)
                ], limit=1)
    
                if marketplace:
                    # Si encontramos el marketplace, obtenemos la tarifa del campo 'fee_marketplace'
                    fee = marketplace.fee_marketplace or 0.0
                else:
                    raise UserError(
                        f"No se encontró un marketplace que coincida con '{rec.marketplace.name}' para la compañía '{rec.company_id.name}'."
                    )
    
            # Asignamos el valor de la tarifa al campo fee_import
            rec.fee_import = fee
    

    
    
    @api.depends('order_line.price_subtotal', 'order_line.price_tax', 'order_line.price_total', 'fee_sale')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for order in self:
            order = order.with_company(order.company_id)
            order_lines = order.order_line.filtered(lambda x: not x.display_type)

            if order.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = order.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in order_lines
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(order.currency_id, {}).get('amount_untaxed', 0.0)
                amount_tax = totals.get(order.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(order_lines.mapped('price_subtotal'))
                amount_tax = sum(order_lines.mapped('price_tax'))

            order.amount_untaxed = amount_untaxed
            order.amount_tax = amount_tax
            order.amount_total = order.amount_untaxed + order.amount_tax
            if order.marketplace and order.yuju_order_data and order.yuju_marketplace_fee == 0.00:
                order.fee_sale = (order.amount_untaxed + order.amount_tax) * order.fee_import
            # raise UserError(str((order.amount_untaxed + order.amount_tax) * (1 + order.fee_import)))

     
class sale_order_line_inherit(models.Model):
    _inherit = 'sale.order.line'
    _description='Lineas de la orden de venta'

    proveedor_id=fields.Many2one(
        "product.supplierinfo",
        # related="product_id.product_tmpl_id.partner_id",
        store=True,
        tracking=True,
    )
    

    costo_proveedor=fields.Float(
        related="proveedor_id.price",
        string="Costo",
        tracking=True,
    )

    @api.depends('purchase_line_ids')
    def compute_costo_proveedor_total(self):
        for rec in self:
            costo_proveedor_total = 0  # Inicializa la variable
            for line in rec.purchase_line_ids:
                costo_proveedor_total += line.price_unit  # Asegúrate de actualizar la variable adecuadamente
            rec.costo_proveedor_total = costo_proveedor_total
        
    # def compute_costo_proveedor_total(self):
    #     for rec in self:
    #         if rec.costo_proveedor:
    #             costo_proveedor_total = rec.costo_proveedor * rec.product_uom_qty
    #         rec.write({'costo_proveedor_total': costo_proveedor_total})
            
    costo_proveedor_total=fields.Float(
        compute="compute_costo_proveedor_total",
        string="Costo total",
        store=True,
    )

   
                

    costo_proveedor_2=fields.Float(
        string="Costo proveedor guardado",
    )

    
    codigo_proveedor=fields.Char(
        related="proveedor_id.product_code",
        string="Codigo proveedor",
        trackin=True,
    )

    importe_descuento=fields.Float(
        string="Importe descuento",
    )

    def compute_precio_antes_dec(self):
        for rec in self:
            rec.precio_antes_dec = rec.price_unit + rec.importe_descuento
    precio_antes_dec=fields.Float(
        string="Precio antes descuento",
        compute=compute_precio_antes_dec,
    )

    @api.onchange('product_id')
    def onchange_product_id_for_llantas_config(self):
        if self.product_id.id:
            self.name = self.product_id.name

    marketplace_id = fields.Char(
        string="Canal de venta",
        compute="_compute_marketplace_id",
        store=True
    )

    @api.depends('order_id.marketplace.name')
    def _compute_marketplace_id(self):
        for line in self:
            line.marketplace_id = line.order_id.marketplace.name
    
    link_venta=fields.Char(
        string="Link de venta",
        related="order_id.link_venta",
        store=True
    )
    folio_venta=fields.Char(
        string="Folio de venta",
        related="order_id.folio_venta",
        store=True
    )
    fecha_venta=fields.Datetime(
        string="Fecha venta",
        related="order_id.fecha_venta",
        store=True
    )
    partner_id=fields.Many2one(
        string="Cliente",
        related="order_id.partner_id",
        store=True,
    )
    comprador=fields.Char(
        string="Comprador",
        related="order_id.comprador_id.name",
        store=True
    )
    estado_venta=fields.Selection([
        ('01','Pendiente'),
        ('02','Debito en curso'),
        ('03','Traspaso'),
        ('04','Guia pendiente'),
        ('05','Enviado'),
        ('06','Entregado'),
        ('07','Cerrado'),
        ('08','Incidencia'),
        ('09','Devolución'),], string="Estatus", related="order_id.ventas_status", store=True)
    
    comision=fields.Float(
        string="Comisión",
        related="order_id.comision",
        store=True
    )
    envio=fields.Float(
        string="Envio",
        related="order_id.envio",
        store=True
    )

    nombre_producto=fields.Char(
        string="Producto",
        related="product_id.product_tmpl_id.name",
        store=True,
        # company_dependent=True,
    )

    codigo_prod=fields.Char(
        string="sku",
        related="product_id.product_tmpl_id.default_code",
        store=True
    )
    #Listas de precios
    @api.onchange('product_id','proveedor_id')
    def onchange_product_id_for_llantired(self):
        if self.product_id.id and self.order_id.id and self.order_id.partner_id.id and self.order_id.pricelist_id.id:
            self.price_unit = self.pricelist_item_id._compute_price(self.product_id, self.product_uom_qty, self.product_uom, self.order_id.date_order, self.order_id.currency_id, self.costo_proveedor)


    is_killer = fields.Boolean(
        string="Es killer?",
        compute='_compute_killer',
        store=True,
        default=False,
    )
    
    killer_id = fields.Many2one(
        'llantas_config.killer_list',
        string="Killer ID",
        compute='_compute_killer',
        store=True,
    )
    
    killer_id_killer_price = fields.Float(
        string="Precio killer",
        store=True,
    )
    
    killer_id_base_price = fields.Float(
        string="Precio base killer",
        store=True,
    )
    
    killer_id_promotion_price = fields.Float(
        string="Precio de promoción killer",
        store=True,
    )
    
    total_con_killer = fields.Float(
        string="Total con killer",
        compute='_compute_total_con_killer',
        store=True,
    )
    
    @api.depends('product_id', 'order_id.marketplace')
    def _compute_killer(self):
        fecha_actual = datetime.now()  # Obtener la fecha actual
        for line in self:
            # Filtrar los registros 'killer' activos y válidos para la fecha actual
            killers = line.product_id.product_tmpl_id.killer_ids.filtered(
                lambda k: k.marketplace_id == line.order_id.marketplace and
                          k.initial_date and 
                          k.initial_date <= fecha_actual <= (k.final_date or fecha_actual) and
                          k.status == 'active'
            )
            # Asignar el primer registro que cumpla con los criterios o None si no hay
            killer = killers[:1] if killers else None
            line.killer_id = killer.id if killer else None
            line.is_killer = bool(killer)
    
            if killer:
                # Guardar los valores directamente en los campos persistentes
                line.killer_id_killer_price = killer.killer_price
                line.killer_id_base_price = killer.base_price
                line.killer_id_promotion_price = killer.promotion_price
    
                # Si cumple la condición de killer, actualizar price_unit con el precio de promoción
                line.price_unit = line.killer_id_promotion_price
            else:
                # Limpiar los valores si no hay killer aplicable
                line.killer_id_killer_price = 0.0
                line.killer_id_base_price = 0.0
                line.killer_id_promotion_price = 0.0
    
    @api.depends('price_total', 'killer_id_killer_price')
    def _compute_total_con_killer(self):
        for rec in self:
            # Calcular el total considerando el precio killer si es aplicable
            rec.total_con_killer = rec.price_total + (rec.killer_id_killer_price or 0)
    
        
    link_venta=fields.Char(
        string="Link de venta",
        related="order_id.link_venta",
        store=True
    )

    @api.depends('purchase_line_ids', 'purchase_line_ids.price_unit')
    def compute_costo_orden_compra(self):
        for rec in self:
            costo_orden_compra = 0
            for purchase_line in rec.purchase_line_ids:
                costo_orden_compra += purchase_line.price_unit * purchase_line.product_uom_qty  # Sumar el costo total de la orden de compra
            rec.costo_orden_compra = costo_orden_compra
    
    costo_orden_compra = fields.Float(
        compute=compute_costo_orden_compra,
        string="Costo Orden de Compra",
        store=False,  # Cambiado a False si no necesitas almacenar el valor
    )

    @api.depends('purchase_line_ids', 'purchase_line_ids.invoice_lines', 'purchase_line_ids.invoice_lines.quantity', 'purchase_line_ids.invoice_lines.price_unit')
    def compute_costo_orden_facturada(self):
        for rec in self:
            costo_orden_facturada = 0
            for purchase_line in rec.purchase_line_ids:
                for invoice_line in purchase_line.invoice_lines:
                    costo_orden_facturada += (invoice_line.price_unit * invoice_line.quantity)  # Acumular el costo facturado
            rec.costo_orden_facturada = costo_orden_facturada
    
    costo_orden_facturada = fields.Float(
        string="Costo Orden Facturada",
        compute=compute_costo_orden_facturada,
        store=False,  # Cambiado a False si no necesitas almacenar el valor
    )

    order_id=fields.Many2one(
        "sale.order",
        string="Orden de venta",
        store=True,
    )


    @api.depends('envio', 'comision', 'order_id', 'order_id.amount_untaxed', 'costo_orden_facturada', 'costo_orden_compra', 'killer_id_killer_price')
    def _compute_t1(self):
        for rec in self:
            # Inicializamos las variables
            t1 = t2 = t3 = 0
            t1_porcentaje = t2_porcentaje = t3_porcentaje = "0.00%"
    
            if rec.order_id and rec.killer_id_killer_price and rec.order_id.amount_untaxed != 0:
                killer_price = rec.killer_id_killer_price
                
                # Cálculo para T1
                t1 = (rec.order_id.amount_untaxed - (rec.comision / 1.16) - (rec.envio / 1.16) + (killer_price / 1.16) - rec.product_id.standard_price)
                t1_porcentaje = "{:.2f}%".format((t1 / rec.order_id.amount_untaxed) * 100)
    
                # Cálculo para T2 (solo si hay costo de orden de compra)
                if rec.costo_orden_compra > 0:
                    t2 = (rec.order_id.amount_untaxed - (rec.comision / 1.16) - (rec.envio / 1.16) + (killer_price / 1.16) - rec.costo_orden_compra)
                    t2_porcentaje = "{:.2f}%".format((t2 / rec.order_id.amount_untaxed) * 100)
    
                # Cálculo para T3 (solo si hay costo facturado)
                if rec.costo_orden_facturada > 0:
                    t3 = (rec.order_id.amount_untaxed - (rec.comision / 1.16) - (rec.envio / 1.16) + (killer_price / 1.16) - rec.costo_orden_facturada)
                    t3_porcentaje = "{:.2f}%".format((t3 / rec.order_id.amount_untaxed) * 100)
    
            # Asignar valores a los campos
            rec.t1 = t1
            rec.t2 = t2
            rec.t3 = t3
            rec.t1_porcentaje = t1_porcentaje
            rec.t2_porcentaje = t2_porcentaje
            rec.t3_porcentaje = t3_porcentaje


    t1=fields.Float(
        string="T1",
        compute="_compute_t1",
        store=True,
    )

    t1_porcentaje=fields.Char(
        string="T1 %",
        compute="_compute_t1",
        store=True,
        

    )

    t2=fields.Float(
        string="T2",
        compute="_compute_t1",
        store=True,


    )

    t2_porcentaje=fields.Char(
        string="T2 %",
        compute="_compute_t1",
        store=True,

    )

    t3=fields.Float(
        string="T3",
        compute="_compute_t1",
        store=True,


    )

    t3_porcentaje=fields.Char(
        string="T3 %",
        compute="_compute_t1",
        store=True,

    )
    


    
           
