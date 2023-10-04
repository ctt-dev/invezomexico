# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
import logging
from odoo.osv import expression
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError, ValidationError
from collections import OrderedDict
from odoo.http import request
_logger = logging.getLogger(__name__)


class autofacturador(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        child = partner.child_ids
        if 'pos_order_count' in counters:
            pos_order_count = request.env['pos.order'].search_count(self._get_pos_order_domain(partner,child)) \
                if request.env['pos.order'].check_access_rights('read', raise_exception=False) else 0
            values['pos_order_count'] = pos_order_count
        return values


    @http.route(['/autofacturador/<int:order_id>'], type='http', auth="public", website=True, sitemap=False)
    def portal_my_factura_search(self, order_id, access_token=None, report_type=None, download=False, **kw):
        _logger.warning("RUTAAA")
        _logger.warning(order_id)
        values = {}
        values.update({
            'order_id': order_id,
        })
        return request.render("autofacturacion.portal_auto_invoices", values)

    @http.route(['/autofacturador/error/<int:order_id>'], type='http', auth="public", website=True, sitemap=False)
    def portal_my_factura_search_error(self, order_id,error, access_token=None, report_type=None, download=False, **kw):
        _logger.warning("RUTAAA")
        _logger.warning(order_id)
        _logger.warning(error)
        values = {}
        values.update({
            'order_id': order_id,
            'error': error,
        })
        return request.render("autofacturacion.portal_auto_invoices", values)

    @http.route(['/autofacturador/formulario/<int:order_id>'], type='http', auth="public", website=True, sitemap=False)
    def portal_my_factura_form(self, order_id, cantidad, access_token=None, report_type=None, download=False, **kw):
        values = {}
        _logger.warning("FORM")
        try:
            _logger.warning(request.env.user)
            _logger.warning(request.env.company)
            pagos = request.env['l10n_mx_edi.payment.method'].search([])
            _logger.warning(pagos)
            factura = request.env['sale.order'].search([('folio_venta', '=', order_id), ('amount_total', '=', cantidad)])
            _logger.warning(order_id)
            _logger.warning(cantidad)
            if(factura):
                if(not factura['state'] == 'sale'):
                    raise ValidationError(_("La orden no ha sido confirmada"))
                values = {
                    'order_id' : order_id,
                    'cantidad' : cantidad,
                    'pagos' : pagos
                }
                return request.render("autofacturacion.portal_auto_invoices_form", values)
            else:
                return request.redirect('/autofacturador/error/'+str(order_id)+'?error=1')
        except (AccessError) as a:
            _logger.warning(a)
            return request.redirect('/autofacturador/'+str(order_id))
        except (MissingError) as e:
            _logger.warning(e)
            return request.redirect('/autofacturador/'+str(order_id))

    @http.route(['/autofacturador/facturar'], type='http', auth="public", website=True)
    def portal_my_factura_creacion(self, order_id, razon_social, rfc, email, zip, forma_pago, cfdi, regimen, access_token=None, report_type=None, download=False, **kw):
        _logger.warning("facturar")
        _logger.warning(order_id)
        _logger.warning(razon_social)
        _logger.warning(rfc)
        _logger.warning(email)
        _logger.warning(forma_pago)
        _logger.warning(cfdi)
        _logger.warning(regimen)
        values = {}
        order_ids = []
        try:
            factura = request.env['sale.order'].sudo().search([('folio_venta', '=', order_id)])
            cliente = request.env['res.partner'].sudo().search([('vat', '=', rfc)])
            if cliente :
                _logger.warning("CLiente")
                _logger.warning(cliente)
                cliente.sudo().write({
                    'name' : razon_social,
                    'vat' : rfc,
                    'zip' : zip,
                    'l10n_mx_edi_fiscal_regime' : regimen
                })
            else :
                _logger.warning("NUEVO CLIENTE")
                cliente = request.env['res.partner'].sudo().create({
                    'name' : razon_social,
                    'vat' : rfc,
                    'zip' : zip,
                    'l10n_mx_edi_fiscal_regime' : regimen
                })
                _logger.warning(cliente)
            _logger.warning(factura)
            factura.update({
                    'partner_id' : cliente
                })
            facturador = request.env['sale.advance.payment.inv'].sudo().create({
                'sale_order_ids' : factura,
            })
            invoice = facturador.create_invoices_portal(True, forma_pago, cfdi)
            invoice_sudo = self._document_check_access('account.move', invoice.id, access_token)
            return self._show_report(model=invoice_sudo, report_type='pdf', report_ref='account.account_invoices', download=download)

            
            # return request.redirect('/my/posorders/autofacturador/error/'+str(order_id)+'?error=1')
            # document_sudo = document.with_user(SUPERUSER_ID).exists()
            # if not document_sudo:
            #     raise MissingError(_("This document does not exist."))
            # try:
            #     document.check_access_rights('read')
            #     document.check_access_rule('read')
            # except AccessError:
            #     if not access_token or not document_sudo.access_token or not consteq(document_sudo.access_token, access_token):
            #         raise
        except (AccessError) as a:
            _logger.warning(a)
            return request.redirect('/autofacturador/'+str(order_id))
        except (MissingError) as e:
            _logger.warning(e)
            return request.redirect('/autofacturador/'+str(order_id))
        # _logger.warning("SAOKO")
        # _logger.warning(order_sudo)

        # if report_type in ('html', 'pdf', 'text'):
        #     return self._show_report(model=order_sudo, report_type=report_type, report_ref='account.account_invoices', download=download)

        # values = order_id
        # _logger.warning("KANEKI")
        # _logger.warning(values)

