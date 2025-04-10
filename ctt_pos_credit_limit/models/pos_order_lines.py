# -*- coding: utf-8 -*-
"""Pos order"""
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Abhishek E T (Contact : odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0
#    (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the
#    Software
#    or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#    OTHERWISE,ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
#    USE OR OTHER DEALINGS IN THE SOFTWARE.
#
################################################################################

from odoo import models, api, fields

import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
_logger = logging.getLogger(__name__)
import datetime


class PosOrderLinesCreditLimit(models.Model):
    """Breaking the creation of credit payment journal"""
    _inherit = ['pos.order.line']

    # @api.model
    # def create(self, vals_list):
    #     _logger.warning(self)
    #     super(PosOrderLinesCreditLimit, self).create(vals_list)
    #     self.partner.message_post(body="Se agrego producto "+self.full_product_name,
    #               type="comment")
    @api.model
    def write(self, vals_list):
        _logger.warning(self)
        _logger.warning(vals_list)
        try:
            if vals_list['qty']:
                qty = self.qty
        except:
            _logger.warning("Error qty")
        try:
            if vals_list['price_unit']:
                price_unit = self.price_unit
        except:
            _logger.warning("Error price_unit")
        try:
            if vals_list['discount']:
                discount = self.discount
        except Exception as e:
            _logger.warning(e)
        super(PosOrderLinesCreditLimit, self).write(vals_list)
        try:
            self.order_id.message_post(body="Se modificó precio de "+self.full_product_name+" de $"+str(price_unit)+" a $"+str(self.price_unit),
                      type="comment")
        except:
            _logger.warning("Error qty")
        try:
            self.order_id.message_post(body="Se modificó la cantidad de "+self.full_product_name+" de "+str(qty)+" a "+str(self.qty),
                      type="comment")
        except:
            _logger.warning("Error price_unit")

        try:
            self.order_id.message_post(body="Se modificó el descuento de "+self.full_product_name+" de "+str(discount)+"% a "+str(self.discount)+"%",
                      type="comment")
        except:
            _logger.warning("Error discount")

