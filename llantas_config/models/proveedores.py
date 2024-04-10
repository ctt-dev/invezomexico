# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _
import logging
import datetime
import pandas as pd
import tempfile
import base64
from odoo.exceptions import Warning
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)

class WizardImportExistenciasProv(models.TransientModel):
    _name = 'llantas_config.ctt_prov_cargar_wizard'

    file_data = fields.Binary('Documento xlsx')
    file_name = fields.Char(string="Documento")

    proveedor_id = fields.Many2one(
        "llantas_config.proveedores_links",
        string="Proveedor",
    )

    tipo_cambio=fields.Float(
        string="TC a importar",
    )

    def dejar_en_cero(self):
        # Set 'existencia' to 0 for all records with the same 'nombre_proveedor'
        existing_proveedor = self.env['llantas_config.ctt_prov'].search([
            ('nombre_proveedor', '=', self.proveedor_id.name),
        ])
        existing_proveedor.write({
            'existencia': 0,
        })
        
    def llanti_bodega(self):
        count_updated = 0
        count_created = 0
        tipo_cambio = 1
        if self.tipo_cambio != 0.00:
            tipo_cambio = self.tipo_cambio
        
        fecha_actual = datetime.datetime.now()
    
        if self.proveedor_id.name == 'Llantired':
            quant_ids = self.env['stock.quant'].search([('location_id.usage','=','internal'),('company_id.name','=','LLANTIRED')])
            product_list = []
            for quant_id in quant_ids:
                if quant_id.product_id.id not in product_list:
                    product_list.append(quant_id.product_id.id)
    
            for product in product_list:
                product_id = self.env['product.product'].browse(product)
                quant_ids = self.env['stock.quant'].search([('product_id','=',product_id.id),('location_id.usage','=','internal'),('company_id.name','=','LLANTIRED')])
                quantity = 0
                for quant_id in quant_ids:
                    quantity += quant_id.quantity
                
                existing_records_same_proveedor = self.env['llantas_config.ctt_prov'].search([
                    ('nombre_proveedor', '=', self.proveedor_id.name),
                    ('sku_interno', '=', product_id.default_code),
                    ('sku', '=', product_id.default_code)
                ])
                if existing_records_same_proveedor:
                    # Update existing records with the new values
                    for existing_record in existing_records_same_proveedor:
                        existing_record.write({
                            'existencia': quantity,
                            'costo_sin_iva': product_id.standard_price,
                            'fecha_actualizacion': fecha_actual,
                        })
                        count_updated += 1
                else:
                    # If the product doesn't exist, create a new record
                    try:
                        new_record = {
                            'nombre_proveedor': self.proveedor_id.name,
                            'sku_interno': product_id.default_code,
                            'producto': product_id.name,
                            'nombre_almacen': 'Llantired',
                            'existencia': quantity,
                            'costo_sin_iva': product_id.standard_price,
                            # 'tipo_moneda': record.get('Moneda'),
                            'tipo_moneda': 'MXN',
                            'tipo_cambio': 1,
                            'fecha_actualizacion': fecha_actual,
                            'sku': product_id.default_code,
                        }
                        self.env['llantas_config.ctt_prov'].create(new_record)
                        count_created += 1
                    except UserError as e:
                        _logger.error(f"Error creating record: {e}")
            
            return {'count_updated': count_updated, 'count_created': count_created, 'message': "Archivo importado correctamente", 'proveedor': self.proveedor_id.name}


        
        elif self.proveedor_id.name == 'La bodega':
            quant_ids = self.env['stock.quant'].search([('location_id.usage','=','internal'),('company_id.name','=','LA BODEGA LLANTAS Y ACCESORIOS')])
            product_list = []
            for quant_id in quant_ids:
                if quant_id.product_id.id not in product_list:
                    product_list.append(quant_id.product_id.id)
    
            for product in product_list:
                product_id = self.env['product.product'].browse(product)
                quant_ids = self.env['stock.quant'].search([('product_id','=',product_id.id),('location_id.usage','=','internal'),('company_id.name','=','LA BODEGA LLANTAS Y ACCESORIOS')])
                quantity = 0
                for quant_id in quant_ids:
                    quantity += quant_id.quantity
                
                existing_records_same_proveedor = self.env['llantas_config.ctt_prov'].search([
                    ('nombre_proveedor', '=', self.proveedor_id.name),
                    ('sku_interno', '=', product_id.default_code),
                    ('sku', '=', product_id.default_code)
                ])
                # raise UserError(str(product_id.name)+' #'+str(quantity))
                if existing_records_same_proveedor:
                    # Update existing records with the new values
                    for existing_record in existing_records_same_proveedor:
                        existing_record.write({
                            'existencia': quantity,
                            'costo_sin_iva': product_id.standard_price,
                            'fecha_actualizacion': fecha_actual,
                        })
                        count_updated += 1
                else:
                    # If the product doesn't exist, create a new record
                    try:
                        new_record = {
                            'nombre_proveedor': self.proveedor_id.name,
                            'sku_interno': product_id.default_code,
                            'producto': product_id.name,
                            'nombre_almacen': 'Llantired',
                            'existencia': quantity,
                            'costo_sin_iva': product_id.standard_price,
                            # 'tipo_moneda': record.get('Moneda'),
                            'tipo_moneda': 'MXN',
                            'tipo_cambio': 1,
                            'fecha_actualizacion': fecha_actual,
                            'sku': product_id.default_code,
                        }
                        self.env['llantas_config.ctt_prov'].create(new_record)
                        count_created += 1
                    except UserError as e:
                        _logger.error(f"Error creating record: {e}")
            
            return {'count_updated': count_updated, 'count_created': count_created, 'message': "Archivo importado correctamente", 'proveedor': self.proveedor_id.name}
        else:
            raise UserError('Proveedor incorrecto')
               
        
    def import_herrera_tires(self, record):
        count_updated = 0
        count_created = 0
        tipo_cambio = 1
        if self.tipo_cambio != 0.00:
            tipo_cambio = self.tipo_cambio
        
        fecha_actual = datetime.datetime.now()
        
        existing_records_same_proveedor = self.env['llantas_config.ctt_prov'].search([
            ('nombre_proveedor', '=', self.proveedor_id.name),
            ('sku', '=', record.get('Codigo'))
        ])
        if existing_records_same_proveedor:
            # Update existing records with the new values
            for existing_record in existing_records_same_proveedor:
                existing_record.write({
                    'existencia': record.get('Existencia'),
                    'costo_sin_iva': record.get('Costo antes de iva') * tipo_cambio,
                    'fecha_actualizacion': fecha_actual,
                })
                count_updated += 1
        else:
            # If the product doesn't exist, create a new record
            try:
                new_record = {
                    'nombre_proveedor': self.proveedor_id.name,
                    'sku': record.get('Codigo'),
                    'producto': record.get('Titulo'),
                    'nombre_almacen': self.proveedor_id.name,
                    'existencia': record.get('Existencia'),
                    'costo_sin_iva': record.get('Costo antes de iva') * tipo_cambio,
                    # 'tipo_moneda': record.get('Moneda'),
                    'tipo_moneda': 'MXN',
                    'tipo_cambio': self.tipo_cambio,
                    'fecha_actualizacion': fecha_actual,
                }
                self.env['llantas_config.ctt_prov'].create(new_record)
                count_created += 1
            except UserError as e:
                _logger.error(f"Error creating record: {e}")
    
        return {'count_updated': count_updated, 'count_created': count_created, 'message': "Archivo importado correctamente", 'proveedor': self.proveedor_id.name}
    
    def import_futurama(self, record):
        count_updated = 0
        count_created = 0
        tipo_cambio = 1
        if self.tipo_cambio != 0.00:
            tipo_cambio = self.tipo_cambio
        fecha_actual = fields.Datetime.now()
    
        # Itera sobre los almacenes y actualiza la existencia para cada uno
        for almacen_column in ['MAT', 'VGR', 'VAL', 'IXT', 'QRT', 'GDL']:
            # Busca el registro con el SKU y el almacén específicos
            existing_record = self.env['llantas_config.ctt_prov'].search([
                ('sku', '=', record.get('CLAVE ARTICULO')),
                ('nombre_almacen', '=', almacen_column)
            ], limit=1)
    
            if existing_record:
                # Si el producto ya existe para ese SKU y almacén, actualiza la existencia
                existing_record.write({'existencia': record.get(almacen_column),'costo_sin_iva': record.get('MAYOREO') * tipo_cambio,'fecha_actualizacion': fecha_actual,})
                count_updated += 1
            else:
                # Si no existe, crea un nuevo registro
                try:
                    self.env['llantas_config.ctt_prov'].create({
                        'nombre_proveedor': self.proveedor_id.name,
                        'sku': record.get('CLAVE ARTICULO'),
                        'producto': record.get('DESCRIPCIÓN'),
                        'nombre_almacen': almacen_column,
                        'existencia': record.get(almacen_column),
                        'costo_sin_iva': record.get('MAYOREO') * tipo_cambio,
                        'tipo_moneda': 'MXN',
                        'tipo_cambio': self.tipo_cambio,
                        'fecha_actualizacion': fecha_actual,
                        'marca': record.get('APLICACIÓN'),
                        'aplicacion': record.get('MARCA'),
                    })
                    count_created += 1
                except UserError as e:
                    _logger.error(f"Error creating record: {e}")
                    self.env.cr.rollback()
    
        return {'count_updated': count_updated, 'count_created': count_created, 'message': "Archivo importado correctamente", 'proveedor': self.proveedor_id.name}
    
    def import_import_treads(self, record):
        count_updated = 0
        count_created = 0
        tipo_cambio = 1
        if self.tipo_cambio != 0.00:
            tipo_cambio = self.tipo_cambio            
        fecha_actual = fields.Datetime.now()

        # Update existing records with the same SKU to update 'existencia' field
        existing_record_by_sku = self.env['llantas_config.ctt_prov'].search([
            ('sku', '=', record.get('Articulo'))
        ])
        it_trailer_usd = record.get('ITTrailerUSD')
        if isinstance(it_trailer_usd, float):
            it_trailer_usd = str(it_trailer_usd)
        it_trailer_usd_cleaned = it_trailer_usd.replace('$', '').replace(',', '').strip()
        
        if existing_record_by_sku:
            # If the product exists, update the 'existencia' field
            existing_record_by_sku.write({'existencia': record.get('Stock'),'costo_sin_iva': float(it_trailer_usd_cleaned) * tipo_cambio,'fecha_actualizacion': fecha_actual,})
            count_updated += 1
        else:
            # If the product doesn't exist, create a new record
           

            try:
                self.env['llantas_config.ctt_prov'].create({
                    'nombre_proveedor': self.proveedor_id.name,
                    'sku': record.get('Articulo'),
                    'producto': record.get('Descripción'),
                    'nombre_almacen': self.proveedor_id.name,
                    'existencia': record.get('Stock'),
                    'costo_sin_iva': float(it_trailer_usd_cleaned) * tipo_cambio,
                    'tipo_moneda': 'MXN',
                    'tipo_cambio': self.tipo_cambio,
                    'fecha_actualizacion': fecha_actual,
                    'marca': record.get('Marca'),
                    'aplicacion': record.get('Segmento'),
                    'modelo': record.get('Modelo'),
                    'medida': record.get('Medida'),
                    'uso': record.get('Uso'),
                })
                count_created += 1
            except UserError as e:
                _logger.error(f"Error creating record: {e}")
                self.env.cr.rollback()

        return {'count_updated': count_updated, 'count_created': count_created, 'message': "Archivo importado correctamente", 'proveedor': self.proveedor_id.name}

            
    def import_loyga(self, record):
        count_updated = 0
        count_created = 0
        tipo_cambio = 1
        if self.tipo_cambio != 0.00:
            tipo_cambio = self.tipo_cambio
        fecha_actual = fields.Datetime.now()

        # Update existing records with the same SKU to update 'existencia' field
        existing_record_by_sku = self.env['llantas_config.ctt_prov'].search([
            ('sku', '=', record.get('CODIGO'))
        ])

        if existing_record_by_sku:
            # If the product exists, update the 'existencia' field
            existing_record_by_sku.write({'existencia': record.get('EXISTENCIA'), 'costo_sin_iva': record.get('PRECIO') * tipo_cambio,'fecha_actualizacion': fecha_actual,})
            count_updated += 1
        else:
            # If the product doesn't exist, create a new record
            try:
                self.env['llantas_config.ctt_prov'].create({
                    'nombre_proveedor': self.proveedor_id.name,
                    'sku': record.get('CODIGO'),
                    'producto': record.get('ARTICULO'),
                    'nombre_almacen': self.proveedor_id.name,
                    'existencia': record.get('EXISTENCIA'),
                    'costo_sin_iva': record.get('PRECIO') * tipo_cambio,
                    'tipo_moneda': 'MXN',
                    'tipo_cambio': self.tipo_cambio,
                    'fecha_actualizacion': fecha_actual,
                    'modelo': record.get('MODELO'),
                    'marca': record.get('MARCA'),
                })
                count_created += 1
            except UserError as e:
                _logger.error(f"Error creating record: {e}")
                self.env.cr.rollback()

        return {'count_updated': count_updated, 'count_created': count_created, 'message': "Archivo importado correctamente", 'proveedor': self.proveedor_id.name}

    def import_malpa(self, record):
        count_updated = 0
        count_created = 0
        tipo_cambio = 1
        if self.tipo_cambio != 0.00:
            tipo_cambio = self.tipo_cambio
        
        it_precio_lista = record.get('PRECIO DE LISTA')
        if isinstance(it_precio_lista, float):
            it_precio_lista = str(it_precio_lista)
    
        precio_lista = it_precio_lista.replace('$', '').replace(',', '').strip()
    
        it_precio_llantired = record.get('PRECIO LLANTIRED')
        if isinstance(it_precio_llantired, float):
            it_precio_llantired = str(it_precio_llantired)
    
        precio_llantired = it_precio_llantired.replace('$', '').replace(',', '').strip()
    
        fecha_actual = fields.Datetime.now()
    
        # Itera sobre los almacenes y actualiza la existencia para cada uno
        for almacen_column in ['01 HERMOSILLO', '04 NOGALES', '05 OBREGON', '06 NAVOJOA', '07 LOS MOCHIS', '10 GUADALAJARA']:
            # Busca el registro con el SKU y el almacén específicos
            existing_record = self.env['llantas_config.ctt_prov'].search([
                ('sku', '=', record.get('Producto')),
                ('nombre_almacen', '=', almacen_column)
            ], limit=1)
    
            if existing_record:
                # Si el producto ya existe para ese SKU y almacén, actualiza la existencia
                existing_record.write({'existencia': record.get(almacen_column), 'costo_sin_iva': float(precio_lista) * tipo_cambio,'fecha_actualizacion': fecha_actual,})
                count_updated += 1
            else:
                # Si no existe, crea un nuevo registro
                try:
                    self.env['llantas_config.ctt_prov'].create({
                        'nombre_proveedor': self.proveedor_id.name,
                        'sku': record.get('Producto'),
                        'producto': record.get('Descripción'),
                        'nombre_almacen': almacen_column,
                        'existencia': record.get(almacen_column),
                        'costo_sin_iva': float(precio_lista) * tipo_cambio,
                        'precio_llantired': precio_llantired,
                        'tipo_moneda': 'MXN',
                        'tipo_cambio': self.tipo_cambio,
                        'fecha_actualizacion': fecha_actual,
                        'marca': record.get('APLICACIÓN'),
                        'aplicacion': record.get('MARCA'),
                    })
                    count_created += 1
                except Exception as e:
                    # Maneja las excepciones según sea necesario
                    print(f"Error creating record: {e}")
    
        return {'count_updated': count_updated, 'count_created': count_created, 'message': "Archivo importado correctamente", 'proveedor': self.proveedor_id.name}
        
    def import_new_tires(self, record):
        count_updated = 0
        count_created = 0
        tipo_cambio = 1
        if self.tipo_cambio != 0.00:
            tipo_cambio = self.tipo_cambio
        it_precio_lista = record.get('PRECIO DE LISTA')
    
        fecha_actual = fields.Datetime.now()
    
        # Itera sobre los almacenes y actualiza la existencia para cada uno
        for almacen_column in ['1 Bodega', '2 Carmelo', '3 Muestras', '5 Calle7', '6 Piedras', '7 Cuerna', '8 Portales']:
            # Busca el registro con el SKU y el almacén específicos
            existing_record = self.env['llantas_config.ctt_prov'].search([
                ('sku', '=', record.get('Producto')),
                ('nombre_almacen', '=', almacen_column)
            ], limit=1)
    
            if existing_record:
                # Si el producto ya existe para ese SKU y almacén, actualiza la existencia
                existing_record.write({'existencia': record.get(almacen_column), 'costo_sin_iva': record.get('MAYOREO') * tipo_cambio,'fecha_actualizacion': fecha_actual,})
                count_updated += 1
            else:
                # Si no existe, crea un nuevo registro
                try:
                    self.env['llantas_config.ctt_prov'].create({
                        'nombre_proveedor': self.proveedor_id.name,
                        'sku': record.get('Producto'),
                        'producto': record.get('Descripción'),
                        'nombre_almacen': almacen_column,
                        'existencia': record.get(almacen_column),
                        'costo_sin_iva': record.get('MAYOREO') * tipo_cambio,
                        'tipo_moneda': 'MXN',
                        'tipo_cambio': self.tipo_cambio,
                        'fecha_actualizacion': fecha_actual,
                    })
                    count_created += 1
                except UserError as e:
                    _logger.error(f"Error creating record: {e}")
                    self.env.cr.rollback()
    
        return {'count_updated': count_updated, 'count_created': count_created, 'message': "Archivo importado correctamente", 'proveedor': self.proveedor_id.name}

    def import_radialpros(self, record):
        count_updated = 0
        count_created = 0
        promociones = 0
        tipo_cambio = 1
        if self.tipo_cambio != 0.00:
            tipo_cambio = self.tipo_cambio
        
        
        fecha_actual = fields.Datetime.now()
        sku = record.get('SKU')
        nombre_almacen = record.get('Almacé n')
    
        # Update existing records with the same SKU and almacen to update 'existencia' field
        existing_record = self.env['llantas_config.ctt_prov'].search([
            ('sku', '=', sku),
            ('nombre_almacen', '=', nombre_almacen),
        ])
    
        if existing_record:
            # If the product exists, update the 'existencia' field
            existing_record.write({'existencia': record.get('Stock'),'costo_sin_iva': record.get('Mayoreo DLLS') * tipo_cambio,'fecha_actualizacion': fecha_actual,})
            count_updated += 1
        else:
            if record.get('PROMOCIONDLLS'):
                promociones=record.get('PROMOCIONDLLS')
            # If the product doesn't exist, create a new record
            try:
                self.env['llantas_config.ctt_prov'].create({
                    'nombre_proveedor': self.proveedor_id.name,
                    'sku': sku,
                    'producto': record.get('Descripción'),
                    'nombre_almacen': nombre_almacen,
                    'existencia': record.get('Stock'),
                    'costo_sin_iva': record.get('Mayoreo DLLS') * tipo_cambio,
                    'precio_promocion': promociones,
                    'tipo_moneda': 'MXN',
                    'tipo_cambio': self.tipo_cambio,
                    'fecha_actualizacion': fecha_actual,
                    'modelo': record.get('Modelo'),
                    'marca': record.get('Marca'),
                    'uso': record.get('Uso'),
                    'medida': record.get('medida'),
                    'aplicacion': record.get('Segmento'),
                })
                count_created += 1
            except UserError as e:
                _logger.error(f"Error creating record: {e}")
                self.env.cr.rollback()
    
        return {'count_updated': count_updated, 'count_created': count_created, 'message': "Archivo importado correctamente", 'proveedor': self.proveedor_id.name}
    
    def convert_to_float(self, value, default=0.0):
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    def import_tbc(self, record):
        count_updated = 0
        count_created = 0
        tipo_cambio = 1
        if self.tipo_cambio != 0.00:
            tipo_cambio = self.tipo_cambio
        
        precio_lista = record.get('PRECIO DE LISTA')
        precio_cliente = record.get('PRECIO_CLIENTE')
    
        precio_lista = self.convert_to_float(precio_lista)
        precio_cliente = self.convert_to_float(precio_cliente)
    
        if self.tipo_cambio > 1:
            tipomoneda = 'USD'
        else:
            tipomoneda = 'MXN'
    
        fecha_actual = fields.Datetime.now()        
    
        # Itera sobre los almacenes y actualiza la existencia para cada uno
        for almacen_column in ['LOCAL', 'GDL', 'CENTRAL']:
            # Busca el registro con el SKU y el almacén específicos
            existing_record_by_sku = self.env['llantas_config.ctt_prov'].search([
                ('sku', '=', record.get('ARTÍCULO')),
                ('nombre_almacen', '=', almacen_column)
            ], limit=1)
    
            if existing_record_by_sku:
                # Si el producto ya existe para ese SKU y almacén, actualiza la existencia
                existing_record_by_sku.write({'existencia': record.get(almacen_column), 'costo_sin_iva': precio_cliente * tipo_cambio,'fecha_actualizacion': fecha_actual,})
                count_updated += 1
            else:
                # Si no existe, crea un nuevo registro
                try:
                    self.env['llantas_config.ctt_prov'].create({
                        'nombre_proveedor': self.proveedor_id.name,
                        'sku': record.get('ARTÍCULO'),
                        'producto': record.get('DESCRIPCIÓN'),
                        'nombre_almacen': almacen_column,
                        'existencia': record.get(almacen_column),
                        'precio_lista': precio_lista,
                        'costo_sin_iva': precio_cliente * tipo_cambio,
                        'tipo_moneda': 'MXN',
                        'tipo_cambio': self.tipo_cambio,
                        'fecha_actualizacion': fecha_actual,
                        'marca': record.get('MARCA'),
                    })
                    count_created += 1
                except UserError as e:
                    _logger.error(f"Error creating record: {e}")
                    self.env.cr.rollback()
    
        return {'count_updated': count_updated, 'count_created': count_created, 'message': "Archivo importado correctamente", 'proveedor': self.proveedor_id.name}

    def import_tersa(self, record):
        count_updated = 0
        count_created = 0
        tipo_cambio = 1
        if self.tipo_cambio != 0.00:
            tipo_cambio = self.tipo_cambio
        # Agrega un registro de log para rastrear la ejecución del código
        _logger.info(f"Importing record: {record}")


        fecha_actual = fields.Datetime.now()

        # Busca registros existentes con el mismo SKU y el mismo nombre de almacén
        existing_records = self.env['llantas_config.ctt_prov'].search([
            ('sku', '=', record.get('Columna1')),
            ('nombre_almacen', '=', record.get('Columna10'))
        ])

        if existing_records:
            # Si existen registros, actualiza el campo 'existencia' en cada uno
            for existing_record in existing_records:
                existing_record.write({'existencia': record.get('Columna12'), 'costo_sin_iva': record.get('Columna14') * tipo_cambio,'fecha_actualizacion': fecha_actual})
                count_updated += 1
        else:
            # Si no existen registros, crea uno nuevo
            try:
                self.env['llantas_config.ctt_prov'].create({
                    'nombre_proveedor': self.proveedor_id.name,
                    'sku': record.get('Columna1'),
                    'producto': record.get('Columna2'),
                    'nombre_almacen': record.get('Columna10'),
                    'existencia': record.get('Columna12'),
                    'costo_sin_iva': record.get('Columna14') * tipo_cambio,
                    'tipo_moneda': 'MXN',
                    'tipo_cambio': self.tipo_cambio,
                    'fecha_actualizacion': fecha_actual,
                    'modelo': record.get('Columna6'),
                    'marca': record.get('Columna5'),
                    'uso': record.get('Columna4'),
                    'medida': record.get('Columna3'),
                })
                count_created += 1
            except Exception as e:
                # Maneja excepciones de manera más específica y registra los detalles
                _logger.error(f"Error creating record: {e}")
                self.env.cr.rollback()

        # Agrega un registro de log con información sobre la importación
        _logger.info(f"Import summary: {count_updated} records updated, {count_created} records created")

        # Retorna un diccionario con información sobre la importación
        return {'count_updated': count_updated, 'count_created': count_created, 'message': "Archivo importado correctamente", 'proveedor': self.proveedor_id.name}

    def import_tres_siglos(self, record):
        count_updated = 0
        count_created = 0
        tipo_cambio = 1
        if self.tipo_cambio != 0.00:
            tipo_cambio = self.tipo_cambio
        
        precio_lista = record.get('Mayoreo +100pz')
        precio_cliente = record.get('Mayoreo +100pz')
    
        precio_lista = self.convert_to_float(precio_lista)
        precio_cliente = self.convert_to_float(precio_cliente)
    
        if self.tipo_cambio > 1:
            tipomoneda = 'USD'
        else:
            tipomoneda = 'MXN'
    
        fecha_actual = fields.Datetime.now()        
        
        # Itera sobre los almacenes y actualiza la existencia para cada uno
        for almacen_column in ['CENTRAL', 'MACRO CED']:
            almacen_value = record.get(almacen_column)
            if almacen_value is not None:
                almacen_value = str(almacen_value)
                almacen_value = float(almacen_value.replace('+', ''))
            else:
                almacen_value = None
    
            # Busca el registro con el SKU y el almacén específicos
            existing_record_by_sku = self.env['llantas_config.ctt_prov'].search([
                ('sku', '=', record.get('Clave')),
                ('nombre_almacen', '=', almacen_column)
            ], limit=1)
    
            if existing_record_by_sku:
                # Si el producto ya existe para ese SKU y almacén, actualiza la existencia
                existing_record_by_sku.write({'existencia': almacen_value, 'costo_sin_iva': precio_cliente * tipo_cambio,'fecha_actualizacion': fecha_actual,})
                count_updated += 1
            else:
                # Si no existe, crea un nuevo registro
                try:
                    self.env['llantas_config.ctt_prov'].create({
                        'nombre_proveedor': self.proveedor_id.name,
                        'sku': record.get('Clave'),
                        'producto': record.get('Descripción'),
                        'nombre_almacen': almacen_column,
                        'existencia': almacen_value,
                        'precio_lista': precio_lista,
                        'costo_sin_iva': precio_cliente * tipo_cambio,
                        'tipo_moneda': 'MXN',
                        'tipo_cambio': self.tipo_cambio,
                        'fecha_actualizacion': fecha_actual,
                    })
                    count_created += 1
                except UserError as e:
                    _logger.error(f"Error creating record: {e}")
                    self.env.cr.rollback()
    
        return {'count_updated': count_updated, 'count_created': count_created, 'message': "Archivo importado correctamente", 'proveedor': self.proveedor_id.name}
    
    def import_data(self):
        count_updated_total = 0
        count_created_total = 0
    
        # ... (código existente)
    
        
            
        file_path = tempfile.gettempdir() + '/file.xlsx'
        data = self.file_data
    
        with open(file_path, 'wb') as f:
            f.write(base64.b64decode(data))
    
        try:
            excel_data = pd.read_excel(file_path, engine='openpyxl')
        except ImportError:
            try:
                excel_data = pd.read_excel(file_path, engine='xlrd')
            except Exception as e:
                raise UserError(f"Error reading Excel file: {e}")
    
        switch_proveedor = {
            'Herrera tires': self.import_herrera_tires,
            'Futurama': self.import_futurama,
            'Import treads': self.import_import_treads,
            'Loyga':self.import_loyga,
            'Malpa':self.import_malpa,
            'New tires':self.import_new_tires,
            'RadialPros':self.import_radialpros,
            'Tbc': self.import_tbc,
            'Tersa':self.import_tersa,
            'Tres siglos': self.import_tres_siglos,
        }

        
    
        import_func = switch_proveedor.get(self.proveedor_id.name)
    
        if import_func:
            with self.env.cr.savepoint():
                try:
                    for _, record in excel_data.iterrows():
                        with self.env.cr.savepoint():
                            result = import_func(record)
                            count_updated_total += result.get('count_updated', 0)
                            count_created_total += result.get('count_created', 0)
                            proveedor = result.get('proveedor')
                except UserError as e:
                    _logger.error(f"Error importing data: {e}")
                    # No lances un UserError aquí, solo imprime el mensaje en el log
                    # Puedes agregar más información de depuración según sea necesario
                    # continue  # Continúa con la siguiente iteración del bucle
    
        else:
            raise UserError(_("Función de importación no encontrada para el proveedor seleccionado."))
    
        return {            
           'type': 'ir.actions.client',
           'tag': 'display_notification',            
           'params': {
               'type': 'success',                
               'sticky': False,
               'message': f"Archivo importado correctamente. Registros actualizados: {count_updated_total}, Registros creados: {count_created_total}, proveedor: {proveedor}",    
               'reload': True,  # Solicita recargar la vista actual
            }        
        }   

            
    
class ctrl_llantas(models.Model): 
    _name = "llantas_config.ctt_prov"
    _description = "Existencias proveedores"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    proveedor=fields.Many2one(
        "res.partner",
        string="Proveedor",
    )

    nombre_proveedor=fields.Char(
        # related="proveedor.name",
        string="Nombre proveedor",
        
    )
    nombre_almacen=fields.Char(
        string="Almacen",
    )
    
    almacen=fields.Many2one(
        'llantas_config.almacen',
        string="Almacen",
    )
    
    fecha_proveedor=fields.Date(
        string="Fecha validez",
    )

    fecha_actualizacion=fields.Datetime(
        string="Fecha actualizacion",
    )
    
    codigo_producto=fields.Many2one(
        "product.supplierinfo",
        string="Producto",
    )
  
    proveedor_id=fields.Char(
        related="codigo_producto.partner_id.name",
        string="Proveedor",        
    )
    
    producto=fields.Char(
        # related="codigo_producto.product_name",
        string="Nombre producto"
    )

    existencia=fields.Integer(
        string="Existencias",
    )
    
    costo_sin_iva=fields.Float(
        string="Costo",
    )

    tipo_cambio=fields.Float(
        string="Tipo de cambio"
    )

    moneda=fields.Many2one(
        "res.currency",
        string="Moneda"
    )

    tipo_moneda=fields.Char(
        string="Moneda",
    )

    sku=fields.Char(
        string="Sku",
    )

    # @api.depends('sku')
    # def compute_product_id(self):
    #     for rec in self:
    #         product = rec.env['product.product']
    #         products = rec.env['product.product'].search([('default_code','=',rec.sku)])
    #         if len(products) > 0:
    #             product = products[0]
    #         rec.product_id = product
    # product_id = fields.Many2one(
    #     'product.product',
    #     string="Producto",
    #     compute=compute_product_id
    # )

    # product_id_qty_available = fields.Float(
    #     string="Cantidad de producto",
    #     related="product_id.qty_available"
    # )

    aplicacion=fields.Char(
        string="Aplicación",
    )

    marca=fields.Char(
        string="Marca",
    )

    uso=fields.Char(
        string="Uso",
    )

    modelo=fields.Char(
        string="Modelo",
    )

    medida=fields.Char(
        string="Medida",
    )
    
    precio_llantired=fields.Float(
        string="Precio llantired",
    )

    precio_promocion=fields.Float(
        string="Precio promoción",
    )

    precio_lista=fields.Float(
        string="Precio lista",
    )

    sku_interno=fields.Char(
        string="Sku interno"
    )
    
class ProductSupplierinfoInherited(models.Model):
    _inherit = 'product.supplierinfo'
    
    def name_get(self):
        res = super(ProductSupplierinfoInherited, self).name_get()
        data = []
        
        for e in self:
            ultima_actualizacion_formateada = ""
            if e.ultima_actualizacion:
                ultima_actualizacion_formateada = e.ultima_actualizacion.strftime("%d/%m/%Y %I:%M:%S %p")
            
            display_value = ''
            display_value += str(e.partner_id.name)
            display_value += ' - $'
            display_value += str(e.price) or ""
            display_value += ' ['
            display_value += str(e.currency_id.name) or ""
            display_value += '] - '
            display_value += ' Existencia actual: '
            display_value += str(e.existencia_actual) or ""
            display_value += ' - Ultima actualización: '
            display_value += ultima_actualizacion_formateada
            data.append((e.id, display_value))
        return data


class ctrl_llantas(models.Model): 
    _name = "llantas_config.ctt_prov_cargar"
    _description = "Cargar Existencia"
    
    nombre_proveedor=fields.Char(
        string="Nombre proveedor",        
    )

    almacen_existencia=fields.Char(
        string="Almacen",
    )
    
    
    fecha_proveedor=fields.Date(
        string="Fecha validez",
    )
    

    referencia_producto=fields.Char(
        string="Producto",
    )
    

    nombre_producto=fields.Char(
        string="Nombre producto"
    )
    
    
    existencias=fields.Integer(
        string="Existencias",
    )
    
    costo_sin_iva=fields.Float(
        string="Costo",
    )

    tipo_cambio=fields.Float(
        string="Tipo de cambio"
    )

    moneda=fields.Many2one(
        "res.currency",
        string="Moneda",
    )


class ctrl_tiredirect(models.Model): 
    _name = "llantas_config.ctt_tiredirect_cargar"
    _description = "Cargar Existencia"

    clave_parte=fields.Char(
        string="Clave Parte",
    )
    
    
    description_description=fields.Char(
        string="Descripción",

    )
    

    moneda_currency=fields.Char(
        string="Moneda",

    )
    

    TC=fields.Float(
        string="Tipo de Cambio",

    )
    
    
    ES=fields.Float(
        string="ES",

    )
    
    FS=fields.Float(
        string="FS",

    )
    
    Existencia_Stock=fields.Integer(
        string="Existencias",

    )
