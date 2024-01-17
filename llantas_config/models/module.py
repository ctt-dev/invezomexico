# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _
import logging
import datetime
from odoo.exceptions import Warning
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from urllib.parse import urlparse, urlunparse, urljoin
_logger = logging.getLogger(__name__)

class ctrl_llantas(models.Model): 
    _name = "llantas_config.ctt_llantas"
    _description = "Llantas"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sale_id = fields.Many2one(
        "sale.order",
        string="Venta",
        store=True,
        company_dependent=True,
    )

    image = fields.Binary(
        related="marketplace.imagen",
        string="Imagen",
        store=True,
    )

    company_image = fields.Binary(
        related="company_id.logo",
        string="Imagen empresa",
        store=True,
    )

    marketplace = fields.Many2one(
        "llantas_config.marketplaces",
        related="sale_id.marketplace",
        string="Marketplace",
        company_dependent=True,
        store=True,
    )

    @api.depends('sale_id.marketplace.name')
    def _compute_marketplace_id(self):
        for line in self:
            line.marketplace_name = line.sale_id.marketplace.name
    marketplace_name = fields.Char(
        string="Canal de venta",
        compute="_compute_marketplace_id",
        store=True,
    )



    name=fields.Char(
        related="sale_id.name",
        string="Nombre",
        tracking=True,
        store=True,
    )

    comprador_id=fields.Many2one(
        "hr.employee",
        related="sale_id.comprador_id",
        string="Comprador",
        company_dependent=True,
    )


    partner_name=fields.Many2one(
        "res.partner",
        related="sale_id.partner_id",
        string="Cliente",
        store=True,
    )

    proveedor_id=fields.Many2one(
        "res.partner",
        string="Proveedor",
        store=True,
        # compute=compute_proveedor_id,
        # store=True,
    )

    def compute_orden_compra(self):
        for rec in self:
            rec.orden_compra = rec.sale_id._get_purchase_orders().id
    orden_compra=fields.Many2one(
        "purchase.order",
        compute=compute_orden_compra,
        string="Orden de compra",
        # store=True,
    )

    partner_id=fields.Many2one(
        "res.partner",
        related="orden_compra.partner_id",
        string="Proveedor",
    )

    

    def compute_factura_prov(self):
        for rec in self:
            rec.factura_prov = rec.sale_id._get_purchase_orders().invoice_ids
    factura_prov=fields.Many2one(
        "account.move",
        string="Factura proveedor",
        compute=compute_factura_prov
    )


    def open_sale_order(self):
        """Método para abrir la orden de venta asociada."""
        if self.sale_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'res_id': self.sale_id.id,
                'view_mode': 'form',
                'view_id': False,
                'target': 'current',
            }


    def open_orden_compra(self):
        """Método para abrir el formulario de la orden de compra asociada."""
        if self.orden_compra:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.order',
                'res_id': self.orden_compra.id,
                'view_mode': 'form',
                'view_id': False,
                'target': 'current',
            }
            
    num_cliente=fields.Char(
        related="partner_name.usuario_marketplace",
        string="Num. Cliente",
        tracking=True,
    )
    
    factura_cliente = fields.Many2many(
        'account.move',
        string="Factura cliente",
        related="sale_id.invoice_ids",
        options="{'action': 'action_open_invoice'}",
    )

    # Relación inversa para navegar desde la factura a la orden de venta
    factura_cliente_relacion = fields.Many2many(
        'llantas_config.ctt_llantas',
        'ctt_llantas_rel',
        'ctt_llantas_id',
        'factura_cliente_relacion_id',
        'Facturas relacionadas',
    )

    @api.depends('factura_cliente')
    def _compute_factura_cliente_relacion(self):
        for record in self:
            record.factura_cliente_relacion = record
    
    show_si = fields.Boolean(
        compute='_compute_show_si',
        string='Mostrar SI',
        store=False,
    )

    def action_show_related_invoices(self):
        # Obtén las facturas relacionadas con sale_id.invoice_ids
        invoices = self.sale_id.invoice_ids
    
        # Abre la vista tree con las facturas relacionadas
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        action['domain'] = [('id', 'in', invoices.ids)]
        return action
    
    
    # factura_cliente2=fields.Char(
    #     # "account.move",
    #     related="sale_id.invoice_ids"
    #     string="Factura cliente",
    #     # tracking=True
    # )
    
    # status = fields.Many2one(
    #     'llantas_config.status', 
    #     string="Status",
    # )

    status_id = fields.Selection([
        ('01','Pendiente'),
        ('02','Debito en curso'),
        ('03','Traspaso'),
        ('04','Guia pendiente'),
        ('05','Enviado'),
        ('06','Entregado'),
        ('07','Cerrado'),
        ('08','Incidencia'),
        ('09','Devolución'),],
        related="sale_id.ventas_status",
        string="Status",
                            
        store=True                                
    )

    @api.onchange('status_id')
    def _onchange_sale_id(self):
        if self.status_id:

            self.sale_id.write({'ventas_status': self.status_id})
        else:
            self.status_id = False
    
    fecha=fields.Datetime(
        string="Fecha",
        store=True
    )
    
    dias = fields.Integer(string="Días transcurridos", compute='_compute_dias', store=True, readonly=True)
    
    @api.depends('fecha')
    def _compute_dias(self):
        records=env['llantas_config.ctt_llantas'].search([])
        if records:
          for rec in records:
            if rec.fecha:
              fecha_hoy = datetime.datetime.today()
              dias_transcurridos = fecha_hoy - rec.fecha
              # raise UserError(dias_transcurridos.days)
              rec.write({'dias': int(dias_transcurridos.days)})
        
    comentarios=fields.Char(
        string="Comentarios",
        tracking=True
    )

    orden_entrega=fields.One2many(
        "stock.picking",
        "carrier_tracking_ref",
        string="No. Guia",
        related="sale_id.picking_ids",
        # store=True,
    )

    @api.depends('orden_entrega','orden_entrega.carrier_tracking_ref')
    def compute_guias(self):
        for rec in self:
            guias = ""
            for orden in rec.orden_entrega:
                guias += str(orden.carrier_tracking_ref) + ", "
            guias = guias[:-2]
            rec.guias = guias
    guias = fields.Char(
        string="Guías",
        compute=compute_guias,
        # store=True
    )

    @api.depends('orden_entrega','orden_entrega.carrier_tracking_ref')
    def compute_detailed_info(self):
        for rec in self:
            detailed_info = ""
            detailed_info += "<table class='table'>"
            detailed_info += "<tr>"
            detailed_info += "<th>Entrega</th>"
            detailed_info += "<th>Carrier</th>"
            detailed_info += "<th>Guía</th>"
            detailed_info += "<th>Link</th>"
            detailed_info += "<th>Estado</th>"
            detailed_info += "</tr>"
            for orden in rec.orden_entrega:
                detailed_info += "<tr>"
                detailed_info += "<td>"+str(orden.display_name)+"</td>"
                detailed_info += "<td>"+str(orden.carrier.display_name)+"</td>"
                detailed_info += "<td>"+str(orden.carrier_tracking_ref)+"</td>"
                detailed_info += "<td>"+str(orden.link_guia)+"</td>"
                detailed_info += "<td>"+str(orden.state)+"</td>"
            detailed_info += "</tr>"
            detailed_info += "</table>"
                # detailed_info += str(orden.display_name) + "<table><tr><td>Carrier:</td><td>" + str(orden.carrier.display_name) + "</td></tr><tr><td>Rastreo: </td><td>" + str(orden.carrier_tracking_ref) + "</td></tr></table>"
            # detailed_info = detailed_info[:-2]
            rec.detailed_info = detailed_info
    detailed_info = fields.Html(
        string="Información detallada",
        compute=compute_detailed_info,
        # store=True
    )

    link_guia = fields.Char(string="Link guia",related="orden_entrega.link_guia")

    def open_link_guia(self):
        return {
            "type": "ir.actions.act_url",
            "url": self.link_guia,
            "target": "new",
        }
    

    carrier = fields.Many2one(
        "llantas_config.carrier",
        string="Carrier",
        store=True,
        # related="orden_entrega.carrier",
        # store=True
    )

    def compute_no_recoleccion(self):
        for rec in self:
            rec.no_recoleccion = rec.sale_id._get_purchase_orders().picking_ids.no_recoleccion
    no_recoleccion=fields.Char(
        compute=compute_no_recoleccion,
        string="No. Recolección",
    )

    # no_recoleccion=fields.Char(
    #     string="No. Recoleccion", 
    #     related="sale_id.picking_ids.no_recoleccion",
    # )

    # carrier_id=fields.Many2one(
    #     "llantas_config.carrier",
    #     related=""
    #     string="Carrier",
    # )

    link_venta = fields.Char(
        related="sale_id.link_venta",
        string="Link venta",
        store=True,
    )

    def action_open_sale_url(self):
        if self.link_venta:
            return {
                'type': 'ir.actions.act_url',
                'url': self.link_venta,
                'target': 'new',
            }
        else:
            # Puedes manejar el caso en el que no hay URL
            raise UserError('No hay URL disponible.')

    no_venta=fields.Char(
        related="sale_id.folio_venta",
        string="No. Venta",
    )

    comision=fields.Float(
        string="Comisión",
    )

    envio=fields.Float(
        string="Envio",
    )

    company_id=fields.Many2one(
        "res.company",
        related="sale_id.company_id",
        string="Empresa"
    )

    def compute_tdp(self):
        for rec in self:
            rec.tdp = rec.sale_id._get_purchase_orders().partner_ref
    tdp=fields.Char(
        string="Referencia compra (TDP)",
        compute=compute_tdp
    )
    
    @api.model
    def create(self, values):
        if 'sale_id' in values:
            sale_id = self.env['sale.order'].browse(values['sale_id'])
            values['proveedor_id'] = sale_id._get_purchase_orders().partner_id
        return super(ctrl_llantas, self).create(values)
    
    def write(self, values):
        for rec in self:
            if 'sale_id' in values:
                sale_id = rec.env['sale.order'].browse(values['sale_id'])
                values['proveedor_id'] = sale_id._get_purchase_orders().partner_id
            record = super(ctrl_llantas, rec).write(values)
        return self


    productos_orden=fields.Many2one(
        "sale.order.line",
        string="Líneas de la orden",
        related="sale_id.lineas_orden",
        store=True,
    )

    producto=fields.Char(
        related="productos_orden.product_id.name",
        string="Producto",
    )

    archivo_adjunto = fields.Binary(string='Archivo Adjunto', attachment=True)

