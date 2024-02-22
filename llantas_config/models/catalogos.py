from odoo import models, fields, api, _
import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
import datetime
import urllib.request 
import json  

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
    
    def action_button_procesar(self):

        if self.proveedores_links_id.name == 'Tire Direct':
            # raise UserError(str(self.proveedores_links_id.name))
            self.proveedores_links_id.procesar_tiredirect()
        else:
            # raise UserError(str(self.proveedores_links_id.name)+"123")
            self.proveedores_links_id.procesar()

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
                self.env['llantas_config.ctt_tiredirect_cargar'].create({
                    'description_description': x["Descripcion_Description"],
                    'clave_parte': x["Clave_Parte"],
                    'moneda_currency': x["Moneda_Currency"],
                    'TC': x["TC"],
                    'ES': x["ES"],
                    'FS': x["FS"],
                    'Existencia_Stock': x["Existencia_Stock"],
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
            # return {
            #     raise UserError('Existencias cargadas, a continuación de clic en procesar')
                # 'name': 'Cargar existencias',
                # 'view_type': 'tree',
                # 'view_mode': 'tree',
                # 'view_id': self.env.ref('llantas_config.view_tiredirect_tree_cargar').id,
                # 'res_model': 'llantas_config.ctt_tiredirect_cargar',
                # 'type': 'ir.actions.act_window',
                # 'target': 'new',
            # }
    # def procesar_existencias(self):
    #     for record in self:
    #         proveedor_id = record.proveedor_id

    #         if proveedor_id.name == 'TIRE DIRECT S.A. DE C.V.':
    #             self.env['llantas_config.ctt_tiredirect_cargar'].procesar_tiredirect(record)
    #         else:
    #             self.env['llantas_config.proveedores_links'].action_button_procesar(record)
          

    #     return True

    

    def procesar(self):
        count_actualizados = 0
        count_agregados = 0
        count_sin_encontrar = 0
        sku_proveedor_procesados = set()
    
        moves = self.env['llantas_config.ctt_prov'].search([('nombre_proveedor', '=', self.name)])
        partner = self.env['res.partner'].search([('name', '=', self.proveedor_id.name)], limit=1)
        proveedor = partner.id
        # raise UserError(str(partner.name))
        fecha_actual = datetime.datetime.now()
    
        if moves:
            for mov in moves:
                if mov.tipo_moneda == 'MXN':
                    moneda = 33
                elif mov.tipo_moneda == 'USD':
                    moneda = 2
                else:
                    moneda = 33
                lines = self.env['product.template'].search([
                    '|',
                    ('default_code', '=', mov.sku),
                    ('sku_alternos.name', 'in', [mov.sku])
                ])

                if lines:
                    for line in lines:
                        sku_proveedor = (line.id, proveedor)
    
                        if sku_proveedor not in sku_proveedor_procesados:
                            proveedores = self.env['product.supplierinfo'].search([
                                ('product_tmpl_id', '=', line.id),
                                ('partner_id', '=', proveedor)],
                                limit=1)
    
                            try:
                                if proveedores.exists():
                                    proveedores_existente = proveedores.filtered(lambda p: p.partner_id == proveedor)
                                    if proveedores_existente:
                                        print(f"SKU {mov.sku} ya procesado para el proveedor {proveedor.name}. Omitiendo.")
                                    else:
                                        proveedores.write({
                                            'partner_id': proveedor,
                                            'currency_id': moneda,
                                            'price': mov.costo_sin_iva * mov.tipo_cambio,
                                            'ultima_actualizacion': fecha_actual,
                                            'tipo_cambio': mov.tipo_cambio,
                                            'precio_neto': mov.costo_sin_iva,
                                            'tipo_moneda_proveedor': mov.tipo_moneda,
                                        })
                                        count_actualizados += 1
                                else:
                                    self.env['product.supplierinfo'].create({
                                        'partner_id': proveedor,
                                        'product_tmpl_id': line.id, 
                                        'currency_id': moneda,
                                        'price': mov.costo_sin_iva * mov.tipo_cambio,
                                        'ultima_actualizacion': fecha_actual,
                                        'tipo_cambio': mov.tipo_cambio,
                                        'precio_neto': mov.costo_sin_iva,
                                        'tipo_moneda_proveedor': mov.tipo_moneda,
                                    })
                                    count_agregados += 1
    
                                sku_proveedor_procesados.add(sku_proveedor)
                            except Exception as e:
                                error_message = f"No se pudo agregar el nuevo registro para SKU {mov.sku} y proveedor {proveedor}: {e}"
                                print(error_message)
                                raise UserError(error_message)
                        else:
                            print(f"SKU {mov.sku} y proveedor {proveedor} ya procesados. Omitiendo.")
                else:
                    count_sin_encontrar += 1
    
        # print(f"Registros actualizados: {count_actualizados}")
        # print(f"Nuevos registros agregados: {count_agregados}")
        # print(f"Registros no encontrados: {count_sin_encontrar}")
        # print(f"Se actualizaron {count_actualizados} registros y se agregaron {count_agregados} nuevos registros correctamente. No se encontraron {count_sin_encontrar}.")
        
        return {            
           'type': 'ir.actions.client',
           'tag': 'display_notification',            
           'params': {
               'type': 'success',                
               'sticky': False,
               'message': f"Se actualizaron {count_actualizados} registros y se agregaron {count_agregados} nuevos registros correctamente. No se encontraron {count_sin_encontrar}.",   
               # 'reload': True,  # Solicita recargar la vista actual
            }
        }

        
    def procesar_tiredirect(self):
        moves=self.env['llantas_config.ctt_tiredirect_cargar'].search([])
        partner=self.env['res.partner'].search([('name','=','TIRE DIRECT S.A. DE C.V.')], limit=1)
        proveedor=partner.id
        fecha_actual=datetime.datetime.now()
        if moves:
          for mov in moves:
            if mov.moneda_currency == 'MXN':
              moneda=33
            if mov.moneda_currency=='USD':
              moneda=2
            lines = self.env['product.template'].search([
                '|',
                ('default_code', '=', mov.clave_parte),
                ('sku_alternos.name', 'in', [mov.clave_parte])
            ])

            if lines:
              for line in lines:
                proveedores=self.env['product.supplierinfo'].search([('product_tmpl_id','=',line.id),('partner_id','=',proveedor)])
                if proveedores:
                  for prov in proveedores:
                    prov.write({
                      'partner_id':proveedor,
                      'product_tmpl_id':line.id,
                      'existencia_actual':mov.Existencia_Stock,
                      'currency_id':33,
                      'price':mov.FS * mov.TC,
                      'ultima_actualizacion':fecha_actual,
                      'tipo_cambio':mov.TC,
                      'precio_neto':mov.FS,
                      'tipo_moneda_proveedor':mov.moneda_currency,
                    })
                
                if len(proveedores) == 0:
                  new_record=self.env['product.supplierinfo'].create({
                    'partner_id':proveedor,
                    'product_tmpl_id':line.id,
                    'existencia_actual':mov.Existencia_Stock,
                    'currency_id':33,
                    'price':mov.FS * mov.TC,
                    'ultima_actualizacion':fecha_actual,
                    'tipo_cambio':mov.TC,
                    'precio_neto':mov.FS,
                    'tipo_moneda_proveedor':mov.moneda_currency,
                  })
                  
              mov.unlink()

        return {            
           'type': 'ir.actions.client',
           'tag': 'display_notification',            
           'params': {
               'type': 'success',                
               'sticky': False,
               'message': ("Se actualizaron los datos correctamente"),            
            }        
        }


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

