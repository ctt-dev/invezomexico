# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime
import logging
_logger = logging.getLogger(__name__)

class tipo_productos(models.Model):
    _name = 'adrone_config.flight_sheet'
    _description = 'Hoja de vuelo'
    _order = 'date desc'

    date = fields.Datetime(string='Fecha')
    flight_time = fields.Char(string='Tiempo de vuelo')
    location = fields.Char(string='Ubicación')
    aircraft_name = fields.Char(string='Aeronave')
    sprayed_area = fields.Char(string='Area recorrida')
    flight_duration = fields.Char(string='Duración de vuelo')
    crop = fields.Char(string='Cultivo')
    pilot_name = fields.Char(string='Piloto')
    team_name = fields.Char(string='Equipo')
    field_name = fields.Char(string='Campo')
    serial_number = fields.Char(string='Numero de vuelo', unique=True)
    start_battery = fields.Char(string='Nivel de batería inicial')
    end_battery = fields.Char(string='Nivel de batería final')