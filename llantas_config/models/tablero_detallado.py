# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _
import logging
import datetime
from odoo.exceptions import Warning
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)

class ctrl_sale_order_line(models.Model): 
    _inherit = "sale.order.line"
    _description = "detallado"
    # _inherit = ['mail.thread', 'mail.activity.mixin']


    producto=fields.Char(
        related="product_id.name",
        string="Producto",
    )

    sale_id=fields.Many2one(
        "llantas_config.ctt_llantas",
        string="Venta", 
        store=True,
    )

    ## Esto provoca bug que no se registre el name de las líneas de producto correctamente. Será comentada para evitarlo
    # name=fields.Char(
    #     related="sale_id.name",
    #     string="Nombre",
    #     store=True,
    # )

    comprador_id=fields.Many2one(
        "hr.employee",
        related="sale_id.comprador_id",
        string="Comprador",
        company_dependent=True,
        store=True,
    )

    # comprador=fields.Char(
    #     related="comprador_id.name",
    #     string="Comprador",
    #     store=True,
    # )
 

    # partner_name=fields.Char(
    #     related="sale_id.partner_id.name",
    #     string="Cliente",
    #     store=True,
    # )
    
    # marketplace=fields.Char(
    #     related="sale_id.marketplace.name",
    #     string="Marketplace",
    #     tracking=True,
    #     store=True,
    # )

    # proveedor_id=fields.Many2one(
    #     "res.partner",
    #     string="Proveedor",

    # )
   
    # def compute_orden_compra(self):
    #     for rec in self:
    #         rec.orden_compra = rec.sale_id._get_purchase_orders().id
    # orden_compra=fields.Many2one(
    #     "purchase.order",
    #     compute=compute_orden_compra,
    #     string="Orden de compra",
    # )

    

    # def compute_factura_prov(self):
    #     for rec in self:
    #         rec.factura_prov = rec.sale_id._get_purchase_orders().invoice_ids
    # factura_prov=fields.Many2one(
    #     "account.move",
    #     string="Factura proveedor",
    #     compute=compute_factura_prov
    # )
    
    # num_cliente=fields.Char(
    #     string="Num. Cliente",
    #     tracking=True
    # )
    
    # factura_cliente=fields.Char(
    #     related="sale_id.invoice_ids.name",
    #     string="Factura cliente",

    # )


    # status_id = fields.Selection([
    #     ('01','Pendiente'),
    #     ('02','Debito en curso'),
    #     ('03','Traspaso'),
    #     ('04','Guia pendiente'),
    #     ('05','Enviado'),
    #     ('06','Entregado'),
    #     ('07','Cerrado'),
    #     ('08','Incidencia'),
    #     ('09','Devolución'),],
    #     related="sale_id.ventas_status",
    #     string="Status",
    #     store=True                                
    # )
    
    # fecha=fields.Datetime(
    #     string="Fecha",
    #     store=True
    # )
    
    # dias=fields.Integer(
    #     string="Dias",
    #     store=True,
    # )

    # comentarios=fields.Char(
    #     string="Comentarios",
    #     tracking=True
    # )

    # orden_entrega=fields.One2many(
    #     "stock.picking",
    #     "carrier_tracking_ref",
    #     string="No. Guia",
    #     related="sale_id.picking_ids",

    # )

    # @api.depends('orden_entrega','orden_entrega.carrier_tracking_ref')
    # def compute_guias(self):
    #     for rec in self:
    #         guias = ""
    #         for orden in rec.orden_entrega:
    #             guias += str(orden.carrier_tracking_ref) + ", "
    #         guias = guias[:-2]
    #         rec.guias = guias
    # guias = fields.Char(
    #     string="Guías",
    #     compute=compute_guias,

    # )

    # @api.depends('orden_entrega','orden_entrega.carrier_tracking_ref')
    # def compute_detailed_info(self):
    #     for rec in self:
    #         detailed_info = ""
    #         detailed_info += "<table class='table'>"
    #         detailed_info += "<tr>"
    #         detailed_info += "<th>Entrega</th>"
    #         detailed_info += "<th>Carrier</th>"
    #         detailed_info += "<th>Guía</th>"
    #         detailed_info += "</tr>"
    #         for orden in rec.orden_entrega:
    #             detailed_info += "<tr>"
    #             detailed_info += "<td>"+str(orden.display_name)+"</td>"
    #             detailed_info += "<td>"+str(orden.carrier.display_name)+"</td>"
    #             detailed_info += "<td>"+str(orden.carrier_tracking_ref)+"</td>"
    #         detailed_info += "</tr>"
    #         detailed_info += "</table>"

    #         rec.detailed_info = detailed_info
    # detailed_info = fields.Html(
    #     string="Información detallada",
    #     compute=compute_detailed_info,

    # )

    # carrier = fields.Many2one(
    #     "llantas_config.carrier",
    #     string="Carrier",
    #     store=True,
    # )

    # def compute_no_recoleccion(self):
    #     for rec in self:
    #         rec.no_recoleccion = rec.sale_id._get_purchase_orders().picking_ids.no_recoleccion
    # no_recoleccion=fields.Char(
    #     compute=compute_no_recoleccion,
    #     string="No. Recoleccion",
    # )

    # link_venta=fields.Char(
    #     related="sale_id.link_venta",
    #     string="Link venta",
    #     store=True,
    # )

    # no_venta=fields.Char(
    #     related="sale_id.folio_venta",
    #     string="No. Venta",
    # )

    # comision=fields.Float(
    #     string="Comisión",
    # )

    # envio=fields.Float(
    #     string="Envio",
    # )

    # company_id=fields.Many2one(
    #     "res.company",
    #     related="sale_id.company_id",
    #     string="Empresa",
    #     store=True,
    # )

    # def compute_tdp(self):
    #     for rec in self:
    #         rec.tdp = rec.sale_id._get_purchase_orders().partner_ref
    # tdp=fields.Char(
    #     string="Referencia compra (TDP)",
    #     compute=compute_tdp
    # )
    
    # @api.model
    # def create(self, values):
    #     if 'sale_id' in values:
    #         sale_id = self.env['sale.order'].browse(values['sale_id'])
    #         values['proveedor_id'] = sale_id._get_purchase_orders().partner_id
    #     return super(ctrl_llantas, self).create(values)
    
    # def write(self, values):
    #     for rec in self:
    #         if 'sale_id' in values:
    #             sale_id = rec.env['sale.order'].browse(values['sale_id'])
    #             values['proveedor_id'] = sale_id._get_purchase_orders().partner_id
    #         record = super(ctrl_llantas, rec).write(values)
    #     return self

    # productos_orden=fields.Many2one(
    #     "sale.order.line",
    #     string="Líneas de la orden",
    # )
    
    
