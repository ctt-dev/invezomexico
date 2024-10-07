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

    yuju_tag=fields.Selection(
        [
            ('13','Mercado Libre Mexico'),
            ('2201','Claro Shop'),
            ('2401','Liverpool'),
            ('3401','Coppel'),
            ('1901','Shopify'),
            ('3101','Elektra'),
            ('2102','Walmart')
        ],
    )

    venta_directa = fields.Boolean(
        string="¿Venta directa?",
        tracking=True,
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


    query_insert_descargas = fields.Text(string="Query Insert")
    query_update_descargas = fields.Text(string="Query Update")
    procesar_descargas = fields.Boolean(string="Procesar descarga", default=False)
    
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

    
    def procesar_concentrado(self):
        try:
            # Establecer el timeout y la URL
            response = urllib.request.urlopen(self.url, timeout=30)  # Timeout de 30 segundos
            data = json.loads(response.read().decode())
        except Exception as e:
            raise UserError(f"Error al obtener datos del JSON: {e}")
        
        update_queries = []
        insert_queries = []
        update_params = []
        insert_params = []
    
        tipo_cambio = 1
        fecha_actual = datetime.datetime.now()
    
        for record in data:
            if isinstance(record, dict):
                sku_proveedor = record.get('SKU PROVEEDOR', 'N/A')
                existencia = record.get('EXISTENCIA PROVEEDOR', 0)
                costo = record.get('COSTO PROVEEDOR', 0.0) * tipo_cambio
                producto = record.get('PRODUCTO', 'N/A')
                proveedor = record.get('PROVEEDOR', 'N/A')
    
                # Verificar si el registro existe en llantas_config.ctt_prov
                existing_record = self.env['llantas_config.ctt_prov'].search([
                    ('nombre_proveedor', '=', proveedor),
                    ('sku', '=', sku_proveedor)
                ], limit=1)
    
                if existing_record:
                    # Si el registro existe y el costo o la existencia han cambiado, generar el query de actualización
                    if existing_record.costo_sin_iva != costo or existing_record.existencia != existencia:
                        update_queries.append("""
                            UPDATE llantas_config_ctt_prov 
                            SET existencia = %s, 
                                costo_sin_iva = %s, 
                                fecha_actualizacion = %s, 
                                procesado = FALSE 
                            WHERE id = %s;
                        """)
                        update_params.extend([existencia, costo, fecha_actual, existing_record.id])
                    else:
                        # Solo actualizar la fecha si no hay cambios en el costo o existencia
                        update_queries.append("""
                            UPDATE llantas_config_ctt_prov 
                            SET fecha_actualizacion = %s, 
                                procesado = FALSE 
                            WHERE id = %s;
                        """)
                        update_params.extend([fecha_actual, existing_record.id])
                else:
                    # Si no existe un registro que coincida, generar el query de inserción
                    insert_queries.append("""
                        INSERT INTO llantas_config_ctt_prov 
                            (nombre_proveedor, sku, producto, nombre_almacen, existencia, costo_sin_iva, tipo_moneda, tipo_cambio, fecha_actualizacion, procesado) 
                        VALUES 
                            (%s, %s, %s, %s, %s, %s, 'MXN', %s, %s, FALSE);
                    """)
                    insert_params.extend([proveedor, sku_proveedor, producto, proveedor, existencia, costo, tipo_cambio, fecha_actual])
    
        # Ejecutar los queries generados
        if update_queries:
            self.env.cr.execute(" ".join(update_queries), tuple(update_params))
    
        if insert_queries:
            self.env.cr.execute(" ".join(insert_queries), tuple(insert_params))
    
        return {
            'message': "Datos procesados correctamente",
            'proveedor': self.proveedor_id.name
        }

    def probar_json(self):
        url1 = "https://script.googleusercontent.com/macros/echo?user_content_key=-nPb1guziFdeML89XAF8sgJtQmuMVWAq0dYIzSc_wZs3QRZeZpoVTKxxZCIhlaOohqfBl6vOUGor4G14ndO5EM3JPYZbyKsjm5_BxDlH2jW0nuo2oDemN9CCS2h10ox_1xSncGQajx_ryfhECjZEnFXKTdTCSsWPTXVM0gnF7bJnigLD7sxsdMOYrTVQl1vVMVRwkiVMGx9SsVmTKE85jS9VA075VAQmtNUHgqsKZo-8mzDTCqnGIg&lib=M4m5NS-apNCUtcNwkLEarFEAXVMBT1kpy"

        url2 ="https://script.googleusercontent.com/macros/echo?user_content_key=N1_BAqUH6r5aCxfcAdoy1Osj2k22NDrcN4AXfMEa7hxmU2k9DyRpkwHSLxY0G58R-o5hkTEui5fvlNVPihU1vv-tqTbjp8pxm5_BxDlH2jW0nuo2oDemN9CCS2h10ox_1xSncGQajx_ryfhECjZEnJs6yOTCCz2AYTectuQhThkO3fnnGxjdOTTXTjGldiZczBRDjSifi-5uXJ1SHiVnFQ0WnERPH6M5wFj3GPAqa3FUrveNIGQWYtz9Jw9Md8uu&lib=MFcnFjvRWaVIWX7Ujvv2ZzNOZyGFvGpb3"
        
        # Función para probar una URL
        def probar_url(url):
            try:
                response = urllib.request.urlopen(url, timeout=30)
                if response.getcode() != 200:
                    raise UserError(f"Error al obtener datos: la URL devolvió el código de estado {response.getcode()}")
                content = response.read().decode()
                if not content:
                    raise UserError(f"La respuesta de la URL está vacía.")
                return content
            except Exception as e:
                raise UserError(f"Error al obtener datos del JSON: {e}")
        
        # Probar ambas URLs
        content1 = probar_url(url1)
        content2 = probar_url(url2)
        
        # Mostrar los primeros 500 caracteres de cada respuesta para comparar
        raise UserError(f"Respuesta URL 1: {content1[:500]}\n\nRespuesta URL 2: {content2[:500]}")
    
    def procesar_concentrado2(self):
        try:
            # Intentar abrir la URL y obtener los datos
            response = urllib.request.urlopen(self.url, timeout=30)  # Timeout de 30 segundos
            data = json.loads(response.read().decode())
            
            # Depurar el JSON recibido
            if not data:
                raise UserError("El JSON está vacío o no tiene el formato esperado.")
            
            # Verificar el contenido del JSON
            # Puedes revisar los primeros registros si es muy largo
            _logger.info(f"Datos recibidos del JSON: {data[:5]}")  # Muestra los primeros 5 registros
    
        except Exception as e:
            raise UserError(f"Error al obtener datos del JSON: {e}")
    
        # Inicialización de variables
        tipo_cambio = 1  # Suponiendo un tipo de cambio fijo
        fecha_actual = datetime.datetime.now()
    
        # Procesar cada registro del JSON
        for record in data:
            if isinstance(record, dict):
                sku_proveedor = record.get('Codigo', 'N/A')
                existencia = record.get('Cantidad', 0)
                costo = record.get('Precio', 0.0) * tipo_cambio
                producto = record.get('Descripcion', 'N/A')
                proveedor = record.get('Proveedor', 'N/A')
                almacen = record.get('Almacen', 'N/A')
    
                # Buscar registro existente en Odoo
                existing_record = self.env['llantas_config.ctt_prov'].search([
                    ('nombre_proveedor', '=', proveedor),
                    ('sku', '=', sku_proveedor),
                    ('nombre_almacen', '=', almacen),
                ], limit=1)
    
                if existing_record:
                    if existing_record.costo_sin_iva != costo or existing_record.existencia != existencia:
                        existing_record.write({
                            'existencia': existencia,
                            'costo_sin_iva': costo,
                            'fecha_actualizacion': fecha_actual,
                            'procesado': False
                        })
                    else:
                        existing_record.write({
                            'fecha_actualizacion': fecha_actual,
                            'procesado': False
                        })
                else:
                    self.env['llantas_config.ctt_prov'].create({
                        'nombre_proveedor': proveedor,
                        'sku': sku_proveedor,
                        'producto': producto,
                        'nombre_almacen': almacen,
                        'existencia': existencia,
                        'costo_sin_iva': costo,
                        'tipo_moneda': 'MXN',
                        'tipo_cambio': tipo_cambio,
                        'fecha_actualizacion': fecha_actual,
                        'procesado': False,
                        'subalmacenes': True
                    })
    
        return {
            'message': "Datos procesados correctamente",
            'proveedor': self.proveedor_id.name
        }

    def _cron_procesar_supplierinfo(self):
        batch_size = 1000
        self.procesar_supplierinfo(batch_size)

    query_create = fields.Text(string="Create")
    query_update = fields.Text(string="Update")
    query_delete = fields.Text(string="Delete")
    porcentaje = fields.Float(string="Porcentaje")
    obteniendo_datos = fields.Boolean(string="Obteniendo datos", default=False)
        

    def procesar_supplierinfo(self, batch_size=None):
        _logger.warning("****** procesar_supplierinfo - 0")
        count_actualizados = 0
        count_agregados = 0
        count_sin_encontrar = 0
        sku_proveedor_procesados = set()
        moneda = self.env['res.currency'].search([('name', '=', 'MXN')], limit=1)
        fecha_actual = datetime.datetime.now()
    
        domain = [
            ('procesado', '=', False),
            '|', ('sku_interno', '!=', ""),
            ('sku_interno', '!=', False),
            ('partner_id', '!=', False)
        ]
        moves = self.env['llantas_config.ctt_prov'].search(domain, limit=3000)
    
        query_create = ""
        query_update = ""
        query_delete = ""
        update_movs_data = []
        delete_ids = []
    
        _logger.warning("****** procesar_supplierinfo - 1")
    
        for move in moves:
            try:
                proveedor = move.partner_id.id
                sku_proveedor = (move.sku, proveedor)
                if sku_proveedor not in sku_proveedor_procesados:
                    lines = self.env['product.template'].search([
                        ('default_code', '=', move.sku_interno),
                        ('es_paquete', '=', False),
                        ('detailed_type', '=', 'product')
                    ])
                    if lines:
                        for line in lines:
                            supplier_info = self.env['product.supplierinfo'].search([
                                ('product_tmpl_id', '=', line.id),
                                ('partner_id', '=', proveedor)
                            ], limit=1)
    
                            if supplier_info:
                                if supplier_info.price == move.costo_sin_iva:
                                    query_update += f"""UPDATE product_supplierinfo SET ultima_actualizacion='{fecha_actual}' WHERE id={supplier_info.id};\n"""
                                    count_actualizados += 1
                                else:
                                    query_update += f"""UPDATE product_supplierinfo SET currency_id={moneda.id}, price={move.costo_sin_iva}, ultima_actualizacion='{fecha_actual}', tipo_cambio=1, precio_neto={move.costo_sin_iva}, tipo_moneda_proveedor='MXN', product_code='{move.sku}', existencia_actual={move.existencia} WHERE id={supplier_info.id};\n"""
                                    count_actualizados += 1
                                # Actualiza los campos procesado y fecha_actualizacion
                                update_movs_data.append(f"""UPDATE llantas_config_ctt_prov SET procesado = TRUE, fecha_actualizacion = '{fecha_actual}', sku_interno = '{move.sku_interno}', costo_sin_iva = {move.costo_sin_iva} WHERE id = {move.id};\n""")
                            else:
                                if move.existencia == 0:
                                    continue
                                query_create += f"""INSERT INTO product_supplierinfo (partner_id, product_tmpl_id, currency_id, price, ultima_actualizacion, tipo_cambio, precio_neto, tipo_moneda_proveedor, product_code, existencia_actual, delay, min_qty) VALUES ({proveedor}, {line.id}, {moneda.id}, {move.costo_sin_iva}, '{fecha_actual}', 1, {move.costo_sin_iva}, 'MXN', '{move.sku}', {move.existencia}, 7, 1);\n"""
                                count_agregados += 1
                                # Actualiza los campos procesado y fecha_actualizacion
                                update_movs_data.append(f"""UPDATE llantas_config_ctt_prov SET procesado = TRUE, fecha_actualizacion = '{fecha_actual}', sku_interno = '{move.sku_interno}', costo_sin_iva = {move.costo_sin_iva} WHERE id = {move.id};\n""")
    
                    else:
                        count_sin_encontrar += 1
                        delete_ids.append(move.id)
    
                sku_proveedor_procesados.add(sku_proveedor)
    
            except Exception as e:
                _logger.error(f"Error processing move ID {move.id}: {str(e)}")
    
        # Generar la consulta de eliminación
        if delete_ids:
            ids_str = ', '.join(map(str, delete_ids))
            query_delete = f"DELETE FROM llantas_config_ctt_prov WHERE id IN ({ids_str});"
        else:
            query_delete = ""
    
        # Ejecutar las consultas de actualización y creación
        if update_movs_data:
            self.env.cr.execute('\n'.join(update_movs_data))
        
        # Registro de las consultas para depuración
        _logger.warning(f"Query Create: {query_create}")
        _logger.warning(f"Length of query_create: {len(query_create)}")
        _logger.warning(f"Query Update: {query_update}")
        _logger.warning(f"Length of query_update: {len(query_update)}")
        _logger.warning(f"Query Delete: {query_delete}")
    
        # Guardar las consultas en el modelo
        self.write({
            'query_create': query_create if query_create else None,
            'query_update': query_update if query_update else None,
            'query_delete': query_delete if query_delete else None,
            'porcentaje': 100,  # Solo mostrar al 100% cuando el proceso termine
            'obteniendo_datos': True,
        })
    
        _logger.warning("****** procesar_supplierinfo - 4")
        return {
            'count_actualizados': count_actualizados,
            'count_agregados': count_agregados,
            'count_sin_encontrar': count_sin_encontrar
        }


    def ejecutar_consultas_sql(self):
        try:
            # Recuperar las consultas SQL almacenadas en el campo de texto
            query_create = self.query_create
            query_update = self.query_update
            query_delete = self.query_delete
    
            # Ejecutar las consultas, si existen
            if query_create:
                self.env.cr.execute(query_create)
                _logger.info("Consultas INSERT ejecutadas correctamente.")
            
            if query_update:
                self.env.cr.execute(query_update)
                _logger.info("Consultas UPDATE ejecutadas correctamente.")
            
            if query_delete:
                self.env.cr.execute(query_delete)
                _logger.info("Consultas DELETE ejecutadas correctamente.")
            
            # Marcar el proceso como completado
            self.write({
                'porcentaje': 0,
                'obteniendo_datos': False,
                'query_create': False,
                'query_update':False,
                'query_delete':False,
            })
        
        except Exception as e:
            _logger.error(f"Error al ejecutar consultas SQL: {str(e)}")
            # Manejo de errores si es necesario
    
        return {
            'message': "Consultas SQL procesadas correctamente."
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
        updates_by_proveedor = defaultdict(list)
        inserts_by_proveedor = defaultdict(list)
        update_movs_data = []
        delete_ids = []
    
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
                    if line.es_paquete or line.detailed_type != 'product':
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
                            if (supplier_info.price == costo_mas_bajo and 
                                supplier_info.partner_id.id == proveedor and 
                                supplier_info.product_tmpl_id.id == line.id):
                                continue
                            else:
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
                                    updates_by_proveedor[proveedor].append((query, values))
                                    count_actualizados += 1
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
                                    updates_by_proveedor[proveedor].append((query, values))
                                    count_actualizados += 1
                                   
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
                            inserts_by_proveedor[proveedor].append((query, values))
                            count_agregados += 1
                        sku_proveedor_procesados.add(sku_proveedor)
                        
                        # Acumular datos para actualización en bloque
                        for mov in sku_moves:
                            update_movs_data.append((mov.id, fecha_actual, line.default_code, costo_mas_bajo))
    
            else:
                count_sin_encontrar += 1
                delete_ids.append(mov.id)
    
        # Ejecutar todas las actualizaciones e inserciones acumuladas por proveedor
        for proveedor, updates in updates_by_proveedor.items():
            for query, values in updates:
                self.env.cr.execute(query, values)
        
        for proveedor, inserts in inserts_by_proveedor.items():
            for query, values in inserts:
                self.env.cr.execute(query, values)
        
        # Actualizar registros de llantas_config.ctt_prov en bloque
        if update_movs_data:
            update_query = """
                UPDATE llantas_config_ctt_prov
                SET procesado = TRUE, fecha_actualizacion = %s, sku_interno = %s, costo_sin_iva = %s
                WHERE id = %s
            """
            for id, fecha, sku_interno, costo in update_movs_data:
                self.env.cr.execute(update_query, (fecha, sku_interno, costo, id))
        
        # Eliminar registros en bloque
        if delete_ids:
            self.env.cr.execute("DELETE FROM llantas_config_ctt_prov WHERE id IN %s", (tuple(delete_ids),))
    
        movimientos_restantes = self.env['llantas_config.ctt_prov'].search([('nombre_proveedor', '=', self.name), ('procesado', '=', False)])
        if not movimientos_restantes:
            sale_warn_msg="Todos los productos han sido procesados. No hay productos pendientes por procesar."
            return {
                'warning': {
                    'title': _("Advertencia"),
                    'message': sale_warn_msg,
                }
            }
    
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'sticky': False,
                'message': f"Se actualizaron {count_actualizados} registros y se agregaron {count_agregados} nuevos registros correctamente. No se encontraron {count_sin_encontrar}.",
            }
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



    # def procesar(self, limite):
    #     count_actualizados = 0
    #     count_agregados = 0
    #     count_sin_encontrar = 0
    #     sku_proveedor_procesados = set()
    #     moneda = self.env['res.currency'].search([('name', '=', 'MXN')])
    #     moves = self.env['llantas_config.ctt_prov'].search([('nombre_proveedor', '=', self.name), ('procesado', '=', False)], limit=limite)
    #     partner = self.env['res.partner'].search([('name', '=', self.proveedor_id.name)], limit=1)
    #     proveedor = partner.id if partner else False
    #     fecha_actual = datetime.datetime.now()
        
    #     existencias_por_sku_proveedor = defaultdict(float)
    #     for move in moves:
    #         lines = self.env['product.template'].search([
    #             '|',
    #             ('default_code', '=', move.sku),
    #             ('sku_alternos.name', 'in', [move.sku])
    #         ])
    #         if lines:
    #             for lin in lines:
    #                 if lin.es_paquete or not move.sku_interno:
    #                     continue
        
    #     for mov in moves:
    #         existencias_por_sku_proveedor[(mov.sku, proveedor)] += mov.existencia
        
    #     for (sku, proveedor), existencia_total in existencias_por_sku_proveedor.items():
    #         lines = self.env['product.template'].search([
    #             '|',
    #             ('default_code', '=', sku),
    #             ('sku_alternos.name', 'in', [sku])
    #         ])
    #         if lines:
    #             for line in lines:
    #                 if line.es_paquete or line.detailed_type != 'product':
    #                     continue
    
    #                 sku_proveedor = (line.id, proveedor)
    #                 if sku_proveedor not in sku_proveedor_procesados:
    #                     sku_moves = self.env['llantas_config.ctt_prov'].search([
    #                         ('sku', '=', sku),
    #                         ('nombre_proveedor', '=', self.name)
    #                     ])
    
    #                     tipo_cambio = 0
    #                     if sku_moves:
    #                         costo_mas_bajo = min(sku_moves.mapped('costo_sin_iva'))
    #                         filtered_moves = sku_moves.filtered(lambda x: x.costo_sin_iva == costo_mas_bajo)
    #                         tipo_cambio = filtered_moves[0].tipo_cambio if filtered_moves else 0
    #                     else:
    #                         costo_mas_bajo = 0.0
    
    #                     supplier_info = self.env['product.supplierinfo'].search([
    #                         ('product_tmpl_id', '=', line.id),
    #                         ('partner_id', '=', proveedor)
    #                     ], limit=1)
    
    #                     if supplier_info:
    #                         if supplier_info.price != costo_mas_bajo:
    #                             query = """
    #                                 UPDATE product_supplierinfo 
    #                                 SET 
    #                                     currency_id=%s,
    #                                     price=%s,
    #                                     ultima_actualizacion=%s,
    #                                     tipo_cambio=%s,
    #                                     precio_neto=%s,
    #                                     tipo_moneda_proveedor='MXN',
    #                                     product_code=%s,
    #                                     existencia_actual=%s
    #                                 WHERE id=%s
    #                             """
    #                             values = (
    #                                 moneda.id,
    #                                 costo_mas_bajo,
    #                                 fecha_actual,
    #                                 tipo_cambio,
    #                                 costo_mas_bajo,
    #                                 sku,
    #                                 existencia_total,
    #                                 supplier_info.id
    #                             )
    #                             self.env.cr.execute(query, values)
    #                             count_actualizados += 1
    #                             # self.env['llantas_config.ctt_prov'].search([
    #                             #     ('sku', '=', sku),
    #                             #     ('nombre_proveedor', '=', self.name)
    #                             # ])
    #                         else:
    #                             query = """
    #                                 UPDATE product_supplierinfo 
    #                                 SET 
    #                                     existencia_actual=%s,
    #                                     ultima_actualizacion=%s
    #                                 WHERE id=%s
    #                             """
    #                             values = (
    #                                 existencia_total,
    #                                 fecha_actual,
    #                                 supplier_info.id
    #                             )
    #                             self.env.cr.execute(query, values)
    #                             count_actualizados += 1
    #                             # self.env['llantas_config.ctt_prov'].search([
    #                             #     ('sku', '=', sku),
    #                             #     ('nombre_proveedor', '=', self.name)
    #                             # ])
    #                             _logger.info(f"Update record: {record}")
    #                     else:
    #                         if existencia_total == 0:
    #                             continue
    #                         query = """
    #                             INSERT INTO product_supplierinfo (partner_id, product_tmpl_id, currency_id, price, ultima_actualizacion,
    #                                                               tipo_cambio, precio_neto, tipo_moneda_proveedor, product_code, existencia_actual, delay, min_qty)
    #                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    #                         """
    #                         values = (
    #                             proveedor,
    #                             line.id,
    #                             moneda.id,
    #                             costo_mas_bajo,
    #                             fecha_actual,
    #                             tipo_cambio,
    #                             costo_mas_bajo,
    #                             'MXN',
    #                             sku,
    #                             existencia_total,
    #                             7,
    #                             1
    #                         )
    #                         self.env.cr.execute(query, values)
    #                         count_agregados += 1
    #                         # self.env['llantas_config.ctt_prov'].search([
    #                         #     ('sku', '=', sku),
    #                         #     ('nombre_proveedor', '=', self.name)
    #                         # ])
    #                     sku_proveedor_procesados.add(sku_proveedor)
    #         else:
    #             count_sin_encontrar += 1
    #             mov.unlink()
        
    #     # Verificar si quedan movimientos sin procesar
    #     movimientos_restantes = self.env['llantas_config.ctt_prov'].search([('nombre_proveedor', '=', self.name), ('procesado', '=', False)])
    #     if not movimientos_restantes:
    #         sale_warn_msg="odos los productos han sido procesados. No hay productos pendientes por procesar."
    #                 return {
    #                     'warning': {
    #                         'title': _("Advertencia"),
    #                         'message': sale_warn_msg,
    #                     }
    #                 }
    #         raise UserError("Todos los productos han sido procesados. No hay productos pendientes por procesar.")
    #         # return {
    #         #     'type': 'ir.actions.client',
    #         #     'tag': 'display_notification',
    #         #     'params': {
    #         #         'type': 'warning',
    #         #         'sticky': True,
    #         #         'message': "Todos los productos han sido procesados. No hay productos pendientes por procesar.",
    #         #     }
    #         # }
        
    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'display_notification',
    #         'params': {
    #             'type': 'success',
    #             'sticky': False,
    #             'message': f"Se actualizaron {count_actualizados} registros y se agregaron {count_agregados} nuevos registros correctamente. No se encontraron {count_sin_encontrar}.",
    #         }
    #     }
    # def procesar(self, limite):
    #     count_actualizados = 0
    #     count_agregados = 0
    #     count_sin_encontrar = 0
    #     sku_proveedor_procesados = set()
    #     moneda = self.env['res.currency'].search([('name', '=', 'MXN')])
    #     moves = self.env['llantas_config.ctt_prov'].search([('nombre_proveedor', '=', self.name), ('procesado', '=', False)], limit=limite)
    #     partner = self.env['res.partner'].search([('name', '=', self.proveedor_id.name)], limit=1)
    #     proveedor = partner.id if partner else False
    #     fecha_actual = datetime.datetime.now()
        
    #     existencias_por_sku_proveedor = defaultdict(float)
    #     for move in moves:
    #         lines = self.env['product.template'].search([
    #             '|',
    #             ('default_code', '=', move.sku),
    #             ('sku_alternos.name', 'in', [move.sku])
    #         ])
    #         if lines:
    #             for lin in lines:
    #                 if lin.es_paquete or not move.sku_interno:
    #                     continue
        
    #     for mov in moves:
    #         existencias_por_sku_proveedor[(mov.sku, proveedor)] += mov.existencia
        
    #     for (sku, proveedor), existencia_total in existencias_por_sku_proveedor.items():
    #         lines = self.env['product.template'].search([
    #             '|',
    #             ('default_code', '=', sku),
    #             ('sku_alternos.name', 'in', [sku])
    #         ])
    #         if lines:
    #             for line in lines:
    #                 if line.es_paquete or line.detailed_type != 'product':
    #                     continue
        
    #                 sku_proveedor = (line.id, proveedor)
    #                 if sku_proveedor not in sku_proveedor_procesados:
    #                     sku_moves = self.env['llantas_config.ctt_prov'].search([
    #                         ('sku', '=', sku),
    #                         ('nombre_proveedor', '=', self.name)
    #                     ])
        
    #                     tipo_cambio = 0
    #                     if sku_moves:
    #                         costo_mas_bajo = min(sku_moves.mapped('costo_sin_iva'))
    #                         filtered_moves = sku_moves.filtered(lambda x: x.costo_sin_iva == costo_mas_bajo)
    #                         tipo_cambio = filtered_moves[0].tipo_cambio if filtered_moves else 0
    #                     else:
    #                         costo_mas_bajo = 0.0
        
    #                     supplier_info = self.env['product.supplierinfo'].search([
    #                         ('product_tmpl_id', '=', line.id),
    #                         ('partner_id', '=', proveedor)
    #                     ], limit=1)
        
    #                     if supplier_info:
    #                         if (supplier_info.price == costo_mas_bajo and 
    #                             supplier_info.partner_id.id == proveedor and 
    #                             supplier_info.product_tmpl_id.id == line.id):
    #                             # Si los datos son iguales, omitir
    #                             continue
    #                         else:
    #                             if supplier_info.price != costo_mas_bajo:
    #                                 query = """
    #                                     UPDATE product_supplierinfo 
    #                                     SET 
    #                                         currency_id=%s,
    #                                         price=%s,
    #                                         ultima_actualizacion=%s,
    #                                         tipo_cambio=%s,
    #                                         precio_neto=%s,
    #                                         tipo_moneda_proveedor='MXN',
    #                                         product_code=%s,
    #                                         existencia_actual=%s
    #                                     WHERE id=%s
    #                                 """
    #                                 values = (
    #                                     moneda.id,
    #                                     costo_mas_bajo,
    #                                     fecha_actual,
    #                                     tipo_cambio,
    #                                     costo_mas_bajo,
    #                                     sku,
    #                                     existencia_total,
    #                                     supplier_info.id
    #                                 )
    #                                 self.env.cr.execute(query, values)
    #                                 count_actualizados += 1
    #                             else:
    #                                 query = """
    #                                     UPDATE product_supplierinfo 
    #                                     SET 
    #                                         existencia_actual=%s,
    #                                         ultima_actualizacion=%s
    #                                     WHERE id=%s
    #                                 """
    #                                 values = (
    #                                     existencia_total,
    #                                     fecha_actual,
    #                                     supplier_info.id
    #                                 )
    #                                 self.env.cr.execute(query, values)
    #                                 count_actualizados += 1
    #                     else:
    #                         if existencia_total == 0:
    #                             continue
    #                         query = """
    #                             INSERT INTO product_supplierinfo (partner_id, product_tmpl_id, currency_id, price, ultima_actualizacion,
    #                                                               tipo_cambio, precio_neto, tipo_moneda_proveedor, product_code, existencia_actual, delay, min_qty)
    #                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    #                         """
    #                         values = (
    #                             proveedor,
    #                             line.id,
    #                             moneda.id,
    #                             costo_mas_bajo,
    #                             fecha_actual,
    #                             tipo_cambio,
    #                             costo_mas_bajo,
    #                             'MXN',
    #                             sku,
    #                             existencia_total,
    #                             7,
    #                             1
    #                         )
    #                         self.env.cr.execute(query, values)
    #                         count_agregados += 1
    #                     sku_proveedor_procesados.add(sku_proveedor)
    #         else:
    #             count_sin_encontrar += 1
    #             mov.unlink()
        
    #     movimientos_restantes = self.env['llantas_config.ctt_prov'].search([('nombre_proveedor', '=', self.name), ('procesado', '=', False)])
    #     if not movimientos_restantes:
    #         sale_warn_msg="odos los productos han sido procesados. No hay productos pendientes por procesar."
    #         return {
    #             'warning': {
    #                 'title': _("Advertencia"),
    #                 'message': sale_warn_msg,
    #             }
    #         }
        
    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'display_notification',
    #         'params': {
    #             'type': 'success',
    #             'sticky': False,
    #             'message': f"Se actualizaron {count_actualizados} registros y se agregaron {count_agregados} nuevos registros correctamente. No se encontraron {count_sin_encontrar}.",
    #         }
    #     }
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
            # if lines:
            #     for lin in lines:
            #         if lin.es_paquete or not move.sku_interno:
            #             continue

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
                    # if line.es_paquete or line.detailed_type != 'product':
                    #     continue
                    if line.detailed_type != 'product':
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
                            if (supplier_info.price == costo_mas_bajo and 
                                supplier_info.partner_id.id == proveedor and 
                                supplier_info.product_tmpl_id.id == line.id):
                                # Si los datos son iguales, omitir
                                continue
                            else:
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
                        sku_proveedor_procesados.add(sku_proveedor)
                        
                        # Actualizar ctt_prov con el default_code y costo
                        for mov in sku_moves:
                            mov.write({
                                'procesado': True, 
                                'fecha_actualizacion': fecha_actual,
                                'sku_interno': line.default_code,
                                'costo_sin_iva': costo_mas_bajo
                            })
            else:
                count_sin_encontrar += 1
                mov.unlink()

        movimientos_restantes = self.env['llantas_config.ctt_prov'].search([('nombre_proveedor', '=', self.name), ('procesado', '=', False)])
        if not movimientos_restantes:
            sale_warn_msg="Todos los productos han sido procesados. No hay productos pendientes por procesar."
            return {
                'warning': {
                    'title': _("Advertencia"),
                    'message': sale_warn_msg,
                }
            }

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

    def name_get(self):
        res = super(killer_list, self).name_get()
        data = []
        for e in self:
            display_value = ''
            display_value += str(e.marketplace_id.name)
            display_value += ' - '
            display_value += str(e.status) or ""
            display_value += ''
            data.append((e.id, display_value))
        return data
        
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

    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        default=lambda self: self.env.company,
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


