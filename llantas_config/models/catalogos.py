from odoo import models, fields, api, _
import logging
import tempfile
import json
import base64
import pandas as pd
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from collections import defaultdict
_logger = logging.getLogger(__name__)
import datetime
import urllib.request 
import json  
from odoo import _

class marca_llanta(models.Model): 
    _name = 'llantas_config.marca_llanta'
    _description = 'Catalogo de marca de llantas'
    _order = 'id desc'
    
    name = fields.Char(string="Nombre",required=False)
    color = fields.Integer(string="Color",required=False)

class modelo_llanta(models.Model):
    _name = 'llantas_config.modelo_llanta'
    _description = 'Catalogo de modelo de llantas'
    _order = 'id desc'
    
    name = fields.Char(string="Nombre",required=False)
    color = fields.Integer(string="Color",required=False)

class medida_llanta(models.Model):
    _name = 'llantas_config.medida_llanta'
    _description = 'Catalogo de medida de llantas'
    _order = 'id desc'

    name = fields.Char(string="Nombre",required=False)
    color = fields.Integer(string="Color",required=False)

# class status(models.Model):
#     _name = 'llantas_config.status'
#     _description = 'Status'
#     _order = 'id desc'
    
#     name = fields.Char(
#         string="Nombre",
#         required=True,
#         tracking=True,
#     )
    
#     color = fields.Integer(
#         string="Color",
#         tracking=True,
#     )
#     description=fields.Char(
#         string="Descripción",
#         tracking=True,
#     )
    
class almacen(models.Model):
    _name = 'llantas_config.almacen'
    _description = 'Catalogo de almacenes'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nombre",required=False)
    proveedor=fields.Many2one(
        "res.partner",
        string="Proveedor",
    )
    color = fields.Integer(string="Color",required=False)

class marketplaces(models.Model):
    _name = 'llantas_config.marketplaces'
    _description = 'Catalogo de marketplaces'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def name_get(self):
        res = super(marketplaces, self).name_get()
        data = []
        for e in self:
            display_value = ''
            display_value += str(e.name)
            display_value += ' ('
            display_value += str(e.company_id.name) or ""
            display_value += ')'
            data.append((e.id, display_value))
        return data

    name = fields.Char(
        string="Nombre",
        store=True
    )

    # display_name=fields.Char(
    #     related="name",
    #     string="display_name")
    
    url= fields.Char(
        string="Url marketplace",
    )

    mostrar_comision=fields.Boolean(
        string="Mostrar comisión?",
        default="1",
    )
    
    mostrar_envio=fields.Boolean(
        string="Mostrar envio?",
        default="1",
    )

    category_id=fields.Many2one(
        "res.partner.category",
        string="Categoria contacto",
        
    )

    diarios_id=fields.Many2one(
        "account.journal",
        string="Diario de facturación",
    )
    
    color = fields.Integer(
        string="Color",
    )

    company_id=fields.Many2one(
        "res.company",
        string="Empresa",
    )

    imagen=fields.Binary(
        string="Imagen",
        store=True,
    )

    @api.model
    def create(self, values):
        values['company_id'] = self.env.company.id
        return super(marketplaces, self).create(values)
    
    # def process_link(self):
    #     url = urllib.request.urlopen(self.url) 
    #     data = json.loads(url.read().decode()) 
    #     for x in data["objects"]["ResponseRow"]:
    #         self.env['llantas_config.ctt_tiredirect_cargar'].create({
    #             'description_description': x["Descripcion_Description"],
    #             'clave_parte': x["Clave_Parte"],
    #             'moneda_currency': x["Moneda_Currency"],
    #             'TC': x["TC"],
    #             'ES': x["ES"],
    #             'FS': x["FS"]
    #         })
    #     return {
    #         'name': 'Cargar existencias',
    #         'view_type': 'tree',
    #         'view_mode': 'tree',
    #         'view_id': self.env.ref('llantas_config.view_tiredirect_tree_cargar').id,
    #         'res_model': 'llantas_config.ctt_tiredirect_cargar',
    #         'type': 'ir.actions.act_window',
    #         'target': 'new',
    #     }


class proveedores_link_wizard(models.TransientModel):
    _name = 'llantas_config.proveedores_links_wizard'
    _description = 'Links proveedores'

    proveedores_links_id=fields.Many2one(
        "llantas_config.proveedores_links",
        string="Proveedor",
    )

    limite=fields.Integer(
        string="Limite"
    )
    
    def action_button_procesar(self):
        self.proveedores_links_id.procesar(limite=self.limite)

        # if self.proveedores_links_id.name == 'Tire Direct':
        #     # raise UserError(str(self.proveedores_links_id.name))
        #     self.proveedores_links_id.procesar_tiredirect()
        # else:
        #     # raise UserError(str(self.proveedores_links_id.name)+"123")
        #     self.proveedores_links_id.procesar()

class proveedores_link(models.Model):
    _name = 'llantas_config.proveedores_links'
    _description = 'Links proveedores'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Nombre",
    )

    proveedor_id=fields.Many2one(
        "res.partner",
        string="Proveedor relacionado",
    )
    
    url= fields.Char(
        string="Url proveedor",
    )
    
    color = fields.Integer(
        string="Color",
    )
    
    company_id=fields.Many2one(
        "res.company",
        string="Empresa",
    )
    

    def action_open_modal(self):
        return {
            'name': 'Importar existencia de proveedores',
            'type': 'ir.actions.act_window',
            'res_model': 'llantas_config.proveedores_links_wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('llantas_config.view_wizard_existencias_proveedor_form').id,
            'target': 'new',
        }

    def process_link(self):
        url = urllib.request.urlopen(self.url) 
        data = json.loads(url.read().decode()) 
    
        for x in data["objects"]["ResponseRow"]:
            try:
                FS = float(x["FS"])
            except:
                FS = 0
            try:
                TC = float(x["TC"])
            except:
                TC = 0
    
            if x["Moneda_Currency"] == 'MXN':
                costo = FS
            else:
                costo = FS * TC
    
            existing_record = self.env['llantas_config.ctt_prov'].search([('sku', '=', x["Clave_Parte"])], limit=1)
            if existing_record:
                existing_record.write({
                    'existencia': x["Existencia_Stock"],
                    'costo_sin_iva': costo,
                })
            else:
                self.env['llantas_config.ctt_prov'].create({
                    'producto': x["Descripcion_Description"],
                    'sku': x["Clave_Parte"],
                    'tipo_moneda': 'MXN',
                    'tipo_cambio': TC,
                    'aplicacion': x["Tipo_Type"],
                    'marca': x["Marca_Brand"],
                    'modelo': x["Modelo_Pattern"],
                    'costo_sin_iva': costo,
                    'existencia': x["Existencia_Stock"],
                    'nombre_proveedor': 'Tire Direct',
                })
    
        return {            
           'type': 'ir.actions.client',
           'tag': 'display_notification',            
           'params': {
               'type': 'success',                
               'sticky': False,
               'message': ("Se descargaron las existencias correctamente."),            
            }        
        }



    def procesar(self, limite):
        count_actualizados = 0
        count_agregados = 0
        count_sin_encontrar = 0
        sku_proveedor_procesados = set()
        moneda = self.env['res.currency'].search([('name', '=', 'MXN')])
        moves = self.env['llantas_config.ctt_prov'].search([('nombre_proveedor', '=', self.name), ('procesado', '=', False)], limit=limite)
        partner = self.env['res.partner'].search([('name', '=', self.proveedor_id.name)], limit=1)
        proveedor = partner.id if partner else False
        fecha_actual = datetime.datetime.now()
        
        existencias_por_sku_proveedor = defaultdict(float)
        for move in moves:
            lines = self.env['product.template'].search([
                '|',
                ('default_code', '=', move.sku),
                ('sku_alternos.name', 'in', [move.sku])
            ])
            if lines:
                for lin in lines:
                    if lin.es_paquete or not move.sku_interno:
                        continue
        
        for mov in moves:
            existencias_por_sku_proveedor[(mov.sku, proveedor)] += mov.existencia
        
        for (sku, proveedor), existencia_total in existencias_por_sku_proveedor.items():
            lines = self.env['product.template'].search([
                '|',
                ('default_code', '=', sku),
                ('sku_alternos.name', 'in', [sku])
            ])
            if lines:
                for line in lines:
                    if line.es_paquete:
                        continue
    
                    sku_proveedor = (line.id, proveedor)
                    if sku_proveedor not in sku_proveedor_procesados:
                        sku_moves = self.env['llantas_config.ctt_prov'].search([
                            ('sku', '=', sku),
                            ('nombre_proveedor', '=', self.name)
                        ])
    
                        tipo_cambio = 0
                        if sku_moves:
                            costo_mas_bajo = min(sku_moves.mapped('costo_sin_iva'))
                            filtered_moves = sku_moves.filtered(lambda x: x.costo_sin_iva == costo_mas_bajo)
                            tipo_cambio = filtered_moves[0].tipo_cambio if filtered_moves else 0
                        else:
                            costo_mas_bajo = 0.0
    
                        supplier_info = self.env['product.supplierinfo'].search([
                            ('product_tmpl_id', '=', line.id),
                            ('partner_id', '=', proveedor)
                        ], limit=1)
    
                        if supplier_info:
                            if supplier_info.price != costo_mas_bajo:
                                query = """
                                    UPDATE product_supplierinfo 
                                    SET 
                                        currency_id=%s,
                                        price=%s,
                                        ultima_actualizacion=%s,
                                        tipo_cambio=%s,
                                        precio_neto=%s,
                                        tipo_moneda_proveedor='MXN',
                                        product_code=%s,
                                        existencia_actual=%s
                                    WHERE id=%s
                                """
                                values = (
                                    moneda.id,
                                    costo_mas_bajo,
                                    fecha_actual,
                                    tipo_cambio,
                                    costo_mas_bajo,
                                    sku,
                                    existencia_total,
                                    supplier_info.id
                                )
                                self.env.cr.execute(query, values)
                                count_actualizados += 1
                                # self.env['llantas_config.ctt_prov'].search([
                                #     ('sku', '=', sku),
                                #     ('nombre_proveedor', '=', self.name)
                                # ])
                            else:
                                query = """
                                    UPDATE product_supplierinfo 
                                    SET 
                                        existencia_actual=%s,
                                        ultima_actualizacion=%s
                                    WHERE id=%s
                                """
                                values = (
                                    existencia_total,
                                    fecha_actual,
                                    supplier_info.id
                                )
                                self.env.cr.execute(query, values)
                                count_actualizados += 1
                                # self.env['llantas_config.ctt_prov'].search([
                                #     ('sku', '=', sku),
                                #     ('nombre_proveedor', '=', self.name)
                                # ])
                        else:
                            if existencia_total == 0:
                                continue
                            query = """
                                INSERT INTO product_supplierinfo (partner_id, product_tmpl_id, currency_id, price, ultima_actualizacion,
                                                                  tipo_cambio, precio_neto, tipo_moneda_proveedor, product_code, existencia_actual, delay, min_qty)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """
                            values = (
                                proveedor,
                                line.id,
                                moneda.id,
                                costo_mas_bajo,
                                fecha_actual,
                                tipo_cambio,
                                costo_mas_bajo,
                                'MXN',
                                sku,
                                existencia_total,
                                7,
                                1
                            )
                            self.env.cr.execute(query, values)
                            count_agregados += 1
                            # self.env['llantas_config.ctt_prov'].search([
                            #     ('sku', '=', sku),
                            #     ('nombre_proveedor', '=', self.name)
                            # ])
                        sku_proveedor_procesados.add(sku_proveedor)
            else:
                count_sin_encontrar += 1
                mov.unlink()
        
        # Verificar si quedan movimientos sin procesar
        movimientos_restantes = self.env['llantas_config.ctt_prov'].search([('nombre_proveedor', '=', self.name), ('procesado', '=', False)])
        if not movimientos_restantes:
            raise UserError("Todos los productos han sido procesados. No hay productos pendientes por procesar.")
            # return {
            #     'type': 'ir.actions.client',
            #     'tag': 'display_notification',
            #     'params': {
            #         'type': 'warning',
            #         'sticky': True,
            #         'message': "Todos los productos han sido procesados. No hay productos pendientes por procesar.",
            #     }
            # }
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'sticky': False,
                'message': f"Se actualizaron {count_actualizados} registros y se agregaron {count_agregados} nuevos registros correctamente. No se encontraron {count_sin_encontrar}.",
            }
        }
   
    # def procesar_tiredirect(self):
    #     moves=self.env['llantas_config.ctt_prov'].search(['nombre_proveedor','=','Tire Direct'])
    #     partner=self.env['res.partner'].search([('name','=','TIRE DIRECT S.A. DE C.V.')], limit=1)
    #     proveedor=partner.id
    #     fecha_actual=datetime.datetime.now()
    #     if moves:
    #       for mov in moves:
    #         if mov.moneda_currency == 'MXN':
    #           moneda=33
    #         if mov.moneda_currency=='USD':
    #           moneda=2
    #         lines = self.env['product.template'].search([
    #             '|',
    #             ('default_code', '=', mov.clave_parte),
    #             ('sku_alternos.name', 'in', [mov.clave_parte])
    #         ])

    #         if lines:
    #           for line in lines:
    #             proveedores=self.env['product.supplierinfo'].search([('product_tmpl_id','=',line.id),('partner_id','=',proveedor)])
    #             if proveedores:
    #               for prov in proveedores:
    #                 prov.write({
    #                   'partner_id':proveedor,
    #                   'product_tmpl_id':line.id,
    #                   'existencia_actual':mov.Existencia_Stock,
    #                   'currency_id':33,
    #                   'price':mov.FS * mov.TC,
    #                   'ultima_actualizacion': fecha_actual,
    #                   'tipo_cambio':mov.TC,
    #                   'precio_neto':mov.FS,
    #                   'tipo_moneda_proveedor':mov.moneda_currency,
    #                 })
                
    #             if len(proveedores) == 0:
    #               new_record=self.env['product.supplierinfo'].create({
    #                 'partner_id':proveedor,
    #                 'product_tmpl_id':line.id,
    #                 'existencia_actual':mov.Existencia_Stock,
    #                 'currency_id':33,
    #                 'price':mov.FS * mov.TC,
    #                 'ultima_actualizacion': fecha_actual,
    #                 'tipo_cambio':mov.TC,
    #                 'precio_neto':mov.FS,
    #                 'tipo_moneda_proveedor':mov.moneda_currency,
    #               })
                  
    #           # mov.unlink()

    #     return {            
    #        'type': 'ir.actions.client',
    #        'tag': 'display_notification',            
    #        'params': {
    #            'type': 'success',                
    #            'sticky': False,
    #            'message': ("Se actualizaron los datos correctamente"),            
    #         }        
    #     }

    def procesar_tiredirect(self):
        # Buscar movimientos de proveedor "Tire Direct"
        moves = self.env['llantas_config.ctt_prov'].search([('nombre_proveedor', '=', 'Tire Direct')])
        
        # Buscar el partner correspondiente a "TIRE DIRECT S.A. DE C.V."
        partner = self.env['res.partner'].search([('name', '=', 'TIRE DIRECT S.A. DE C.V.')], limit=1)
        proveedor = partner.id if partner else False
        
        fecha_actual = fields.Datetime.now()
        
        # Diccionario para mapear monedas a sus valores equivalentes
        moneda_map = {
            'MXN': 33,
            'USD': 2
        }
        
        count_actualizados = 0
        count_agregados = 0
        
        if moves:
            for mov in moves:
                # Obtener el valor de la moneda según el tipo de cambio
                moneda = moneda_map.get(mov.moneda_currency, 1)  # Valor predeterminado si no se encuentra la moneda
                
                # Buscar el producto basado en el código o alternativos
                lines = self.env['product.template'].search([
                    '|',
                    ('default_code', '=', mov.clave_parte),
                    ('sku_alternos.name', 'in', [mov.clave_parte])
                ], limit=1)
                
                if lines:
                    for line in lines:
                        # Buscar información de proveedor existente
                        query = """
                            SELECT id FROM product_supplierinfo
                            WHERE product_tmpl_id = %s
                            AND partner_id = %s
                            LIMIT 1
                        """
                        self.env.cr.execute(query, (line.id, proveedor))
                        result = self.env.cr.fetchone()
                        
                        if result:
                            supplier_info_id = result[0]
                            
                            # Actualizar información existente
                            query = """
                                UPDATE product_supplierinfo
                                SET existencia_actual = %s,
                                    currency_id = %s,
                                    price = %s,
                                    ultima_actualizacion = %s,
                                    tipo_cambio = %s,
                                    precio_neto = %s,
                                    tipo_moneda_proveedor = %s
                                WHERE id = %s
                            """
                            values = (
                                mov.Existencia_Stock,
                                moneda,
                                mov.FS * mov.TC,
                                fecha_actual,
                                mov.TC,
                                mov.FS,
                                mov.moneda_currency,
                                supplier_info_id
                            )
                            self.env.cr.execute(query, values)
                            count_actualizados += 1
                        else:
                            # Crear nuevo registro de proveedor
                            query = """
                                INSERT INTO product_supplierinfo (partner_id, product_tmpl_id, existencia_actual, currency_id, price,
                                                                  ultima_actualizacion, tipo_cambio, precio_neto, tipo_moneda_proveedor)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """
                            values = (
                                proveedor,
                                line.id,
                                mov.Existencia_Stock,
                                moneda,
                                mov.FS * mov.TC,
                                fecha_actual,
                                mov.TC,
                                mov.FS,
                                mov.moneda_currency
                            )
                            self.env.cr.execute(query, values)
                            count_agregados += 1
        
        # Opcionalmente, puedes eliminar los registros movidos
        # for mov in moves:
        #     mov.unlink()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'sticky': False,
                'message': f"Se actualizaron {count_actualizados} registros y se agregaron {count_agregados} nuevos registros correctamente.",
            }
        }

    # def procesar_tiredirect(self):
    #     # Buscar movimientos de proveedor "Tire Direct"
    #     moves = self.env['llantas_config.ctt_prov'].search([('nombre_proveedor', '=', 'Tire Direct')])
        
    #     # Buscar el partner correspondiente a "TIRE DIRECT S.A. DE C.V."
    #     partner = self.env['res.partner'].search([('name', '=', 'TIRE DIRECT S.A. DE C.V.')], limit=1)
    #     proveedor = partner.id if partner else False
        
    #     fecha_actual = fields.Datetime.now()
        
    #     # Diccionario para mapear monedas a sus valores equivalentes
    #     moneda_map = {
    #         'MXN': 33,
    #         'USD': 2
    #     }
        
    #     count_actualizados = 0
    #     count_agregados = 0
        
    #     if moves:
    #         for mov in moves:
    #             # Obtener el valor de la moneda según el tipo de cambio
    #             moneda = moneda_map.get(mov.moneda_currency, 1)  # Valor predeterminado si no se encuentra la moneda
                
    #             # Buscar el producto basado en el código o alternativos
    #             lines = self.env['product.template'].search([
    #                 '|',
    #                 ('default_code', '=', mov.clave_parte),
    #                 ('sku_alternos.name', 'in', [mov.clave_parte])
    #             ])
                
    #             if lines:
    #                 for line in lines:
    #                     # Buscar información de proveedor existente
    #                     proveedores = self.env['product.supplierinfo'].search([
    #                         ('product_tmpl_id', '=', line.id),
    #                         ('partner_id', '=', proveedor)
    #                     ])
                        
    #                     vals = {
    #                         'partner_id': proveedor,
    #                         'product_tmpl_id': line.id,
    #                         'existencia_actual': mov.Existencia_Stock,
    #                         'currency_id': moneda,
    #                         'price': mov.FS * mov.TC,
    #                         'ultima_actualizacion': fecha_actual,
    #                         'tipo_cambio': mov.TC,
    #                         'precio_neto': mov.FS,
    #                         'tipo_moneda_proveedor': mov.moneda_currency,
    #                     }
                        
    #                     if proveedores:
    #                         # Actualizar información existente
    #                         proveedores.write(vals)
    #                         count_actualizados += 1
    #                     else:
    #                         # Crear nuevo registro de proveedor
    #                         self.env['product.supplierinfo'].create(vals)
    #                         count_agregados += 1
        
    #     # Opcionalmente, puedes eliminar los registros movidos
    #     # for mov in moves:
    #     #     mov.unlink()
        
    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'display_notification',
    #         'params': {
    #             'type': 'success',
    #             'sticky': False,
    #             'message': f"Se actualizaron {count_actualizados} registros y se agregaron {count_agregados} nuevos registros correctamente.",
    #         }
    #     }


class status_ventas(models.Model):
    _name = 'llantas_config.status_ventas'
    _description = 'Catalogo de status'
    _order = 'id desc'
    # _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Nombre",
        required=True,

    )
    
    description=fields.Char(
        string="Descripción",

    )
    
    color = fields.Integer(
        string="Color",
        required=True,
        
    )

class carriers(models.Model):
    _name = 'llantas_config.carrier'
    _description = 'Catalogo carriers'
    _order = 'id desc'
    # _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Nombre",
        required=True,
    )

    url=fields.Char(
        string="Url"
    )

    is_trackeable=fields.Boolean(
        string="Rastreable?"
    )

    company_id=fields.Many2one(
        "res.company",
        string="Empresa",
    )

class sku_marketplaces(models.Model):
    _name = 'llantas_config.sku_marketplace'
    _description = 'Catalogo de sku'
    _order = 'id desc'
    # _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Nombre",
        required=True,
    )

    marketplace=fields.Many2one(
        "llantas_config.marketplaces",
        string="Marketplace relacionado",
        # company_dependent=True,
    )
    
    Proveedor_id=fields.Many2one(
        "res.partner",
        string="Proveedor"
    )
    
    product_id=fields.Many2one(
        "product.template",
        string="Producto",
    )

    color=fields.Integer(
        string="Color",
    )
    
class almacenes_proveedores(models.Model):
    _name = 'llantas_config.almacenes_prov'
    _description = 'Almacenes de proveedores'
    _order = 'id desc'
    # _inherit = ['mail.thread', 'mail.activity.mixin']

    partner_id = fields.Many2one(
        "res.partner",
        string="Proveedor",
        tracking=True,
        required=True
    )

    sucursal=fields.Char(
        string="Sucursal",
        tracking=True,
        required=True
    )
    
    almacen=fields.Integer(
        string="Almacen",
        tracking=True,
        required=True
    )

    almacen_proveedor=fields.Char(
        string="Almacen proveedor",
        tracking=True,
    )

class compatibilidad(models.Model):
    _name = 'llantas_config.compatibilidad'
    _description = 'Compatibilidad de llanta'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def name_get(self):
        res = super(compatibilidad, self).name_get()
        data = []
        for e in self:
            display_value = ''
            display_value += str(e.brand_id.name)
            display_value += ' / '
            display_value += str(e.model_id.name) or ""
            display_value += ' / '
            display_value += str(e.year) or ""
            display_value += ' / '
            display_value += str(e.version) or ""
            display_value += ' / '
            display_value += str(e.medida) or ""
            data.append((e.id, display_value))
        return data

    ##Campo para product.product
    # compatibilidad_ids = fields.One2many(
    #     'product_id',
    #     'llantas_config.compatibilidad',
    #     string = "Modelos de auto compatibles"
    # )

    product_id = fields.Many2one(
        'product.template',
        string = "Producto"
    )

    brand_id = fields.Many2one(
        'fleet.vehicle.model.brand',
        string = "Marca"
    )

    model_id = fields.Many2one(
        'fleet.vehicle.model',
        string = "Modelo"
    )

    year = fields.Integer(
        string="Año"
    )

    version = fields.Char(
        string="Versión"
    )

    medida = fields.Char(
        string="Medida"
    )
    
class pronto_pago(models.Model):
    _name = 'llantas_config.pronto_pago'
    _description = 'Pronto pago'
    _order = 'id desc'
    # _inherit = ['mail.thread', 'mail.activity.mixin']

    def name_get(self):
        res = super(pronto_pago, self).name_get()
        data = []
        for e in self:
            display_value = ''
            display_value += str(e.name)
            display_value += ' - '
            display_value += str(e.pronto_pago_porcentaje) or ""
            display_value += '%'
            data.append((e.id, display_value))
        return data
        
    name=fields.Char(
        string="Nombre",
    )
    
    pronto_pago_dias_vencimiento = fields.Integer(
        string="Días para vencimiento"
    )

    pronto_pago_porcentaje = fields.Float(
        string="Porcentaje de descuento"
    )

    product_category = fields.Many2one(
        "product.category",
        string="Categoria de producto",
        # tracking=True,
        store=True,
    )

    partner_id=fields.Many2one(
        "res.partner",
        string="Contacto",
        store=True,
    )



    
    
    
class killer_list(models.Model):
    _name = 'llantas_config.killer_list'
    _description = 'Listado killers'
    _order = 'id desc'

    
    product_id=fields.Many2one(
        "product.template",
        string="Producto",
        store=True,
    )
    
    sku=fields.Char(
        string="sku",
        related="product_id.default_code",
    )
    
    killer_price=fields.Float(
        string="Precio killer",
    )
    
    final_date=fields.Datetime(
        string="Fecha final",
    )

    marketplace_id=fields.Many2one(
        "llantas_config.marketplaces",
        string="Marketplace",
        store=True,
    )

    status = fields.Selection([
        ('active', 'Activo'),
        ('expired', 'Vencido'),
        ('cancelled', 'Cancelado'),
        ('pause','Pausado'),
    ], string="Estado", default='active')

    base_price = fields.Float(
        string="Precio base",
    )
    
    promotion_price=fields.Float(
        string="Precio promoción",
    )
    
    initial_date=fields.Datetime(
        string="Fecha inicial",
    )

class killer_no_product_list(models.Model):
    _name = 'llantas_config.killer_no_product'
    _description = 'Listado productos no encontrados'
    _order = 'id desc'

    
    product=fields.Char(
        string="Producto",
    )
    
    sku=fields.Char(
        string="sku"
    )
    
    killer_price=fields.Float(
        string="Precio killer",
    )
    
    final_date=fields.Datetime(
        string="Fecha final",
    )

    marketplace_id=fields.Many2one(
        "llantas_config.marketplaces",
        string="Marketplace",
        store=True,
    )

    base_price = fields.Float(
        string="Precio base",
    )
    
    promotion_price=fields.Float(
        string="Precio promoción",
    )
    
    initial_date=fields.Datetime(
        string="Fecha inicial",
    )


