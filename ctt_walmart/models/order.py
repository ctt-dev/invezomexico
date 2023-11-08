# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json
from datetime import datetime, timedelta
from odoo.addons.ctt_walmart.utils.WalmartAPI import WalmartAPI
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    mkt_id = fields.Char(string="ID")
    data = fields.Text(string="data")

    def _prepare_walmart_vals(self, order_json):
        partner_obj = self.env["res.partner"]
        buyer_name = order_json["billingInfo"]["postalAddress"]["name"]

        partner_id = partner_obj.search([("name", "=", buyer_name)])
        if not len(partner_id):
            partner_id = partner_obj.create({"name": buyer_name})
        
        vals = {
            "marketplace_id": order_json["purchaseOrderId"],
            "company_id": self.env.user.company_id.id,
            "partner_id": partner_id.id,
            "date_order": datetime.strptime(order_json["orderDate"], "%Y-%m-%dT%H:%M:%S.%f%z").strftime('%Y-%m-%d %H:%M:%S'),
        }
        return vals

    def _create_order_lines_walmart(self,order_lines):
        orderlines = self.env["sale.order.line"]
        product_obj = self.env['product.product']
        
        for line in order_lines:
            try:
                product_id = product_obj.search(['|',("product_tmpl_id.name","=",line["item"]["productName"]),("product_tmpl_id.marketplace_template_ids.marketplace_title","=",line["item"]["productName"])])
                orderlines += self.env["sale.order.line"].create({
                    "product_id": product_id.id,
                    "name": line["item"]["productName"],
                    "product_uom_qty": line["orderLineQuantity"]["amount"],
                    "price_unit": line["item"]["unitPrice"]["amount"],
                    "order_id": self.id,
                    "customer_lead": 3.0,
                    "product_uom": product_id.uom_id.id
                })
            except Exception as e:
            _logger.warning(f"Ocurrió un error al crear linea de orden: {e}")

    def search_new_orders(self):
        _logger.warning(f"Buscando ordenes")
        #Inicializar Clinte de Walmart
        params = self.env['ir.config_parameter'].sudo()
        client_id = params.get_param('ctt_walmart.walmart_client_id')
        client_secret = params.get_param('ctt_walmart.walmart_client_secret')

        api_client = WalmartAPI(client_id, client_secret)

        url = f"orders" #Endpoint

        params = {
            "statusCodeFilter": "Created",
        }

        try:
            response = api_client.send_request("GET", url, params=params) #Request GET

            for order in response["order"]:
                order_existing = self.search_count([('marketplace_id', '=', order['purchaseOrderId'])])

                if not order_existing:
                    _logger.warning(f"Orden no existen en DB")
                    saleorder_obj = self.env["sale.order"]
                    odoobot = self.env.ref('base.partner_root')
                    mail_obj = self.env.ref('ctt_walmart.walmart_channel')

                    vals = saleorder_obj._prepare_walmart_vals(order)

                    order_id = saleorder_obj.create(vals)
                    order_id._create_order_lines_walmart(order["orderLines"])

                    message = "Nueva orden <b>%s</b> creada desde Walmart" % (order_id.name)
                    mail_obj.message_post(
                        body=message,
                        message_type='comment',
                        subtype_xmlid='mail.mt_note',
                        author_id=odoobot.id
                    )

        except Exception as e:
            _logger.warning(f"Ocurrió un error inesperado: {e}")