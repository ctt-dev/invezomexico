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

    # lugar=fields.Char(
    #     string="Nombre de parcela",
    #     tracking=True,
    # )

    parcela=fields.Many2one(
        "adrone_config.parcelas",
        string="Nombre de parcela",
        tracking=True,
    )

    asignado=fields.Many2one(
        "hr.employee",
        string="Asignado a piloto",
        company_dependent=True,
        tracking=True,
    )

    auxiliar=fields.Many2one(
        "hr.employee",
        string="Auxiliar",
        company_dependent=True,
        tracking=True,
    )

    fecha_aplicar=fields.Datetime(
        string="Fecha para aplicar",
        tracking=True,
    )

    # cultivo=fields.Char(
    #     string="Cultivo",
    #     tracking=True,
    # )

    cultivo_id=fields.Many2one(
        "adrone_config.cultivos",
        string="Cultivo",
        tracking=True,
    )

    hectareas=fields.Char(
        string="Hectareas por aplicar",
        tracking=True,
    )

    tipo_producto=fields.Many2one(
        "adrone_config.tipo_productos",
        string="Tipo de producto",
    )

    tipo_prod=fields.Many2many(
        "adrone_config.tipo_productos",
        # "name",
        string="Tipo producto",
        tracking=True,
    )

    volumen=fields.Char(
        string="Volumen de solución total",
        tracking=True,
    )

    altura=fields.Char(
        string="Altura sobre cultivo",
        tracking=True,
    )

    velocidad=fields.Char(
        string="Velocidad de vuelo",
        tracking=True,
    )

    espacio_surcos=fields.Char(
        string="Espacio entre surcos",
    )

    task_sequence = fields.Char(
        string="Task Sequence",
        default=lambda self: self.env['ir.sequence'].next_by_code('project.task.sequence'),
        readonly=True,
    )

    supervisor=fields.Char(
        string="Supervisor de agrícola",
        tracking=True,
    )
    
    # hora_inicio=fields.Datetime(
    #     string="Hora de inicio",
    #     tracking=True,
    # )

    # hora_terminacion=fields.Datetime(
    #     string="Hora de terminación",
    #     tracking=True,
    # )




