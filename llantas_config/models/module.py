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
        store=True
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
    )
    
    comprador_id = fields.Many2one(
        "hr.employee",
        related="sale_id.comprador_id",
        string="Comprador",
        company_dependent=True,
        store=True,
    )
    
    comprador_name = fields.Char(
        string="Nombre del Comprador",
        compute="_compute_comprador_name",
        store=True,
    )
    @api.depends('sale_id','sale_id.comprador_id','sale_id.comprador_id.name')
    def _compute_comprador_name(self):
        for rec in self:
            rec.comprador_name = rec.sale_id.comprador_id.name
   
    partner_name=fields.Many2one(
        "res.partner",
        related="sale_id.partner_id",
        string="Cliente",
    )

    proveedor_id=fields.Many2one(
        "res.partner",
        string="Proveedor",
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
    )

    partner_id=fields.Many2one(
        "res.partner",
        related="orden_compra.partner_id",
        string="Proveedor",
    )

    

    def compute_factura_prov(self):
        for rec in self:
            purchase_orders = rec.sale_id._get_purchase_orders()
            if purchase_orders and purchase_orders.invoice_ids:
                rec.factura_prov = purchase_orders.invoice_ids[0]
            else:
                rec.factura_prov = False

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
            
    # num_cliente=fields.Char(
    #     related="partner_name.usuario_marketplace",
    #     string="Num. Cliente",
    # )
    
    factura_cliente = fields.Many2many(
        'account.move',
        string="Factura cliente",
        related="sale_id.invoice_ids",
        options="{'action': 'action_open_invoice'}",
        required=False,  # Permitir que el campo sea nulo
    )

    factura_cliente_count = fields.Integer(
        string="Número de facturas de cliente",
        compute='_compute_factura_cliente_count',
        store=True
    )

    @api.depends('factura_cliente')
    def _compute_factura_cliente_count(self):
        for record in self:
            record.factura_cliente_count = len(record.factura_cliente)

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

    @api.depends('sale_id','sale_id.ventas_status')
    def compute_status_id(self):
        for rec in self:
            # raise UserError("compute_status_id")
            rec.status_id = rec.sale_id.ventas_status
            _logger.warning("compute_status_id --> " + str(rec.status_id))
    status_id = fields.Selection(
        [
            ('01','Pendiente'),
            ('02','Debito en curso'),
            ('03','Traspaso'),
            ('04','Guia pendiente'),
            ('05','Enviado'),
            ('06','Entregado'),
            ('07','Cerrado'),
            ('08','Incidencia'),
            ('09','Devolución'),
        ],
        compute=compute_status_id,
        inverse=compute_status_id,
        string="Status",
        tracking=True,
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
    )
    
    dias = fields.Integer(string="Días transcurridos", compute='_compute_dias', store=True, readonly=True)
    
    @api.depends('fecha')
    def _compute_dias(self):
        records=self.env['llantas_config.ctt_llantas'].search([])
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
        string="Salidas",
        related="sale_id.picking_ids",
        # store=True,
    )

    orden_recepcion=fields.Many2many(
        "stock.picking",
        "name",
        string="Entradas",
        related="orden_compra.picking_ids",
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

    @api.depends('orden_entrega', 'orden_entrega.carrier_tracking_ref','sale_id')
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
                detailed_info += "<td>" + str(orden.display_name) + "</td>"
                if isinstance(orden.carrier, models.Model):  # Verifica si orden.carrier es un registro de modelo
                    detailed_info += "<td>" + rec.sale_id.carrier_id.name + "</td>"
                else:
                    detailed_info += "<td></td>"  # O alguna indicación de que no hay ningún valor
                detailed_info += "<td>" + str(orden.carrier_tracking_ref) + "</td>"
                detailed_info += "<td>" + str(orden.link_guia) + "</td>"
                detailed_info += "<td>" + str(orden.state) + "</td>"
                detailed_info += "</tr>"
    
            detailed_info += "</table>"
            rec.detailed_info = detailed_info
    
    detailed_info = fields.Html(
        string="Información detallada",
        compute=compute_detailed_info,
    )
    
    carrier = fields.Many2one(
        "llantas_config.carrier",
        string="Carrier",
        related="sale_id.carrier_id",
    )
    
    link_guia = fields.Char(string="Link guia",related="orden_entrega.link_guia")

    def open_link_guia(self):
        return {
            "type": "ir.actions.act_url",
            "url": self.link_guia,
            "target": "new",
        }
    def compute_no_recoleccion(self):
        for rec in self:
            tdp = ""
            try:
                no_recoleccion = rec.no_recoleccion
                if no_recoleccion:
                    tdp = ", ".join(str(picking_id.no_recoleccion) for picking_id in rec.sale_id._get_purchase_orders().picking_ids if picking_id.no_recoleccion)
            except Exception as e:
                tdp = ""
                _logger.error("Error al calcular no_recoleccion: %s", str(e))
            rec.tdp = tdp
    no_recoleccion=fields.Char(
        compute=compute_no_recoleccion,
        string="No. Recolección",
    )
    no_recoleccion2=fields.Char(
        string="No. Recoleccion", 
        related="sale_id.picking_ids.no_recoleccion",
    )

    # carrier_id=fields.Many2one(
    #     "llantas_config.carrier",
    #     related=""
    #     string="Carrier",
    # )

    link_venta = fields.Char(
        related="sale_id.link_venta",
        string="Link venta",
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
            tdp = ""
            for purchase_id in rec.sale_id._get_purchase_orders():
                if purchase_id.partner_ref:
                    tdp += str(purchase_id.partner_ref) + ", "
            rec.tdp = tdp[:-2]
    tdp=fields.Char(
        string="Referencia compra (TDP)",
        compute=compute_tdp
    )
    
    @api.model
    def create(self, values):
        if 'sale_id' in values:
            sale_id = self.env['sale.order'].browse(values['sale_id'])
            values['proveedor_id'] = sale_id._get_purchase_orders().partner_id.id
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
    )

    producto=fields.Char(
        related="productos_orden.product_id.name",
        string="Producto",
    )

    archivo_adjunto = fields.Binary(string='Archivo Adjunto', attachment=True)



    def compute_sale_id_attachment_ids(self):
        for rec in self:
            attachment_ids = rec.env['ir.attachment'].search([('res_model', '=', 'sale.order'), ('res_id', '=', rec.sale_id.id)])
            if attachment_ids:
                rec.sale_id_attachment_ids = attachment_ids
            else:
                rec.sale_id_attachment_ids = False
    sale_id_attachment_ids = fields.Many2many(
        'ir.attachment',
        string="Orden de venta - Adjuntos",
        compute=compute_sale_id_attachment_ids
    )

    def compute_orden_compra_attachment_ids(self):
        for rec in self:
            attachment_ids = rec.env['ir.attachment'].search([('res_model','=','purchase.order'),('res_id','=',rec.orden_compra.id)])
            if attachment_ids:
                rec.orden_compra_attachment_ids = attachment_ids
            else:
                rec.orden_compra_attachment_ids = False
    orden_compra_attachment_ids = fields.Many2many(
        'ir.attachment',
        string="Orden de compra - Adjuntos",
        compute=compute_orden_compra_attachment_ids
    )

    def compute_factura_prov_attachment_ids(self):
        for rec in self:
            attachment_ids = rec.env['ir.attachment'].search([('res_model','=','account.move'),('res_id','=',rec.factura_prov.id)])
            if attachment_ids:
                rec.factura_prov_attachment_ids = attachment_ids
            else:
                rec.factura_prov_attachment_ids = False
                
    factura_prov_attachment_ids = fields.Many2many(
        'ir.attachment',
        string="Factura de proveedor - Adjuntos",
        compute=compute_factura_prov_attachment_ids
    )


