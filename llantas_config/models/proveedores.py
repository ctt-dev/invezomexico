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

class WizardImportexistenciasprov(models.TransientModel):
    _name = 'llantas_config.ctt_prov_cargar_wizard'

    file_data = fields.Binary('Documento xlsx')
    file_name = fields.Char(string="Documento")

    def import_data(self):
        # Guarda el archivo temporalmente
        file_path = tempfile.gettempdir() + '/file.xlsx'
        data = self.file_data
        with open(file_path, 'wb') as f:
            f.write(base64.b64decode(data))

        # Imprimir los nombres de las hojas disponibles
        excel_sheets = pd.ExcelFile(file_path).sheet_names
        _logger.info(f"Available sheets: {excel_sheets}")
        
        # Intentar leer los datos desde la primera hoja
        excel_data = pd.read_excel(file_path, sheet_name=excel_sheets[0], engine='openpyxl')
        # Leer el archivo Excel desde el campo Binary

        # Convertir el DataFrame a un diccionario
        excel_dict = excel_data.to_dict(orient='records')

        # Hacer algo con el diccionario (puedes imprimirlo para verificar)
        for record in excel_dict:
            # Convierte las cadenas de tiempo en objetos datetime
            fecha_actual = datetime.datetime.now()
            existencias = self.env['llantas_config.ctt_prov'].search([('sku','=',record['Codigo']), ('nombre_proveedor','=',record['Proveedor'])])
            if len(existencias) == 0:
                try:
                    record = self.env['llantas_config.ctt_prov'].create({
                        'nombre_proveedor': record['Proveedor'],
                        'sku': record['Codigo'],
                        'producto': record['NombreArticulo'],
                        'nombre_almacen': record['almacen'],
                        'existencia': record['Existencia'],
                        'costo_sin_iva': record['Costo Antes de Iva'],
                        'moneda': record['moneda'],
                        'tipo_cambio': record['tipo cambio'],
                        'fecha_actualizacion': fecha_actual,
                     })
                except Exception as e:
                    _logger.error(f"Error: {e}")
                    self.env.cr.rollback()  # Intenta revertir la transacción para evitar problemas posteriores
                    return {'type': 'ir.actions.client', 'tag': 'reload'}
                    continue
            else:
                for existe in existencias:
                    try:
                        existe.write({
                            'sku': record['Codigo'],
                            'almacen': record['almacen'],
                            'existencia': record['Existencia'],
                            'costo_sin_iva': record['Costo Antes de Iva'],
                            'moneda': record['moneda'],
                            'tipo_cambio': record['tipo cambio'],
                            'fecha_actualizacion': fecha_actual,
                         })
                    except Exception as e:
                        _logger.error(f"Error: {e}")
                        self.env.cr.rollback()  # Intenta revertir la transacción para evitar problemas posteriores
                        return {'type': 'ir.actions.client', 'tag': 'reload'}
                        continue

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
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
        string="Moneda",
    )

    sku=fields.Char(
        string="Sku",
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
