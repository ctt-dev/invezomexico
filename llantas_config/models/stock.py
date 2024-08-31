from odoo import models, fields, api, _
import logging
import io
import base64
import xlsxwriter
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

_logger = logging.getLogger(__name__)

class sale_order_inherit(models.Model):
    _inherit = 'stock.quant'
    _description = 'stock_quant'

    sku = fields.Char(
        string="Sku",
        related="product_tmpl_id.default_code",
    )
    
    aplicacion = fields.Char(
        string="Aplicación",
        related="product_tmpl_id.categ_id.name",
    )
    
    medida = fields.Char(
        string="Medida",
        related="product_tmpl_id.medida_llanta.name",
    )
    
    marca = fields.Char(
        string="Marca",
        related="product_tmpl_id.marca_llanta.name",
    )

    @api.depends('product_tmpl_id')
    def _compute_precio_publico(self):
        for rec in self:
            precio_publico = 0.0
            precio_may5pzs = 0.0
            precio_may100pzs = 0.0
            if rec.product_tmpl_id.standard_price != 0.0:
                precio_publico = (rec.product_tmpl_id.standard_price * 1.20) * 1.16
                precio_may5pzs = (rec.product_tmpl_id.standard_price * 1.10) * 1.16
                precio_may100pzs = (rec.product_tmpl_id.standard_price * 1.05) * 1.16
            rec.precio_publico = precio_publico
            rec.precio_may5pzs = precio_may5pzs
            rec.precio_may100pzs = precio_may100pzs

    precio_publico = fields.Float(
        string="Precio Público",
        compute="_compute_precio_publico",
        store=True,
    )

    precio_may5pzs = fields.Float(
        string="Precio Mayoreo +5 Pzas",
        compute="_compute_precio_publico",
        store=True,
    )

    precio_may100pzs = fields.Float(
        string="Precio Mayoreo +100 Pzas",
        compute="_compute_precio_publico",
        store=True,
    )

    almacen_name = fields.Char(
        string="Almacén",
        related="warehouse_id.name",
        store=True,
    )

class StockQuantWizard(models.TransientModel):
    _name = 'stock.quant.wizard'
    _description = 'Wizard para agrupar almacen_name y exportar a Excel y PDF'

    almacen_name_ids = fields.Many2many(
        'stock.warehouse', 
        string='Almacenes',
        help="Selecciona los almacenes para incluir en la exportación"
    )

    ocultar_en_cero = fields.Boolean(
        string="Ocultar precios en 0",
        default=True,
    )

    def _get_current_company(self):
        """Obtiene la empresa activa en la sesión actual."""
        return self.env.company

    def _get_grouped_stock_quants(self):
        """Agrupa los quants por SKU y almacén, sumando las cantidades."""
        stock_quants = self.env['stock.quant'].search([('warehouse_id', 'in', self.almacen_name_ids.ids)])
        grouped_data = {}

        for quant in stock_quants:
            key = (quant.sku, quant.warehouse_id.id)
            if key in grouped_data:
                grouped_data[key]['available_quantity'] += quant.available_quantity
            else:
                grouped_data[key] = {
                    'product_id': quant.product_id.name,
                    'aplicacion': quant.aplicacion,
                    'medida': quant.medida,
                    'marca': quant.marca,
                    'available_quantity': quant.available_quantity,
                    'precio_publico': quant.precio_publico,
                    'precio_may5pzs': quant.precio_may5pzs,
                    'precio_may100pzs': quant.precio_may100pzs,
                }
        return grouped_data

    def export_to_excel(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Lista de Precios')
        
        # Configuración de formato
        bold = workbook.add_format({'bold': True, 'align': 'center'})
        red_bold = workbook.add_format({'bold': True, 'color': 'red'})
        center = workbook.add_format({'align': 'center'})
        orange_bg = workbook.add_format({'bg_color': '#FFA500', 'align': 'center'})
        
        # Obtener la empresa actual
        company = self._get_current_company()
        logo = company.logo  # Obtener el logo binario de la empresa actual
        
        if logo:
            logo_image = io.BytesIO(base64.b64decode(logo))
            worksheet.insert_image('G1', 'logo.png', {'image_data': logo_image, 'x_scale': 0.5, 'y_scale': 0.5})
        
        # Añadir las notas importantes
        worksheet.merge_range('A1:F1', '::: NOTA IMPORTANTE :::', center)
        worksheet.merge_range('A2:F2', 'UNICAMENTE SE MUESTRA LA DISPONIBILIDAD PARA LA VENTA', bold)
        worksheet.merge_range('A3:F3', 'LOS PRECIOS INCLUYEN I.V.A', center)
        worksheet.merge_range('A4:F4', 'LOS PRECIOS SE ENCUENTRAN SUJETOS A CAMBIOS SIN PREVIO AVISO', center)
        worksheet.merge_range('A5:F5', 'UNA VEZ SALIDA LA MERCANCIA NO SE ACEPTAN DEVOLUCIONES', red_bold)
        
        # Obtener la fecha en formato corto (ej. 15/07/2024)
        today_str = datetime.today().strftime('%d/%m/%Y')
        
        # Añadir la fecha
        worksheet.write('A6', 'Fecha', center)
        worksheet.write('B6', today_str, orange_bg)
    
        # Ajustar el ancho de la columna B (Producto) a 85
        worksheet.set_column('A:A', 15)
        worksheet.set_column('C:K', 15)
        
        # Encabezados con campos de precios al final
        headers = ['SKU', 'Producto', 'Aplicación', 'Medida', 'Marca'] + [almacen.name for almacen in self.almacen_name_ids] + ['Precio Público', 'Precio +5 Pzas', 'Precio +100 Pzas']
        worksheet.write_row(7, 0, headers)  # Cambié la fila a la 7 (FILA 8), para evitar que las notas solapen los encabezados
        
        # Obtener datos agrupados y ordenados por 'medida'
        grouped_data = self._get_grouped_stock_quants()
    
        # Inicializar estructura para acumulación de cantidades por SKU
        consolidated_data = {}
    
        for sku, data_dict in grouped_data.items():
            if sku[0] not in consolidated_data:
                consolidated_data[sku[0]] = {
                    'product_id': data_dict['product_id'],
                    'aplicacion': data_dict['aplicacion'],
                    'medida': data_dict['medida'],
                    'marca': data_dict['marca'],
                    'almacenes': {almacen.id: 0 for almacen in self.almacen_name_ids},
                    'precios': {
                        'precio_publico': data_dict['precio_publico'],
                        'precio_may5pzs': data_dict['precio_may5pzs'],
                        'precio_may100pzs': data_dict['precio_may100pzs'],
                    }
                }
            consolidated_data[sku[0]]['almacenes'][sku[1]] += data_dict['available_quantity']
    
        row = 8  # Cambié el inicio de los datos a la fila 9
        for sku, data in consolidated_data.items():
            row_data = [
                sku,  # SKU
                data['product_id'],
                data['aplicacion'],
                data['medida'],
                data['marca'],
            ]
            for almacen in self.almacen_name_ids:
                cantidad = data['almacenes'].get(almacen.id, 0)  # Obtener la cantidad o 0 si no existe
                row_data.append(cantidad)
            
            # Agregar los precios al final
            precios = [
                f'{data["precios"]["precio_publico"]:.2f}',
                f'{data["precios"]["precio_may5pzs"]:.2f}',
                f'{data["precios"]["precio_may100pzs"]:.2f}',
            ]
            
            if self.ocultar_en_cero:
                precios = [precio if float(precio) != 0 else '' for precio in precios]
            
            row_data += precios
            
            worksheet.write_row(row, 0, row_data)
            row += 1
    
        # Ajustar el ancho de las columnas
        worksheet.set_column('B:B', 70)  # Ancho de columna para 'Producto'
        
        workbook.close()
        output.seek(0)
        
        attachment = self.env['ir.attachment'].create({
            'name': 'Lista_de_Precios.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.getvalue()),
            'res_model': 'stock.quant.wizard',
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }


    def export_to_pdf(self):
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=landscape(letter))
        
        # Configuración del estilo para la tabla
        styles = getSampleStyleSheet()
        style_table = styles['Table']
        style_table.fontName = 'Helvetica'
        style_table.fontSize = 10
        style_table.alignment = 1
        style_table.textColor = colors.black
        
        # Obtener la empresa actual
        company = self._get_current_company()
        logo = company.logo  # Obtener el logo binario de la empresa actual
        
        if logo:
            logo_image = io.BytesIO(base64.b64decode(logo))
        
        # Obtener datos agrupados
        grouped_data = self._get_grouped_stock_quants()
        
        data = []
        data.append(['SKU', 'Producto', 'Aplicación', 'Medida', 'Marca'] + [almacen.name for almacen in self.almacen_name_ids] + ['Precio Público', 'Precio +5 Pzas', 'Precio +100 Pzas'])
        
        for sku, data_dict in grouped_data.items():
            row_data = [
                sku,  # SKU
                data_dict['product_id'],
                data_dict['aplicacion'],
                data_dict['medida'],
                data_dict['marca'],
            ]
            for almacen in self.almacen_name_ids:
                cantidad = grouped_data.get((sku, almacen.id), 0)  # Obtener la cantidad o 0 si no existe
                row_data.append(cantidad)
            
            precios = [
                f'{data_dict["precio_publico"]:.2f}',
                f'{data_dict["precio_may5pzs"]:.2f}',
                f'{data_dict["precio_may100pzs"]:.2f}',
            ]
            
            if self.ocultar_en_cero:
                precios = [precio if float(precio) != 0 else '' for precio in precios]
            
            row_data += precios
            data.append(row_data)
        
        table = Table(data, colWidths=[1.2*inch]*5 + [0.8*inch]*len(self.almacen_name_ids) + [1.2*inch]*3)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements = []
        if logo:
            logo_image.seek(0)
            img = Image(logo_image)
            img.drawHeight = 1.5 * inch
            img.drawWidth = 1.5 * inch
            elements.append(img)
        
        elements.append(table)
        
        doc.build(elements)
        output.seek(0)
        
        attachment = self.env['ir.attachment'].create({
            'name': 'Lista_de_Precios.pdf',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'mimetype': 'application/pdf',
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/{}?download=true'.format(attachment.id),
            'target': 'new',
        }


            
class sale_order_inherit(models.Model):
    _inherit = 'stock.picking'
    _description='stock_picking'

    carrier=fields.Char(
        string="Carrier",
        related="sale_id.llantas_config_carrier_id.name",
        readonly=True,
    )

    no_venta=fields.Char(
        related="sale_id.folio_venta",
        string="No. Venta",
        tracking=True,
    )

    marketplace=fields.Char(
        related="sale_id.marketplace.name",
        string="Marketplace",
        tracking=True,
    )

    no_recoleccion=fields.Char(
        string="No. Recoleccion",
        tracking=True,
        
    )

    link_guia=fields.Char(
        string="Link guia",
        related="sale_id.link_guia",
        readonly=True,
    )

    tdp=fields.Char(
        string="Referencia de compra (TDP)",
        related="purchase_id.partner_ref",
    )

    fecha_entrega=fields.Date(
        string="Fecha entrega",
        tracking=True
    )

    carrier_tracking_ref=fields.Char(
        string="Guia de rastreo",
        related="sale_id.guia",
        readonly=True,
    )

    # carrier_id=fields.Many2one(
    #     "llantas_config.carrier",
    #     string="Carrier",
    # )

    
    
            

    # def _compute_rastreador(self):
    #     for rec in self:
    #         carriers = self.env['llantas_config.carrier'].search([('is_trackeable', '=', True)])
    #         link = ''
    #         if carriers:
    #             for carrier in carriers:
    #                 if carrier.name == 'DHL':
    #                     link = 'https://www.dhl.com/mx-es/home/rastreo.html?tracking-id=' + str(rec.carrier_tracking_ref) + '&submit=1'
    #                 elif carrier.name == 'FEDEX':
    #                     link = 'https://www.fedex.com/wtrk/track/?action=track&trackingnumber=' + str(rec.carrier_tracking_ref) + '&cntry_code=mx&locale=es_mx'
    #                 else:
    #                     link = str(carrier.url) + str(rec.carrier_tracking_ref)

    #             rec.rastreador = link
    # rastreador = fields.Char(
    #     string="Guía", 
    #     compute="_compute_rastreador", 
    #     readonly=True
    # )
    