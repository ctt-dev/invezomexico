# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import tempfile
import os
from lxml import etree
import xml.etree.ElementTree as ET
from odoo.addons.ctt_walmart.utils.WalmartAPI import WalmartAPI
import logging
_logger = logging.getLogger(__name__)

class MarketplaceProductTemplate(models.Model):
    _inherit = 'marketplaces.template'

    walmart_feed_id = fields.Many2one('walmart.feed', string='Feed')
    walmart_status_feed = fields.Selection(related='walmart_feed_id.status')

    def _process_template(self):
        params = self.env['ir.config_parameter'].sudo()
        base_url = params.get_param('web.base.url')
        image_url_1920 = base_url + '/web/image?' + 'model=product.template&id=' + str(self.product_id.id) + '&field=image_1920'
        
        root = ET.Element("MPItemFeed", xmlns="http://walmart.com/")
    
        # MPItemFeedHeader
        feed_header = ET.SubElement(root, "MPItemFeedHeader")
        ET.SubElement(feed_header, "version").text = "3.2"
        ET.SubElement(feed_header, "mart").text = "WALMART_MEXICO"
        ET.SubElement(feed_header, "locale").text = "es_MX"
    
        # MPItem
        mp_item = ET.SubElement(root, "MPItem")
        ET.SubElement(mp_item, "processMode").text = "CREATE"
        #SKU
        for line in self.field_lines:
            if line.field_id.complex_type == "MPItem":
                if line.field_id.name == "sku":
                    ET.SubElement(mp_item, "sku").text = line.value
        
        # Product Identifiers
        mp_item_productIdentifiers = ET.SubElement(mp_item, "productIdentifiers")
        productIdentifier = ET.SubElement(mp_item_productIdentifiers, "productIdentifier")           
        for line in self.field_lines:
            if line.field_id.complex_type == "MPItem":
                if line.field_id.name == "productIdType":
                    ET.SubElement(productIdentifier, "productIdType").text = line.value
                elif line.field_id.name == "productId":
                    ET.SubElement(productIdentifier, "productId").text = line.value
    
        # MPProduct
        mp_product = ET.SubElement(mp_item, "MPProduct")
        ET.SubElement(mp_product, "productName").text = self.marketplace_title
    
        # Category
        mp_product_category = ET.SubElement(mp_product, "category")
        mp_product_category_vehicle = ET.SubElement(mp_product_category, "Vehicle")
        mp_product_category_vehicle_tires = ET.SubElement(mp_product_category_vehicle, "Tires")

        #Description
        ET.SubElement(mp_product_category_vehicle_tires, "shortDescription").text = self.marketplace_description
    
        # Categ Fields
        for line in self.attr_lines:
            attr_tag = ET.SubElement(mp_product_category_vehicle_tires, line.attr_id.name)
            if line.attr_id.type == "string":
                if line.attr_id.name == "keyFeatures":
                    keyFeatures = line.value.split(";")
                    for feature in keyFeatures:
                        ET.SubElement(attr_tag, "keyFeaturesValue").text = feature
                elif line.attr_id.name == "mainImageUrl":
                    attr_tag.text = image_url_1920
                elif line.attr_id.name == "productSecondaryImageURL":
                    for image in self.product_id.product_template_image_ids:
                        ET.SubElement(attr_tag, "productSecondaryImageURLValue").text = f"{base_url}/web/image?model=product.image&id={str(image.id)}&field=image_1920"
                else:
                    attr_tag.text = line.value
            
            else:
                values = line.value.split(" ")
                ET.SubElement(attr_tag, "measure").text = values[0]
                ET.SubElement(attr_tag, "unit").text = values[1]
    
        # MPOffer
        mp_offer = ET.SubElement(mp_item, "MPOffer")
    
        # MPOffer Fields
        for line in self.field_lines:
            if line.field_id.complex_type == "MPOffer":
                field_tag = ET.SubElement(mp_offer, line.field_id.name)
                if  line.field_id.type == "string":
                    field_tag.text = line.value
                else:
                    values = line.value.split(" ")
                    ET.SubElement(field_tag, "measure").text = values[0]
                    ET.SubElement(field_tag, "unit").text = values[1]
    
        return root
    
    def publish_walmart_item(self):
        # self.ensure_one()
        # Obtener la estructura XML
        xml_root = self._process_template()
        
        # Convertir la estructura XML en una cadena
        xml_string = ET.tostring(xml_root, encoding="utf-8")

        # Obtiene la ruta del directorio actual donde se encuentra product.py
        current_directory = os.path.dirname(os.path.abspath(__file__))

        # Guardar el XML en un archivo (opcional)
        with open(os.path.join(current_directory, "ejemplo.xml"), "wb") as xml_file:
            xml_file.write(xml_string)
        
        # Ruta al archivo XSD que contiene la definición del esquema
        xsd_file = os.path.join(current_directory, '..', 'utils', 'MP', "MPItemFeed.xsd")
        
        try:
            # Parsea el archivo XSD
            schema = etree.XMLSchema(etree.parse(xsd_file))
        
            # Parsea el archivo XML
            xml_data = etree.parse(os.path.join(current_directory, "ejemplo.xml"))
        
            # Valida el archivo XML contra el esquema XSD
            is_valid = schema.validate(xml_data)
        
            if is_valid:
                #ENVIAR XML A WALMART API
                params = self.env['ir.config_parameter'].sudo()
                client_id = params.get_param('ctt_walmart.walmart_client_id')
                client_secret = params.get_param('ctt_walmart.walmart_client_secret')

                url = "feeds?feedType=item"
                api_client = WalmartAPI(client_id, client_secret)
                
                files=[
                    ('file',('ejemplo.xml',open(os.path.join(current_directory, "ejemplo.xml"),'rb'),'text/xml'))
                ]

                response = api_client.send_request("POST", url, file=files)
                _logger.warning(response)

                feed = self.env['walmart.feed'].create({
                    'feedId': response['feedId'],
                    'status': 'RECEIVED'
                })

                feed.feed_status()

                self.write({'walmart_feed_id': feed.id})
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'success',
                        'sticky': True,
                        'message': ("Artículo se ha enviado para su publicación"),
                    }
                }
            
            else:
                message = "El archivo XML no cumple con el esquema XSD. Errores: \n"
                for error in schema.error_log:
                    message += f"Linea {error.line}: {error.message} \n"
                raise ValidationError(message)
        except etree.XMLSchemaParseError as e:
            raise ValidationError(f"Error al analizar el archivo XSD: {e}")
        except etree.XMLSyntaxError as e:
            raise ValidationError(f"Error al analizar el archivo XML: {e}")
        except Exception as e:
            raise ValidationError(f"Ocurrió un error inesperado: {e}")