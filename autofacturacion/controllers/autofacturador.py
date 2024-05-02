# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
import logging
import base64
from odoo.osv import expression
import io
from io import BytesIO
import threading
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError, ValidationError
from collections import OrderedDict
from odoo.http import request, content_disposition
from odoo.tools import ustr, osutil
from odoo.tools.misc import xlsxwriter
import webbrowser
import zipfile
import json
from urllib.request import urlretrieve
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


    @http.route(['/autofacturador/<string:order_id>'], type='http', auth="public", website=True, sitemap=False)
    def portal_my_factura_search(self, order_id, access_token=None, report_type=None, download=False, **kw):
        values = {}
        values.update({
            'order_id': order_id,
        })
        return request.render("autofacturacion.portal_auto_invoices", values)

    @http.route(['/autofacturador/error/<string:order_id>'], type='http', auth="public", website=True, sitemap=False)
    def portal_my_factura_search_error(self, order_id,error, access_token=None, report_type=None, download=False, **kw):
        values = {}
        values.update({
            'order_id': order_id,
            'error': error,
        })
        return request.render("autofacturacion.portal_auto_invoices", values)

    @http.route(['/autofacturador/xml_report/<string:invoice_id>'], type='http', auth="public", website=True, sitemap=False)
    def portal__xml_report(self, invoice_id, wizard=None, access_token=None, report_type=None, download=False, **kw):
        # model("account.edi.document"):wizard
        # create workbook object from xlsxwriter library
        
        xml = request.env['account.edi.document'].browse(invoice_id)
        xml.move_id.action_invoice_print()
        invoice_sudo = self._document_check_access('account.move', xml.move_id.id, access_token)
        pdf = self._show_report(model=invoice_sudo, report_type='pdf', report_ref='account.account_invoices', download=download)
        file_name = 'Factura-'+xml.move_id.name
        in_memory = BytesIO()
        zip_archive = zipfile.ZipFile(in_memory, "w", compression=zipfile.ZIP_DEFLATED)
        for x in invoice_sudo.attachment_ids:
            _logger.warning(x.display_name)
            if('.pdf' in x.display_name):
                zip_archive.writestr(x.display_name, base64.b64decode(x.datas))
            if('.xml' in x.display_name):
                zip_archive.writestr(x.display_name, base64.b64decode(x.datas))
                
        zip_archive.close()
        
        #Anterior creacion
        # response = request.make_response(
        #             base64.b64decode(xml.attachment_id.datas),
        #             headers=[
        #                 ('Content-Type', 'application/x-zip-compressed'),
        #                 ('Content-Disposition', content_disposition('MX-Invoice-4.0' + '.xml'))
        #             ]
        #         )
        bytes_of_zipfile = in_memory.getvalue()
        return request.make_response(bytes_of_zipfile,[('Content-Type', 'application/zip'),('Content-Disposition', 'attachment; filename=%s.zip;' % file_name)])

    @http.route(['/autofacturador/formulario/<string:order_id>'], type='http', auth="public", website=True, sitemap=False)
    def portal_my_factura_form(self, order_id, cantidad, access_token=None, report_type=None, download=False, **kw):
        values = {}
        try:
            pagos = request.env['l10n_mx_edi.payment.method'].search([])
            factura = request.env['sale.order'].search([('folio_venta', '=', '144d444'), ('amount_total', '=', 3081)])
            #factura = request.env['sale.order'].search([('id', '!=', '0')], limit=1)
            _logger.warning(factura)
            _logger.warning(request.env.company.display_name)
            _logger.warning(request.env.user.display_name)
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
    def portal_my_factura_creacion(self, order_id, razon_social, rfc, email, zip, forma_pago, cfdi, regimen, chckUser, access_token=None, report_type=None, download=False, **kw):
        values = {}
        order_ids = []
        try:
            cliente = None
            if(rfc != 'XAXX010101000'):
                cliente = request.env['res.partner'].sudo().search([('vat', '=', rfc)])
            if cliente :
                cliente.sudo().update({
                    'name' : razon_social,
                    'vat' : rfc,
                    'zip' : zip,
                    'email' : email,
                    'l10n_mx_edi_fiscal_regime' : regimen
                })
            else :
                cliente = request.env['res.partner'].sudo().create({
                    'name' : razon_social,
                    'vat' : rfc,
                    'zip' : zip,
                    'country_id' : 156,
                    'email' : email,
                    'l10n_mx_edi_fiscal_regime' : regimen
                })
            if(chckUser == 'True'):
                user = request.env['res.users'].search([('partner_id', '=', 33679)])
                acceso = False
                for rec in user:
                    if('Portal' in rec.groups_id[2].name):
                        acceso = True
                if(acceso):
                    _logger.warning('update')
                else:
                    portal_wizard = request.env['portal.wizard'].with_context(active_ids=[cliente.id]).create({})
                    portal_user = portal_wizard.user_ids
                    portal_user.email = email
                    portal_user.action_grant_access()
            factura = request.env['sale.order'].sudo().search([('folio_venta', '=', order_id)])
            if(factura.invoice_ids.edi_state == 'sent'):
                return request.redirect('/autofacturador/timbrado/'+str(order_id)) 
            factura.update({
                    'partner_id' : cliente
                })
            facturador = request.env['sale.advance.payment.inv'].sudo().create({
                'sale_order_ids' : factura,
            })
            forma_pago = request.env['l10n_mx_edi.payment.method'].sudo().search([('id', '=', forma_pago)])
            invoice = facturador.create_invoices_portal(True, forma_pago, cfdi)
            invoice_sudo = self._document_check_access('account.move', invoice.id, access_token)
            for x in invoice_sudo.attachment_ids:
                _logger.warning("attatchment")
                _logger.warning(x.display_name)
            if(invoice.state == 'posted'):
                return request.redirect('/autofacturador/timbrado/'+str(order_id))
            invoice_sudo = self._document_check_access('account.move', invoice.id, access_token)
            return self._show_report(model=invoice_sudo, report_type='pdf', report_ref='account.account_invoices', download=download)

        except (AccessError) as a:
            raise a
        except (MissingError) as e:
            raise e

    @http.route(['/autofacturador/timbrar/<string:order_id>'], type='http', auth="public", website=True)
    def portal_my_factura_timbrar(self, order_id, access_token=None, report_type=None, download=False, **kw):
        factura = request.env['sale.order'].sudo().search([('folio_venta', '=', order_id)])
        facturador = request.env['sale.advance.payment.inv'].sudo().create({
                'sale_order_ids' : factura,
            })
        
        mensaje = facturador.timbrado_factura()
        if('Código' in mensaje):
            values = {
                    'error' : mensaje,
                }
            return request.render("autofacturacion.portal_auto_invoices_error", values)
        else:
            return request.redirect(mensaje)
        
    @http.route(['/autofacturador/timbrado/<string:order_id>'], type='http', auth="public", website=True)
    def portal_my_factura_timbrado(self, order_id, access_token=None, report_type=None, download=False, **kw):
        values = {
                    'order_id' : order_id,
                }
        return request.render("autofacturacion.portal_auto_invoices_post", values)
        

