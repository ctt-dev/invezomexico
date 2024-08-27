# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import pandas as pd
import tempfile
import base64
import logging
_logger = logging.getLogger(__name__)

class WizardImportFlightInfo(models.TransientModel):
    _name = 'adrone_config.import.flight'

    file_data = fields.Binary('Documento xlsx')
    file_name = fields.Char(string="Documento")

    def import_data(self):
        # Guarda el archivo temporalmente
        file_path = tempfile.gettempdir() + '/file.xlsx'
        data = self.file_data
        with open(file_path, 'wb') as f:
            f.write(base64.b64decode(data))

        # Leer el archivo Excel desde el campo Binary
        excel_data = pd.read_excel(file_path, sheet_name='flight record', engine='openpyxl')

        # Convertir el DataFrame a un diccionario
        excel_dict = excel_data.to_dict(orient='records')

        # Hacer algo con el diccionario (puedes imprimirlo para verificar)
        for record in excel_dict:
            # Obtén el valor asociado con la clave 'Flight time'
            time_range_str = record['Flight time']
            
            # Divide la cadena en dos partes: marca de tiempo de inicio y marca de tiempo de fin
            date_time_str, range_time_str = time_range_str.split(' ')
            start_time_str, end_time_str = range_time_str.split('-')
            
            # Convierte las cadenas de tiempo en objetos datetime
            start_time = datetime.strptime(f'{date_time_str} {start_time_str}', '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(f'{date_time_str} {end_time_str}', '%Y-%m-%d %H:%M:%S')
            try:
                record = self.env['adrone_config.flight_sheet'].create({
                    'date': start_time,
                    'flight_time': record['Flight time'],
                    'location': record['Location'],
                    'aircraft_name': record['Aircraft name'],
                    'sprayed_area': record['Sprayed area'],
                    'flight_duration': record['Flight duration(min:sec)'],
                    'crop': record['Crop'],
                    'pilot_name': record['Pliot Name'],
                    'team_name': record['Team Name'],
                    'field_name': record['Field Name'],
                    'serial_number': record['Serial Number'],
                    'start_battery': record['Starting Battery Level'],
                    'end_battery': record['Ending Battery Level'],
                })
            except:
                continue
        # Aquí puedes realizar cualquier acción adicional con los datos

        # Puedes agregar lógica adicional según tus necesidades

        return {'type': 'ir.actions.act_window_close'}