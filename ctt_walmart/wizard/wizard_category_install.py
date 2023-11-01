# -*- coding: utf-8 -*-

from odoo import models, fields, api
import xml.etree.ElementTree as ET
import os
import logging


_logger = logging.getLogger(__name__)

class CttWalmartCatgoryInstall(models.TransientModel):
    _name = 'walmart.category.install'

    categ_ids = fields.Many2many('marketplaces.category', string='Categorías')

    def install_categs(self):
        # Función para extraer la información de los elementos
        def extract_info(element, namespaces):
            name = element.find("xsd:annotation/xsd:appinfo/wm:displayName", namespaces).text
            required = element.find("xsd:annotation/xsd:appinfo/wm:requiredLevel", namespaces).attrib.get("value", "Optional") == "Required"
            type = "string"
            return name, required , type

        #Funcion para leer archivo y extraer campos
        def extract_file_info(file, complexType):
            # Cargar el archivo XSD
            xsd_file_path = os.path.join(
                os.path.dirname(__file__),'..', 'utils', 'MP', f'{file}.xsd'
            )
            tree = ET.parse(xsd_file_path)
            root = tree.getroot()
            
            # Crear un diccionario para almacenar los resultados
            result_dict = {}
        
            # Definir los namespaces
            namespaces = {
                "xsd": "http://www.w3.org/2001/XMLSchema",
                "wm": "http://walmart.com/"
            }
            
            # Buscar elementos complejos de tipo "Tires" y extraer la información
            for element in root.findall(complexType, namespaces):
                for child in element.find("xsd:all", namespaces):
                    if child.tag.endswith("element"):
                        name, required, type = extract_info(child, namespaces)
                        element_name = child.attrib.get("name", "")
                        nested_elements =  child.find('.//xsd:complexType', namespaces)
                        if nested_elements:
                            if nested_elements.find("xsd:all", namespaces):
                                for elem in nested_elements.find("xsd:all", namespaces):
                                    if elem.tag.endswith("element"):
                                        if elem.attrib.get("name", "") in ("measure", "unit"):
                                            type = "number_unit"
                            elif nested_elements.find("xsd:sequence",namespaces):
                                type = "list"
                        result_dict[element_name] = {"name": element_name, "displayName": name, "required": required, "type": type}
            
            return result_dict
        
        for categ in self.categ_ids:

            #Extraer campos de categoria
            categ_fields = extract_file_info(categ.group, f".//xsd:complexType[@name='{categ.name}']")

            # Crear attributo de categoria
            for key, value in categ_fields.items():
                self.env['marketplaces.category.attribute'].create({
                    'category_id': categ.id,
                    'name': value['name'],
                    'display_name': value['displayName'],
                    'required': value['required'],
                    'type': value['type']
                })
            
            categ.write({'is_installed': True})
            