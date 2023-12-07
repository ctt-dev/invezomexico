from odoo import models, fields, api, _
import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)
import datetime

class sale_order_inherit(models.Model):
    _inherit = 'sale.order'
    _description='Orden de venta'

    marketplace = fields.Many2one(
        "llantas_config.marketplaces",
        string="Marketplace",
        tracking=True,
        store=True,
        company_dependent=True,
        
    )

    marketplace_name2 = fields.Char(
        string="Canal de venta",
        related="marketplace.name",
        store=True,
        # company_dependent=True,
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
        company_dependent=True,
        store=True,
    )

    folio_venta=fields.Char(
        string="No. Venta",
        tracking=True,
        store=True,

    )

    @api.model
    def create(self, values):
        if 'folio_venta' in values:
            venta_ids=self.env['sale.order'].search([('folio_venta','=',values['folio_venta']),('folio_venta','!=',False)])
            if len(venta_ids) > 0:
                raise UserError('El número de venta debe ser único.')
            # Realizar operaciones adicionales si es necesario
        return super(sale_order_inherit, self).create(values) 
        
    def write(self, values):
        for rec in self:
            if 'folio_venta' in values:
                venta_ids=rec.env['sale.order'].search([('folio_venta','=',values['folio_venta']),('id','!=',rec.id),('folio_venta','!=',False)])
                if len(venta_ids) > 0:
                    raise UserError('El número de venta debe ser único.')
        return super(sale_order_inherit, self).write(values)
    
    
    

    link_venta=fields.Char(
        string="Link de venta",
        tracking=True,
    )

    link_facturacion=fields.Char(
        string="Link de facturacion",
        tracking=True,
        compute="_compute_link"
    )

    def _compute_link(self):
        if(self.folio_venta):
            self.link_facturacion = self.env['ir.config_parameter'].get_param('web.base.url')+'/autofacturador/'+self.folio_venta
        else:
            self.link_facturacion = ''
            
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
        ('09','Devolución'),], 
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

    

    def action_confirm(self):
        res = super(sale_order_inherit, self).action_confirm()
        if self.marketplace.id:
            if self.marketplace.category_id.id:
                if self.marketplace.category_id not in self.partner_id.category_id:
                    self.partner_id.category_id += self.marketplace.category_id
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
        })
        return super(sale_order_inherit, self).copy(default)
        
    # user = self.env.user
    
    def create_purchase(self):
        for rec in self:
            if rec.state == 'sale':
                for line in rec.order_line:
                    if line.proveedor_id:
                        moneda = self.env['res.currency'].search([('name', '=', rec.currency_id.name)])
                        if moneda:
                            id_de_la_moneda = moneda.id
                        else:
                            raise UserError("Moneda no encontrada")

                        if len(line.purchase_line_ids) == 0:
                            nueva_cotizacion_compra = self.env['purchase.order'].create({
                                'partner_id': line.proveedor_id.partner_id.id,
                                'currency_id': id_de_la_moneda,
                                'company_id': self.env.company.id,
                            })
                            
                            purchase_line = self.env['purchase.order.line'].create({
                                'order_id': nueva_cotizacion_compra.id,
                                'product_id': line.product_id.id,
                                'name': line.product_id.name,
                                'product_qty': line.product_qty,
                                'product_uom': line.product_uom.id,
                                'price_unit': line.costo_proveedor,
                                'sale_order_id':rec.id,
                            })
                            line.write({'purchase_line_ids': purchase_line})
                            self.env['mail.message'].create({
                                'model': 'sale.order',
                                'res_id': self.id,
                                'message_type': 'notification',
                                'subtype_id': 2,
                                'email_from': self.user_id.login,
                                'author_id': self.user_id.id,
                                'body': "Orden de compra generada "
                            })
                        else:
                            purchase_id = False
                            for purchase_line in line.purchase_line_ids:
                                purchase_id = purchase_line.order_id
                            purchase_id.write({
                                'partner_id': line.proveedor_id.partner_id.id,
                                'currency_id': id_de_la_moneda,
                                'company_id': self.env.company.id,
                            })
                            for purchase_line in purchase_id.order_line:
                                if purchase_line.sale_line_id.id == line.id:
                                    # raise ValidationError(123)
                                    purchase_line.write({
                                        'product_id': line.product_id.id,
                                        'name': line.product_id.name,
                                        'product_qty': line.product_qty,
                                        'product_uom': line.product_uom.id,
                                        'price_unit': line.costo_proveedor,
                                    })
                            self.env['mail.message'].create({
                                'model': 'sale.order',
                                'res_id': self.id,
                                'message_type': 'notification',
                                'subtype_id': 2,
                                'email_from': self.user_id.login,
                                'author_id': self.user_id.id,
                                'body': "Orden de compra actualizada "
                            })
                                    
                        
                        purchase_order_ids = self._get_purchase_orders().ids
                        action = {
                            'res_model': 'purchase.order',
                            'type': 'ir.actions.act_window',
                        }
                        if len(purchase_order_ids) == 1:
                            action.update({
                                'view_mode': 'form',
                                'res_id': purchase_order_ids[0],
                            })
                        else:
                            action.update({
                                'name': _("Purchase Order generated from %s", self.name),
                                'domain': [('id', 'in', purchase_order_ids)],
                                'view_mode': 'tree,form',
                            })
                        return action
                        
                        
                    else:
                        raise UserError("Se debe seleccionar un proveedor para cada línea de orden de venta")
            
            else:
                raise UserError("La orden de venta necesita estar confirmada")
            
        
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
        store=True
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
    