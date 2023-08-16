# -*- coding: utf-8 -*-

from odoo import models, fields, api
from urllib.parse import urlencode
from datetime import datetime, timedelta
from odoo.addons.ctt_mercado_libre.utils.utils import MeliApi
import json

import logging
_logger = logging.getLogger(__name__)

class MercadoLibreNotification(models.Model):
    _name = "mercadolibre.notification"
    _description = "Notificaciones en MercadoLibre"

    notification_id = fields.Char(string='Notification Id',required=True,index=True)
    application_id = fields.Char(string='Application Id', index=True)
    user_id = fields.Char(string='User Id')
    topic = fields.Char(string='Topic', index=True)
    # sent = fields.Datetime(string='Sent')
    # received = fields.Datetime(string='Received', index=True)
    resource = fields.Char(string="Resource", index=True)
    attempts = fields.Integer(string='Attempts')

    data = fields.Text()

    _sql_constraints = [
        ('unique_notification_id', 'unique(notification_id)', 'Notification Id must be unique!'),
    ]

    def _prepare_values(self, values):
        vals = {
            "notification_id": values["_id"],
            "application_id": values["application_id"],
            "user_id": values["user_id"],
            "topic": values["topic"],
            "resource": values["resource"],
            # "received": values["received"],
            # "sent": values["sent"]
        }
        if "attempts" in values:
            vals["attempts"] = values["attempts"]
        return vals

    def _process_notification(self, data=False):
        try:
            if ("_id" in data):
                if data["topic"] == "orders_v2":

                    vals = self._prepare_values(values=data)

                    params = self.env['ir.config_parameter'].sudo()
                    access_token = params.get_param('ctt_mercado_libre.mercado_libre_token')
                    api_conector = MeliApi({'access_token': access_token})
                    response = api_conector.get(path=data["resource"])
                    data = response.json()
                    vals["data"] = json.dumps(data, indent=4, sort_keys=True)
                    
                    noti = self.create(vals)
                    _logger.info("Created new ORDER notification")
        except Exception as e:
            _logger.error("Error creating notification.")
            _logger.info(e, exc_info=True)
            return {"error": "Error creating notification.", "status": "520" }
    
    def meli_notifications(self, data=False):
        return self._process_notification(data)

    def process_order_notification(self):
        _logger.warning("Procesando")