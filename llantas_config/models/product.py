from odoo import models, fields, api, _
import logging
import datetime
import re
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
_logger = logging.getLogger(__name__)
from odoo.tools.float_utils import float_round

class product_template_inherit(models.Model):
    _inherit = 'product.template'
    _description='Producto'
    
    def _compute_show_qty_status_button(self):
        for template in self:
            template.show_on_hand_qty_status_button = template.type == 'product'
            template.show_forecasted_qty_status_button = template.type == 'product'

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

    
    es_llanta=fields.Boolean(
        string="Es llanta?",
        tracking=True, 
    )

    es_paquete=fields.Boolean(
        string="Es paquete?",
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
        string = "Modelos de auto compatibles"
    )


    qty_suppliers_total = fields.Float(
        string="Cantidad de proveedores",
        compute="_compute_suppliers_total"
    )

    def _compute_suppliers_total(self):
        for rec in self:
            total = sum(seller.existencia_actual for seller in rec.seller_ids)
            rec.qty_suppliers_total = total


    killer_id=fields.Many2one(
        "llantas_config.killer_list",
        string="id killer",
        store=True,
        
    )

    # killer_ids = fields.One2many(
    #     "llantas_config.killer_list",
    #     "marketplace_id",
    #     string="Listado de Killers",

    # )


    @api.model
    def create(self, values):
        values['company_id'] = self.env.company.id
        return super(ProductTemplate, self).create(values)
    
    is_killer=fields.Boolean(
        string="Es killer?",
        tracking=True,
    )

    killer_date=fields.Datetime(
        string="Fecha final killer",
        # related="killer_id.final_date",
        tracking=True,
    )

    killer_initial_date= fields.Datetime(
        string="Fecha inicial killer",
        tracking=True,
        # related="killer_id.initial_date",
        store=True,
    )

    killer_price=fields.Float(
        string="Precio killer",
        tracking=True,
    )

     
    
class product_product_inherit(models.Model):
    _inherit = 'product.product'
    _description='Producto'

    def _search_qty_available(self, operator, value):
        ids = []
        quant_ids = self.env['stock.quant'].search([('location_id.usage','=','internal')])
        for quant_id in quant_ids:
            if quant_id.quantity > 0:
                if quant_id.product_id.id not in ids:
                    ids.append(quant_id.product_id.id)
        return [('id', 'in', ids)]
    
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

    # def _compute_quantities_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
    #     for rec in self:
    #         res = super(product_product_inherit, rec)._compute_quantities_dict(lot_id, owner_id, package_id, from_date=False, to_date=False)
    #     return self

    # def _compute_quantities_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
    #     _logger.warning("_compute_quantities_dict " + str(self.ids))
    #     domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations()
    #     domain_quant = [('product_id', 'in', self.ids)] + domain_quant_loc
    #     dates_in_the_past = False
    #     # only to_date as to_date will correspond to qty_available
    #     to_date = fields.Datetime.to_datetime(to_date)
    #     if to_date and to_date < fields.Datetime.now():
    #         dates_in_the_past = True

    #     domain_move_in = [('product_id', 'in', self.ids)] + domain_move_in_loc
    #     domain_move_out = [('product_id', 'in', self.ids)] + domain_move_out_loc
    #     if lot_id is not None:
    #         domain_quant += [('lot_id', '=', lot_id)]
    #     if owner_id is not None:
    #         domain_quant += [('owner_id', '=', owner_id)]
    #         domain_move_in += [('restrict_partner_id', '=', owner_id)]
    #         domain_move_out += [('restrict_partner_id', '=', owner_id)]
    #     if package_id is not None:
    #         domain_quant += [('package_id', '=', package_id)]
    #     if dates_in_the_past:
    #         domain_move_in_done = list(domain_move_in)
    #         domain_move_out_done = list(domain_move_out)
    #     if from_date:
    #         date_date_expected_domain_from = [('date', '>=', from_date)]
    #         domain_move_in += date_date_expected_domain_from
    #         domain_move_out += date_date_expected_domain_from
    #     if to_date:
    #         date_date_expected_domain_to = [('date', '<=', to_date)]
    #         domain_move_in += date_date_expected_domain_to
    #         domain_move_out += date_date_expected_domain_to

    #     Move = self.env['stock.move'].with_context(active_test=False)
    #     Quant = self.env['stock.quant'].with_context(active_test=False)
    #     domain_move_in_todo = [('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_in
    #     domain_move_out_todo = [('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_out
    #     moves_in_res = dict((item['product_id'][0], item['product_qty']) for item in Move._read_group(domain_move_in_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
    #     moves_out_res = dict((item['product_id'][0], item['product_qty']) for item in Move._read_group(domain_move_out_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
    #     quants_res = dict((item['product_id'][0], (item['quantity'], item['reserved_quantity'])) for item in Quant._read_group(domain_quant, ['product_id', 'quantity', 'reserved_quantity'], ['product_id'], orderby='id'))
    #     if dates_in_the_past:
    #         # Calculate the moves that were done before now to calculate back in time (as most questions will be recent ones)
    #         domain_move_in_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_in_done
    #         domain_move_out_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_out_done
    #         moves_in_res_past = dict((item['product_id'][0], item['product_qty']) for item in Move._read_group(domain_move_in_done, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
    #         moves_out_res_past = dict((item['product_id'][0], item['product_qty']) for item in Move._read_group(domain_move_out_done, ['product_id', 'product_qty'], ['product_id'], orderby='id'))

    #     res = dict()
    #     for product in self.with_context(prefetch_fields=False):
    #         origin_product_id = product._origin.id
    #         product_id = product.id
    #         if not origin_product_id:
    #             res[product_id] = dict.fromkeys(
    #                 ['qty_available', 'free_qty', 'incoming_qty', 'outgoing_qty', 'virtual_available'],
    #                 0.0,
    #             )
    #             continue
    #         rounding = product.uom_id.rounding
    #         res[product_id] = {}
    #         if dates_in_the_past:
    #             qty_available = quants_res.get(origin_product_id, [0.0])[0] - moves_in_res_past.get(origin_product_id, 0.0) + moves_out_res_past.get(origin_product_id, 0.0)
    #         else:
    #             qty_available = quants_res.get(origin_product_id, [0.0])[0]
    #         reserved_quantity = quants_res.get(origin_product_id, [False, 0.0])[1]
    #         res[product_id]['qty_available'] = float_round(qty_available, precision_rounding=rounding)
    #         res[product_id]['free_qty'] = float_round(qty_available - reserved_quantity, precision_rounding=rounding)
    #         res[product_id]['incoming_qty'] = float_round(moves_in_res.get(origin_product_id, 0.0), precision_rounding=rounding)
    #         res[product_id]['outgoing_qty'] = float_round(moves_out_res.get(origin_product_id, 0.0), precision_rounding=rounding)
    #         res[product_id]['virtual_available'] = float_round(
    #             qty_available + res[product_id]['incoming_qty'] - res[product_id]['outgoing_qty'],
    #             precision_rounding=rounding)

    #     return res

    
    
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



    