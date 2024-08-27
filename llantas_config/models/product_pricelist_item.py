from odoo import api, fields, models, tools, _
import logging
# import datetime
# import re
# from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
_logger = logging.getLogger(__name__)

class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    # base = fields.Selection(selection_add=[
    #     ('customize', 'Personalizado')],
    #     ondelete={'customize': 'set default'})

    compute_price = fields.Selection(
        selection_add=[
            ('customize', 'Personalizado'),
            ('marketplace', 'Marketplace'),
        ],
        ondelete={'customize': 'set default','marketplace': 'set default'}
    )

    price_shipping = fields.Float(string="Costo de envío", default=0)
    utility_perc = fields.Float(string="Margen de utilidad", default=0)
    commission_mkp = fields.Float(string="Comisión de Marketplace", default=0)

    @api.onchange('compute_price')
    def _onchange_compute_price(self):
        if self.compute_price != 'fixed':
            self.fixed_price = 0.0
        if self.compute_price != 'percentage':
            self.percent_price = 0.0
        if self.compute_price not in ['formula','customize','marketplace']:
            self.update({
                'base': 'list_price',
            })
        if self.compute_price != 'formula':
            self.update({
                'price_discount': 0.0,
                'price_surcharge': 0.0,
                'price_round': 0.0,
                'price_min_margin': 0.0,
                'price_max_margin': 0.0,
            })
        if self.compute_price != 'customize' or self.compute_price != 'marketplace':
            self.update({
                'price_shipping': 0.0,
                'utility_perc': 0.0,
                'commission_mkp': 0.0,
            })

    def _compute_price(self, product, quantity, uom, date, currency=None, costo_proveedor=0):
        # raise ValidationError(costo_proveedor)
        """Compute the unit price of a product in the context of a pricelist application.

        :param product: recordset of product (product.product/product.template)
        :param float qty: quantity of products requested (in given uom)
        :param uom: unit of measure (uom.uom record)
        :param datetime date: date to use for price computation and currency conversions
        :param currency: pricelist currency (for the specific case where self is empty)

        :returns: price according to pricelist rule, expressed in pricelist currency
        :rtype: float
        """
        product.ensure_one()
        uom.ensure_one()

        currency = currency or self.currency_id
        currency.ensure_one()

        # Pricelist specific values are specified according to product UoM
        # and must be multiplied according to the factor between uoms
        product_uom = product.uom_id
        if product_uom != uom:
            convert = lambda p: product_uom._compute_price(p, uom)
        else:
            convert = lambda p: p

        if self.compute_price == 'fixed':
            price = convert(self.fixed_price)
        elif self.compute_price == 'percentage':
            base_price = self._compute_base_price(product, quantity, uom, date, currency)
            price = (base_price - (base_price * (self.percent_price / 100))) or 0.0
        elif self.compute_price == 'formula':
            base_price = self._compute_base_price(product, quantity, uom, date, currency)
            # complete formula
            price_limit = base_price
            price = (base_price - (base_price * (self.price_discount / 100))) or 0.0
            if self.price_round:
                price = tools.float_round(price, precision_rounding=self.price_round)

            if self.price_surcharge:
                price += convert(self.price_surcharge)

            if self.price_min_margin:
                price = max(price, price_limit + convert(self.price_min_margin))

            if self.price_max_margin:
                price = min(price, price_limit + convert(self.price_max_margin))
        elif self.compute_price == 'customize':
            base_price = self._compute_base_price(product, quantity, uom, date, currency)
            
            base_price = self._compute_base_price(product, quantity, uom, date, currency)
            if costo_proveedor != 0:
                base_price = costo_proveedor
            # _logger.warning(f"Precio base: {base_price}")
            if product.es_paquete:
                try:
                    price = ((base_price * float(product.pkg_type)) + (self.price_shipping * float(product.pkg_type))) / ((100 - self.utility_perc - self.commission_mkp) / 100)
                except ValueError:
                    price = ((base_price * 1) + (self.price_shipping * 1)) / ((100 - self.utility_perc - self.commission_mkp) / 100)
            else:
                price = ((base_price * 1) + (self.price_shipping * 1)) / ((100 - self.utility_perc - self.commission_mkp) / 100)
            # price = 777.777        
        elif self.compute_price == 'marketplace':
            base_price = self._compute_base_price(product, quantity, uom, date, currency)
            if costo_proveedor != 0:
                base_price = costo_proveedor
            # _logger.warning(f"Precio base: {base_price}")
            if product.es_paquete:
                try:
                    price = ((base_price * float(product.pkg_type)) + (self.price_shipping * float(product.pkg_type))) / ((100 - self.utility_perc - self.commission_mkp) / 100)
                except ValueError:
                    price = ((base_price * 1) + (self.price_shipping * 1)) / ((100 - self.utility_perc - self.commission_mkp) / 100)
            else:
                price = ((base_price * 1) + (self.price_shipping * 1)) / ((100 - self.utility_perc - self.commission_mkp) / 100)
        else:  # empty self, or extended pricelist price computation logic
            price = self._compute_base_price(product, quantity, uom, date, currency)

        return price