from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from collections import OrderedDict
from odoo.http import request
import logging
import zipfile
from odoo.tools.misc import xlsxwriter
from io import BytesIO
import datetime
from odoo.addons.account.controllers.portal import PortalAccount
from odoo.exceptions import ValidationError
import base64
_logger = logging.getLogger(__name__)

class PortalAccountInherit(PortalAccount):
    


    @http.route(['/my/invoices/<int:invoice_id>'], type='http', auth="public", website=True)
    def portal_my_invoice_detail(self, invoice_id, access_token=None, report_type=None, download=False, **kw):
        try:
            invoice_sudo = self._document_check_access('account.move', invoice_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            move = request.env['account.move'].sudo().search([('id', '=', invoice_id)])
            invoice_sudo = self._document_check_access('account.move', invoice_id, access_token)
            if(download):
                pdf = self._show_report(model=invoice_sudo, report_type='pdf', report_ref='account.account_invoices', download=download)
                file_name = 'Factura-'+move.name
                in_memory = BytesIO()
                zip_archive = zipfile.ZipFile(in_memory, "w", compression=zipfile.ZIP_DEFLATED)
                for x in invoice_sudo.attachment_ids:
                    _logger.warning(x.display_name)
                    if('.pdf' in x.display_name):
                        zip_archive.writestr(x.display_name, base64.b64decode(x.datas))
                    if('.xml' in x.display_name):
                        zip_archive.writestr(x.display_name, base64.b64decode(x.datas))
                        
                zip_archive.close()
                bytes_of_zipfile = in_memory.getvalue()
                return request.make_response(bytes_of_zipfile,[('Content-Type', 'application/zip'),('Content-Disposition','attachment; filename=%s.zip;' % file_name)])
            return self._show_report(model=invoice_sudo, report_type=report_type, report_ref='account.account_invoices', download=download)

        values = self._invoice_get_page_view_values(invoice_sudo, access_token, **kw)
        return request.render("account.portal_invoice_page", values)