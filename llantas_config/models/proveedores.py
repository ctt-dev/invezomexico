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
               
        
    def import_herrera_tires(self, record):
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
                })
        else:
            # If the product doesn't exist, create a new record
            try:
                new_record = {
                    'nombre_proveedor': self.proveedor_id.name,
                    'sku': record.get('Codigo'),
                    'producto': record.get('Titulo'),
                    'nombre_almacen': self.proveedor_id.name,
                    'existencia': record.get('Existencia'),
                    'costo_sin_iva': record.get('Costo antes de iva'),
                    'tipo_moneda': record.get('Moneda'),
                    'tipo_cambio': self.tipo_cambio,
                    'fecha_actualizacion': fecha_actual,
                }
                self.env['llantas_config.ctt_prov'].create(new_record)
            except UserError as e:
                _logger.error(f"Error creating record: {e}")
    
        return True
    
    def import_futurama(self, record):
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
                existing_record.write({'existencia': record.get(almacen_column)})
            else:
                # Si no existe, crea un nuevo registro
                try:
                    self.env['llantas_config.ctt_prov'].create({
                        'nombre_proveedor': self.proveedor_id.name,
                        'sku': record.get('CLAVE ARTICULO'),
                        'producto': record.get('DESCRIPCIÓN'),
                        'nombre_almacen': almacen_column,
                        'existencia': record.get(almacen_column),
                        'costo_sin_iva': record.get('MAYOREO'),
                        'tipo_moneda': record.get('Moneda'),
                        'tipo_cambio': self.tipo_cambio,
                        'fecha_actualizacion': fecha_actual,
                        'marca': record.get('APLICACIÓN'),
                        'aplicacion': record.get('MARCA'),
                    })
                except UserError as e:
                    _logger.error(f"Error creating record: {e}")
                    self.env.cr.rollback()
    
        return True
    
    def import_import_treads(self, record):
        fecha_actual = fields.Datetime.now()

        # Update existing records with the same SKU to update 'existencia' field
        existing_record_by_sku = self.env['llantas_config.ctt_prov'].search([
            ('sku', '=', record.get('Articulo'))
        ])

        if existing_record_by_sku:
            # If the product exists, update the 'existencia' field
            existing_record_by_sku.write({'existencia': record.get('Stock')})
        else:
            # If the product doesn't exist, create a new record
            it_trailer_usd = record.get('ITTrailerUSD')
            if isinstance(it_trailer_usd, float):
                it_trailer_usd = str(it_trailer_usd)

            it_trailer_usd_cleaned = it_trailer_usd.replace('$', '').replace(',', '').strip()

            if self.tipo_cambio > 1:
                precio = float(it_trailer_usd_cleaned)
                tipomoneda = 'USD'
            else:
                precio = float(it_trailer_usd_cleaned)
                tipomoneda = 'MXN'

            try:
                self.env['llantas_config.ctt_prov'].create({
                    'nombre_proveedor': self.proveedor_id.name,
                    'sku': record.get('Articulo'),
                    'producto': record.get('Descripción'),
                    'nombre_almacen': self.proveedor_id.name,
                    'existencia': record.get('Stock'),
                    'costo_sin_iva': precio,
                    'tipo_moneda': tipomoneda,
                    'tipo_cambio': self.tipo_cambio,
                    'fecha_actualizacion': fecha_actual,
                    'marca': record.get('Marca'),
                    'aplicacion': record.get('Segmento'),
                    'modelo': record.get('Modelo'),
                    'medida': record.get('Medida'),
                    'uso': record.get('Uso'),
                })
            except UserError as e:
                _logger.error(f"Error creating record: {e}")
                self.env.cr.rollback()

        return True

            
    def import_loyga(self, record):
        if self.tipo_cambio > 1:
            tipomoneda = 'USD'
        else:
            tipomoneda = 'MXN'
        fecha_actual = fields.Datetime.now()

        # Update existing records with the same SKU to update 'existencia' field
        existing_record_by_sku = self.env['llantas_config.ctt_prov'].search([
            ('sku', '=', record.get('CODIGO'))
        ])

        if existing_record_by_sku:
            # If the product exists, update the 'existencia' field
            existing_record_by_sku.write({'existencia': record.get('EXISTENCIA')})
        else:
            # If the product doesn't exist, create a new record
            try:
                self.env['llantas_config.ctt_prov'].create({
                    'nombre_proveedor': self.proveedor_id.name,
                    'sku': record.get('CODIGO'),
                    'producto': record.get('ARTICULO'),
                    'nombre_almacen': self.proveedor_id.name,
                    'existencia': record.get('EXISTENCIA'),
                    'costo_sin_iva': record.get('PRECIO'),
                    'tipo_moneda': tipomoneda,
                    'tipo_cambio': self.tipo_cambio,
                    'fecha_actualizacion': fecha_actual,
                    'modelo': record.get('MODELO'),
                    'marca': record.get('MARCA'),
                })
            except UserError as e:
                _logger.error(f"Error creating record: {e}")
                self.env.cr.rollback()

        return True

    def import_malpa(self, record):
        if self.tipo_cambio > 1:
            tipomoneda = 'USD'
        else:
            tipomoneda = 'MXN'
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
                existing_record.write({'existencia': record.get(almacen_column)})
            else:
                # Si no existe, crea un nuevo registro
                try:
                    self.env['llantas_config.ctt_prov'].create({
                        'nombre_proveedor': self.proveedor_id.name,
                        'sku': record.get('Producto'),
                        'producto': record.get('Descripción'),
                        'nombre_almacen': almacen_column,
                        'existencia': record.get(almacen_column),
                        'costo_sin_iva': precio_lista,
                        'precio_llantired': precio_llantired,
                        'tipo_moneda': record.get('Moneda'),
                        'tipo_cambio': self.tipo_cambio,
                        'fecha_actualizacion': fecha_actual,
                        'marca': record.get('APLICACIÓN'),
                        'aplicacion': record.get('MARCA'),
                    })
                except Exception as e:
                    # Maneja las excepciones según sea necesario
                    print(f"Error creating record: {e}")
    
        return True
    def import_new_tires(self, record):
        if self.tipo_cambio > 1:
            tipomoneda = 'USD'
        else:
            tipomoneda = 'MXN'
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
                existing_record.write({'existencia': record.get(almacen_column)})
            else:
                # Si no existe, crea un nuevo registro
                try:
                    self.env['llantas_config.ctt_prov'].create({
                        'nombre_proveedor': self.proveedor_id.name,
                        'sku': record.get('Producto'),
                        'producto': record.get('Descripción'),
                        'nombre_almacen': almacen_column,
                        'existencia': record.get(almacen_column),
                        'costo_sin_iva': record.get('MAYOREO'),
                        'tipo_moneda': record.get('Moneda'),
                        'tipo_cambio': self.tipo_cambio,
                        'fecha_actualizacion': fecha_actual,
                    })
                except UserError as e:
                    _logger.error(f"Error creating record: {e}")
                    self.env.cr.rollback()
    
        return True

    def import_radialpros(self, record):
        if self.tipo_cambio > 1:
            tipomoneda = 'USD'
        else:
            tipomoneda = 'MXN'
        it_precio_lista = record.get('PRECIO DE LISTA')

        fecha_actual = fields.Datetime.now()

        # Update existing records with the same proveedor_id.name to set 'existencia' to 0
        existing_records_same_proveedor = self.env['llantas_config.ctt_prov'].search([
            ('nombre_proveedor', '=', self.proveedor_id.name)
        ])

        for existing_record in existing_records_same_proveedor:
            existing_record.write({'existencia': 0})

        # Update existing records with the same SKU to update 'existencia' field
        existing_record_by_sku = self.env['llantas_config.ctt_prov'].search([
            ('sku', '=', record.get('SKU'))
        ])

        if existing_record_by_sku:
            # If the product exists, update the 'existencia' field
            existing_record_by_sku.write({'existencia': record.get('Stock')})
        else:
            # If the product doesn't exist, create a new record
            try:
                self.env['llantas_config.ctt_prov'].create({
                    'nombre_proveedor': self.proveedor_id.name,
                    'sku': record.get('SKU'),
                    'producto': record.get('Descripción'),
                    'nombre_almacen': record.get('Almacé n'),
                    'existencia': record.get('Stock'),
                    'costo_sin_iva': record.get('Mayoreo DLLS'),
                    'precio_promocion': record.get('PROMOCIONDLLS'),
                    'tipo_moneda': tipomoneda,
                    'tipo_cambio': self.tipo_cambio,
                    'fecha_actualizacion': fecha_actual,
                    'modelo': record.get('Modelo'),
                    'marca': record.get('Marca'),
                    'uso': record.get('Uso'),
                    'medida': record.get('medida'),
                    'aplicacion': record.get('Segmento'),
                })
            except UserError as e:
                _logger.error(f"Error creating record: {e}")
                self.env.cr.rollback()

    def convert_to_float(self, value, default=0.0):
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    def import_tbc(self, record):
        precio_lista = record.get('PRECIO DE LISTA')
        precio_cliente = record.get('PRECIO_CLIENTE')
    
        precio_lista = self.convert_to_float(precio_lista)
        precio_cliente = self.convert_to_float(precio_cliente)
    
        if self.tipo_cambio > 1:
            tipomoneda = 'USD'
        else:
            tipomoneda = 'MXN'
    
        fecha_actual = fields.Datetime.now()
    
        # Update existing records with the same proveedor_id.name to set 'existencia' to 0
        existing_records_same_proveedor = self.env['llantas_config.ctt_prov'].search([
            ('nombre_proveedor', '=', self.proveedor_id.name)
        ])
    
        for existing_record in existing_records_same_proveedor:
            existing_record.write({'existencia': 0})
    
        # Itera sobre los almacenes y actualiza la existencia para cada uno
        for almacen_column in ['LOCAL', 'GDL', 'CENTRAL']:
            # Busca el registro con el SKU y el almacén específicos
            existing_record_by_sku = self.env['llantas_config.ctt_prov'].search([
                ('sku', '=', record.get('ARTÍCULO')),
                ('nombre_almacen', '=', almacen_column)
            ], limit=1)
    
            if existing_record_by_sku:
                # Si el producto ya existe para ese SKU y almacén, actualiza la existencia
                existing_record_by_sku.write({'existencia': record.get(almacen_column)})
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
                        'costo_sin_iva': precio_cliente,
                        'tipo_moneda': record.get('Moneda'),
                        'tipo_cambio': self.tipo_cambio,
                        'fecha_actualizacion': fecha_actual,
                        'marca': record.get('MARCA'),
                    })
                except UserError as e:
                    _logger.error(f"Error creating record: {e}")
                    self.env.cr.rollback()
    
        return True
                


    def import_data(self):
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
        }
    
        import_func = switch_proveedor.get(self.proveedor_id.name)
    
        if import_func:
            # Inicia una transacción
            with self.env.cr.savepoint():
                try:
                    for _, record in excel_data.iterrows():
                        with self.env.cr.savepoint():
                            import_func(record)
                except UserError as e:
                    _logger.error(f"Error importing data: {e}")
                    # No lances un UserError aquí, solo imprime el mensaje en el log
                    # Puedes agregar más información de depuración según sea necesario
                    # continue  # Continúa con la siguiente iteración del bucle
    
        else:
            raise UserError(_("Función de importación no encontrada para el proveedor seleccionado."))
    
        return True

            
    
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
    
class ProductSupplierinfoInherited(models.Model):
    _inherit = 'product.supplierinfo'
    
    def name_get(self):
        res = super(ProductSupplierinfoInherited, self).name_get()
        data = []
        for e in self:
            display_value = ''
            display_value += str(e.partner_id.name)
            display_value += ' - $'
            display_value += str(e.price) or ""
            display_value += ' ['
            display_value += str(e.currency_id.name) or ""
            display_value += ']'
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
