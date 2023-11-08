from odoo import models, fields, api, _
import logging
import datetime
import re
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
_logger = logging.getLogger(__name__)

class project_task_inherit(models.Model):
    _inherit = 'project.task'
    _description = 'Servicio externo'

    lugar=fields.Char(
        string="Lugar",
        tacking=True,
    )

    asignado=fields.Many2one(
        "hr.employee",
        string="Asignado a",
        company_dependent=True,
        tacking=True,
    )

    auxiliar=fields.Many2one(
        "hr.employee",
        string="Auxiliar",
        company_dependent=True,
        tacking=True,
    )

    fecha_aplicar=fields.Datetime(
        string="Fecha para aplicar",
        tacking=True,
    )

    cultivo=fields.Char(
        string="Cultivo",
        tacking=True,
    )

    hectareas=fields.Char(
        string="Hectareas por aplicar",
        tacking=True,
    )

    tipo_producto=fields.Many2one(
        "adrone_config.tipo_productos",
        string="Tipo de producto",
    )

    tipo_prod=fields.Many2many(
        "adrone_config.tipo_productos",
        # "name",
        string="Tipo producto",
        tacking=True,
    )

    volumen=fields.Char(
        string="Volumen de solucion total",
        tacking=True,
    )

    altura=fields.Char(
        string="Altura sobre cultivo",
        tacking=True,
    )

    velocidad=fields.Char(
        string="Velocidad de vuelo",
        tacking=True,
    )

    espacio_surcos=fields.Char(
        string="Espacio entre surcos",
    )