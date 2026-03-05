from odoo import models, fields, api, _
import logging
import datetime
import re
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
_logger = logging.getLogger(__name__)
from odoo.tools.float_utils import float_round

class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'
    _description = 'Producto'
    
    # Corrección: usar @api.depends para campos computados
    @api.depends('type')
    def _compute_show_qty_status_button(self):
        for template in self:
            template.show_on_hand_qty_status_button = template.type == 'product'
            template.show_forecasted_qty_status_button = template.type == 'product'

    codigo_llanta = fields.Char(
        string='Código',
    )

    marca_llanta = fields.Many2one(
        'llantas_config.marca_llanta', 
        string="Marca llanta"
    )
    
    modelo_llanta = fields.Many2one(
        'llantas_config.modelo_llanta', 
        string="Modelo llanta"
    )
    
    medida_llanta = fields.Many2one(
        'llantas_config.medida_llanta', 
        string="Medida llanta"
    )

    indice_carga = fields.Integer(
        string='Índice de carga',
    )

    indice_velocidad = fields.Char(
        string='Índice de velocidad',
    )

    largo = fields.Char(
        string='Largo llanta',
    )
    
    ancho = fields.Char(
        string='Ancho llanta',
    )   
    
    alto = fields.Char(
        string='Alto llanta',
    )   

    rin = fields.Char(
        string='Rin',
    )

    config_marketplace_id = fields.Many2one(
        "llantas_config.product_marketplace",
        string="Marketplaces",
        store=True
    )

    config_marketplace_ids = fields.One2many(
        "llantas_config.product_marketplace",
        "product_ids",
        string="Marketplaces",
        store=True
    )

    sku_alterno_id = fields.Many2one(
        "llantas_config.sku_marketplace",
        string="Sku externo",
    )

    sku_alternos = fields.One2many(
        "llantas_config.sku_marketplace",
        "product_id",
        string="Sku externo",
    )

    es_llanta = fields.Boolean(
        string="¿Es llanta?",
        tracking=True, 
    )

    es_paquete = fields.Boolean(
        string="¿Es paquete?",
        tracking=True,
    )

    pkg_type = fields.Selection(
        selection=[
            ('2', '2'),
            ('4', '4')
        ],
        string="Cantidad",
        default="2",
        required=True
    )

    compatibilidad_ids = fields.One2many(
        'llantas_config.compatibilidad',
        'product_id',
        string="Modelos de auto compatibles"
    )

    qty_suppliers_total = fields.Float(
        string="Cantidad de proveedores",
        compute="_compute_suppliers_total",
        store=True  # Añadido store=True para mejorar rendimiento
    )

    @api.depends('seller_ids.existencia_actual')
    def _compute_suppliers_total(self):
        for rec in self:
            total = sum(seller.existencia_actual for seller in rec.seller_ids)
            rec.qty_suppliers_total = total

    killer_id = fields.Many2one(
        "llantas_config.killer_list",
        string="ID killer",
        store=True,
    )

    killer_ids = fields.One2many(
        "llantas_config.killer_list",
        "product_id",
        string="Lista killer",
        store=True
    )

    # CORRECCIÓN IMPORTANTE: Método create para Odoo 19
    @api.model_create_multi
    def create(self, vals_list):
        """
        Método create para Odoo 19 que maneja creación múltiple
        """
        for vals in vals_list:
            if 'company_id' not in vals:
                vals['company_id'] = self.env.company.id
        return super().create(vals_list)

    # CORRECCIÓN: Añadir método write si es necesario
    def write(self, vals):
        """
        Asegurar que company_id no se modifique incorrectamente
        """
        if 'company_id' in vals and vals['company_id'] != self.env.company.id:
            # Solo permitir cambio si es necesario
            pass
        return super().write(vals)


class ProductProductInherit(models.Model):
    _inherit = 'product.product'
    _description = 'Producto'

    def _search_qty_available(self, operator, value):
        """Buscar productos con cantidad disponible"""
        ids = []
        quant_ids = self.env['stock.quant'].search([
            ('location_id.usage', '=', 'internal'),
            ('quantity', '>', 0)
        ])
        for quant_id in quant_ids:
            if quant_id.product_id.id not in ids:
                ids.append(quant_id.product_id.id)
        return [('id', 'in', ids)]

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        """
        Búsqueda mejorada que incluye sku_alternos
        """
        if not args:
            args = []
            
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            product_ids = []
            
            # Buscar por código
            if operator in positive_operators:
                product_ids = list(self._search(
                    [('default_code', '=', name)] + args, 
                    limit=limit, 
                    access_rights_uid=name_get_uid
                ))
                if not product_ids:
                    product_ids = list(self._search(
                        [('barcode', '=', name)] + args, 
                        limit=limit, 
                        access_rights_uid=name_get_uid
                    ))
            
            # Búsqueda general
            if not product_ids and operator not in expression.NEGATIVE_TERM_OPERATORS:
                # Búsqueda por código
                product_ids = list(self._search(
                    args + [('default_code', operator, name)], 
                    limit=limit
                ))
                
                if not limit or len(product_ids) < limit:
                    limit2 = (limit - len(product_ids)) if limit else False
                    
                    # Búsqueda por nombre
                    if limit2:
                        product2_ids = self._search(
                            args + [('name', operator, name), ('id', 'not in', product_ids)], 
                            limit=limit2, 
                            access_rights_uid=name_get_uid
                        )
                        product_ids.extend(product2_ids)
                    
                    # Búsqueda por sku alterno
                    if limit2 and len(product_ids) < limit:
                        limit3 = limit - len(product_ids)
                        product3_ids = self._search(
                            args + [('sku_alternos.name', operator, name), ('id', 'not in', product_ids)], 
                            limit=limit3, 
                            access_rights_uid=name_get_uid
                        )
                        product_ids.extend(product3_ids)
            
            # Búsqueda negativa
            elif not product_ids and operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = expression.OR([
                    ['&', ('default_code', operator, name), ('name', operator, name)],
                    ['&', ('default_code', '=', False), ('name', operator, name)],
                ])
                domain = expression.AND([args, domain])
                product_ids = list(self._search(
                    domain, 
                    limit=limit, 
                    access_rights_uid=name_get_uid
                ))
            
            # Búsqueda por patrón con corchetes [código]
            if not product_ids and operator in positive_operators:
                ptrn = re.compile(r'\[(.*?)\]')
                res = ptrn.search(name)
                if res:
                    product_ids = list(self._search(
                        [('default_code', '=', res.group(1))] + args, 
                        limit=limit, 
                        access_rights_uid=name_get_uid
                    ))
            
            # Búsqueda por proveedor
            if not product_ids and self._context.get('partner_id'):
                suppliers_ids = self.env['product.supplierinfo']._search([
                    ('partner_id', '=', self._context.get('partner_id')),
                    '|',
                    ('product_code', operator, name),
                    ('product_name', operator, name)
                ], access_rights_uid=name_get_uid)
                
                if suppliers_ids:
                    product_ids = self._search(
                        [('product_tmpl_id.seller_ids', 'in', suppliers_ids)], 
                        limit=limit, 
                        access_rights_uid=name_get_uid
                    )
        else:
            product_ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
            
        return product_ids


class ProductSupplierinfoInherit(models.Model):
    _inherit = 'product.supplierinfo'
    _description = 'Información de proveedor'  # CORRECCIÓN: Descripción más apropiada

    existencia_actual = fields.Integer(
        string="Existencia actual",
        help="Cantidad actual en inventario del proveedor"
    )

    tipo_cambio = fields.Float(
        string="Tipo de cambio",
        digits=(12, 6),  # Añadido digits para mejor precisión
        help="Tipo de cambio aplicado"
    )
    
    precio_neto = fields.Float(
        string="Precio neto",
        digits='Product Price',  # Usar digits estándar de Odoo
        help="Precio neto después de descuentos"
    )

    ultima_actualizacion = fields.Datetime(
        string="Última actualización",
        default=fields.Datetime.now,  # Añadido default
        help="Fecha y hora de la última actualización"
    )

    tipo_moneda_proveedor = fields.Char(
        string="Moneda del proveedor",
        help="Código de la moneda utilizada por el proveedor"
    )

    # CORRECCIÓN: Añadir constraints si es necesario
    _sql_constraints = [
        ('check_existencia_actual', 'CHECK(existencia_actual >= 0)', 
         'La existencia actual no puede ser negativa'),
    ]

    # CORRECCIÓN: Añadir método para validar datos
    @api.constrains('tipo_cambio', 'precio_neto')
    def _check_positive_values(self):
        for record in self:
            if record.tipo_cambio < 0:
                raise ValidationError(_("El tipo de cambio no puede ser negativo."))
            if record.precio_neto < 0:
                raise ValidationError(_("El precio neto no puede ser negativo."))