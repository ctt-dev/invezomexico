# -*- coding: utf-8 -*-

from odoo import models, fields, api
# from urllib.parse import urlencode
from datetime import datetime, timedelta
# from odoo.addons.ctt_mercado_libre.utils.utils import MeliApi
# import json

import logging
_logger = logging.getLogger(__name__)

class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    mercadolibre_id = fields.Char(string="ID Mercado Libre")
    order_by_meli = fields.Boolean(default=False, string="Orden de Mercado Libre")
    
    def _prepare_meli_vals(self, order_json):
        partner_obj = self.env["res.partner"]
        buyer_name = "%s %s" % (order_json["buyer"]["first_name"], order_json["buyer"]["last_name"])

        partner_id = partner_obj.search([("name", "=", buyer_name)])
        if not len(partner_id):
            partner_id = partner_obj.create({"name": buyer_name})
        
        vals = {
            "mercadolibre_id": order_json["id"],
            "company_id": self.env.user.company_id.id,
            "partner_id": partner_id.id,
            "date_order": datetime.strptime(order_json["date_created"], "%Y-%m-%dT%H:%M:%S.%f%z").strftime('%Y-%m-%d %H:%M:%S'),
            "validity_date": datetime.strptime(order_json["expiration_date"], "%Y-%m-%dT%H:%M:%S.%f%z").date(),
            # "order_line": orderlines.ids
        }
        return vals

    def _create_order_lines_meli(self,items):
        orderlines = self.env["sale.order.line"]
        product_obj = self.env['product.product']
        
        for line in items:
            product_id = product_obj.search(['|',("product_tmpl_id.meli_id","=",line["item"]["id"]),("product_tmpl_id.mercadolibre_title","=",line["item"]["title"])])
            # product_id = product_obj.search([("mercadolibre_title","=",line["item"]["title"])])
            orderlines += self.env["sale.order.line"].create({
                "product_id": product_id.id,
                "name": line["item"]["title"],
                "product_uom_qty": line["quantity"],
                "price_unit": line["unit_price"],
                "order_id": self.id,
                "customer_lead": 3.0,
                "product_uom": product_id.uom_id.id
            })
    
    def mercadolibre_order_json(self, meli_data):
        order_id = meli_data["id"]
        order_json = meli_data["order_json"]

        company = self.env.user.company_id

        saleorder_obj = self.env["sale.order"]
        saleorderline_obj = self.env["sale.order.line"]
        product_obj = self.env['product.product']
        odoobot = self.env.ref('base.partner_root')
        mail_obj = self.env["mail.channel"].search([("name", "=", "MercadoLibre")])

        vals = self._prepare_meli_vals(order_json)

        if order_id:
            order_id.write(vals)
        else:
            order_id = saleorder_obj.create(vals)
            order_id._create_order_lines_meli(order_json["order_items"])

            message = "Nueva orden <b>%s</b> creada desde Mercado Libre" % (order_id.name)
            mail_obj.message_post(
                body=message,
                message_type='comment',
                subtype_xmlid='mail.mt_note',
                author_id=odoobot.id
            )
        return order_id