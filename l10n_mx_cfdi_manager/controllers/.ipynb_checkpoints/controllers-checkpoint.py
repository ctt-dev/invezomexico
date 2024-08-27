import logging
try:
    from BytesIO import BytesIO
except ImportError:
    from io import BytesIO
import zipfile
from datetime import datetime
from odoo import http
from odoo.http import request
from odoo.http import content_disposition
import ast

_logger = logging.getLogger(__name__)

class Binary(http.Controller):
    @http.route('/web/binary/download_document', type='http', auth="public")
    def download_document(self, tab_id, **kw):
        new_tab = ast.literal_eval(tab_id)
        attachment_ids = request.env['l10n_mx.cfdi_document'].search([('id', 'in', new_tab)])
        file_dict = [{'path':doc.xml_path, 'name':doc.attatch_name} for doc in attachment_ids]

        zip_filename = datetime.now()
        zip_filename = "CFDI - %s.zip" % zip_filename
        
        bitIO = BytesIO()
        zip_file = zipfile.ZipFile(bitIO, "w", zipfile.ZIP_DEFLATED)
        [zip_file.write(f'{file_info["path"]}/{file_info["name"]}', file_info["name"]) for file_info in file_dict]
        zip_file.close()
        
        return request.make_response(bitIO.getvalue(),
                                     headers=[('Content-Type', 'application/x-zip-compressed'),
                                              ('Content-Disposition', content_disposition(zip_filename))])