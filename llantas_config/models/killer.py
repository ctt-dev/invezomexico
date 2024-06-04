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

class WizardImportlistadokillers(models.TransientModel):
    _name = 'llantas_config.wizard_killer_list'

    file_data = fields.Binary('Documento xlsx')
    file_name = fields.Char(string="Documento")

    marketplace_id = fields.Many2one(
        "llantas_config.marketplaces",
        string="Marketplace",
    )
    
    def import_data_killer(self):
        count_updated_total = 0
        count_created_total = 0
        
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
    
        with self.env.cr.savepoint():
            try:
                for _, record in excel_data.iterrows():
                    with self.env.cr.savepoint():
                        count_updated, count_created = 0, 0
                        fecha_actual = datetime.datetime.now()
    
                        # Convertir fecha final a objeto datetime
                        fecha_str = record.get('fecha final')
                        if isinstance(fecha_str, pd.Timestamp):
                            fecha_str = fecha_str.strftime('%d/%m/%Y')
                        fecha_obj = datetime.datetime.strptime(fecha_str, '%d/%m/%Y')
    
                        # Determinar el estatus basado en la fecha
                        if fecha_obj > fecha_actual:
                            estatus = 'active'
                        else:
                            estatus = 'expired'
    
                        # Buscar registros existentes en killer_list
                        existing_records_same_marketplace = self.env['llantas_config.killer_list'].search([
                            ('sku', '=', record.get('sku')),
                            ('marketplace_id', '=', self.marketplace_id.id),
                            ('final_date', '=', fecha_obj.strftime('%Y-%m-%d')),
                        ])
    
                        if existing_records_same_marketplace:
                            # Actualizar los registros existentes
                            for existing_record in existing_records_same_marketplace:
                                existing_record.write({
                                    'killer_price': record.get('precio killer'),
                                    'status': estatus,
                                })
                                count_updated += 1
                        else:
                            # Buscar en killer_no_product y omitir si ya existe
                            existing_no_product_records = self.env['llantas_config.killer_no_product'].search([
                                ('sku', '=', record.get('sku')),
                                ('marketplace_id', '=', self.marketplace_id.id),
                                ('final_date', '=', fecha_obj.strftime('%Y-%m-%d')),
                            ])
                            if existing_no_product_records:
                                continue
    
                            # Crear nuevos registros si no existen en killer_list ni en killer_no_product
                            try:
                                marketplaces = self.env['llantas_config.marketplaces'].search([('name', 'ilike', record.get('marketplace'))], limit=1)
                                if marketplaces:
                                    products = self.env['product.template'].search(['|', ('default_code', '=', record.get('sku')), ('name', '=', record.get('producto'))])
                                    if products:
                                        for product in products:
                                            new_record = {
                                                'product_id': product.id,
                                                'killer_price': record.get('precio killer'),
                                                'marketplace_id': self.marketplace_id.id,
                                                'sku': record.get('sku'),
                                                'final_date': fecha_obj.strftime('%Y-%m-%d'),
                                                'status': estatus,
                                            }
                                            killer_id = self.env['llantas_config.killer_list'].create(new_record)
                                            product.write({
                                                'is_killer': True,
                                                'killer_date': fecha_obj.strftime('%Y-%m-%d'),
                                                'killer_price': record.get('precio killer'),
                                                'killer_id': killer_id.id,
                                            })
                                            count_created += 1
                                    else:
                                        new_record2 = {
                                            'product': record.get('producto'),
                                            'killer_price': record.get('precio killer'),
                                            'marketplace_id': self.marketplace_id.id,
                                            'sku': record.get('sku'),
                                            'final_date': fecha_obj.strftime('%Y-%m-%d'),
                                        }
                                        self.env['llantas_config.killer_no_product'].create(new_record2)
                                else:
                                    raise UserError('Marketplace no encontrado, favor de revisar el nombre del proveedor seleccionado')
                            except UserError as e:
                                _logger.error(f"Error creating record: {e}")
    
                        count_updated_total += count_updated
                        count_created_total += count_created
            except UserError as e:
                _logger.error(f"Error importing data: {e}")
    
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vista detallada',
            'res_model': 'llantas_config.killer_list',
            'view_mode': 'tree',
            'context': {'search_default_active_filter': 1},
            'target': 'main',
            'view_id': self.env.ref('llantas_config.view_llantas_list_killer_tree').id,
        }


