# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
import logging
import base64
from odoo.osv import expression
import io
import threading
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError, ValidationError
from collections import OrderedDict
from odoo.http import request, content_disposition
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

    @http.route(['/autofacturador/xml_report/<model("account.edi.document"):wizard>'], type='http', auth="public", website=True, sitemap=False)
    def portal__xml_report(self, wizard=None, access_token=None, report_type=None, download=False, **kw):
        _logger.warning("descar")
        # create workbook object from xlsxwriter library
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        _logger.warning(wizard.edi_content)
        workbook.close()
        output.seek(0)
        response.stream.write()
        output.close()
        response = request.make_response(
                    base64.encodestring(wizard.edi_content),
                    headers=[
                        ('Content-Type', 'application/vnd.ms-excel'),
                        ('Content-Disposition', content_disposition('MX-Invoice-4.0' + '.xml'))
                    ]
                )
        return response

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
        values = {}
        order_ids = []
        try:
            factura = request.env['sale.order'].sudo().search([('folio_venta', '=', order_id)])
            cliente = request.env['res.partner'].sudo().search([('vat', '=', rfc)])
            if cliente :
                cliente.sudo().update({
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
            factura.update({
                    'partner_id' : cliente
                })
            facturador = request.env['sale.advance.payment.inv'].sudo().create({
                'sale_order_ids' : factura,
            })
            forma_pago = request.env['l10n_mx_edi.payment.method'].sudo().search([('id', '=', forma_pago)])
            invoice = facturador.create_invoices_portal(True, forma_pago, cfdi)
            _logger.warning("factura check")
            _logger.warning(invoice.state)
            if(invoice.state == 'posted'):
                return request.redirect('/autofacturador/timbrado/'+str(order_id))
            invoice_sudo = self._document_check_access('account.move', invoice.id, access_token)
            return self._show_report(model=invoice_sudo, report_type='pdf', report_ref='account.account_invoices', download=download)

        except (AccessError) as a:
            _logger.warning(a)
            raise AccessError(_(a))
        except (MissingError) as e:
            raise AccessError(_(e))

    @http.route(['/autofacturador/timbrar/<int:order_id>'], type='http', auth="public", website=True)
    def portal_my_factura_timbrar(self, order_id, access_token=None, report_type=None, download=False, **kw):
        _logger.warning("TIMRBADO2")
        factura = request.env['sale.order'].sudo().search([('folio_venta', '=', order_id)])
        facturador = request.env['sale.advance.payment.inv'].sudo().create({
                'sale_order_ids' : factura,
            })
        
        mensaje = facturador.timbrado_factura()
        _logger.warning(mensaje)
        if(mensaje.find('Code : 301') == 1):
            values = {
                    'error' : error,
                    
                }
            return request.render("autofacturacion.portal_auto_invoices_error", values)
        invoice_sudo = self._document_check_access('account.move', factura.invoice_ids.id, access_token)
        return self._show_report(model=invoice_sudo, report_type='pdf', report_ref='account.account_invoices', download=download)
        
    @http.route(['/autofacturador/timbrado/<int:order_id>'], type='http', auth="public", website=True)
    def portal_my_factura_timbrado(self, order_id, access_token=None, report_type=None, download=False, **kw):
        values = {
                    'order_id' : order_id,
                }
        return request.render("autofacturacion.portal_auto_invoices_post", values)
        

