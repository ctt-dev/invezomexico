from odoo import models, fields, api, _
import logging
import datetime
import re
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
_logger = logging.getLogger(__name__)

class product_template_inherit(models.Model):
    _inherit = 'product.template'
    _description='Producto'

    codigo_llanta = fields.Char(
    string='Codigo',
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
    string='Indice de carga',
    )

    indice_velocidad = fields.Char(
    string='Indice de velocidad',
    )

    largo = fields.Float(
    string='Largo llanta',
    )
    
    ancho = fields.Float(
    string='Ancho llanta',
    )	
    
    alto = fields.Float(
    string='Alto llanta',
    )	
    

    config_marketplace_id=fields.Many2one(
        "llantas_config.product_marketplace",
        string="Maketplaces",
        store=True

    )

    config_marketplace_ids=fields.One2many(
        "llantas_config.product_marketplace",
        "product_ids",
        string="Maketplaces",
        store=True

    )

    sku_alterno_id=fields.Many2one(
        "llantas_config.sku_marketplace",
        string="Sku externo",
    )

    sku_alternos=fields.One2many(
        "llantas_config.sku_marketplace",
        "product_id",
        string="Sku externo",
    )

    

class product_product_inherit(models.Model):
    _inherit = 'product.product'
    _description='Producto'

    # @api.model
    # def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
    #     domain = args or []
    #     domain += [('sku_alternos.name', operator, name)]
    #     records = self.search(domain, limit=limit)
    #     return records.name_get()

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if not args:
            args = []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            product_ids = []
            if operator in positive_operators:
                product_ids = list(self._search([('default_code', '=', name)] + args, limit=limit, access_rights_uid=name_get_uid))
                if not product_ids:
                    product_ids = list(self._search([('barcode', '=', name)] + args, limit=limit, access_rights_uid=name_get_uid))
            if not product_ids and operator not in expression.NEGATIVE_TERM_OPERATORS:
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching products, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                product_ids = list(self._search(args + [('default_code', operator, name)], limit=limit))
                if not limit or len(product_ids) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    limit2 = (limit - len(product_ids)) if limit else False
                    product2_ids = self._search(args + [('name', operator, name), ('id', 'not in', product_ids)], limit=limit2, access_rights_uid=name_get_uid)
                    product3_ids = self._search(args + [('sku_alternos.name', operator, name), ('id', 'not in', product_ids)], limit=limit2, access_rights_uid=name_get_uid)
                    product_ids.extend(product2_ids)
                    product_ids.extend(product3_ids)
            elif not product_ids and operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = expression.OR([
                    ['&', ('default_code', operator, name), ('name', operator, name)],
                    ['&', ('default_code', '=', False), ('name', operator, name)],
                ])
                domain = expression.AND([args, domain])
                product_ids = list(self._search(domain, limit=limit, access_rights_uid=name_get_uid))
            if not product_ids and operator in positive_operators:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    product_ids = list(self._search([('default_code', '=', res.group(2))] + args, limit=limit, access_rights_uid=name_get_uid))
            # still no results, partner in context: search on supplier info as last hope to find something
            if not product_ids and self._context.get('partner_id'):
                suppliers_ids = self.env['product.supplierinfo']._search([
                    ('partner_id', '=', self._context.get('partner_id')),
                    '|',
                    ('product_code', operator, name),
                    ('product_name', operator, name)], access_rights_uid=name_get_uid)
                if suppliers_ids:
                    product_ids = self._search([('product_tmpl_id.seller_ids', 'in', suppliers_ids)], limit=limit, access_rights_uid=name_get_uid)
        else:
            product_ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return product_ids

class product_product_inherit(models.Model):
    _inherit = 'product.supplierinfo'
    _description='Producto'

    existencia_actual=fields.Integer(
        string="Existencia actual",
    )

    tipo_cambio=fields.Float(
        string="Tipo cambio",
    )
    
    precio_neto=fields.Float(
        string="Precio neto",
    )

    ultima_actualizacion=fields.Datetime(
        string="Ultima actualizacion",
    )

    tipo_moneda_proveedor=fields.Char(
        string="Tipo moneda proveedor",
    )



    