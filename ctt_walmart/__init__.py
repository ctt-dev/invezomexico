# -*- coding: utf-8 -*-

from . import controllers
from . import models
from . import utils
from . import wizard

import os
from odoo import api, SUPERUSER_ID
import xml.etree.ElementTree as ET
import logging

_logger = logging.getLogger(__name__)

def _walmart_post_init(cr, registry):
    """Crea los records necesarios para el posteo de productos a traves de la API de
    Walmart, campos necesarios para ItemFeed y la categoria Tires a traves de schemas xsd
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    # Aquí puedes ejecutar el código que deseas que se ejecute después de la instalación
    # Por ejemplo, puedes crear registros, realizar configuraciones, etc.
    # env['res.partner'].create({'name': 'Ejecutado después de la instalación'})

    #Cargar marketplace
    marketplace = env.ref("ctt_walmart.marketplace_walmart")

    #Nombres de archivos .xsd
    category_names = ['Animal','ArtAndCraftCategory','Baby','CarriersAndAccessoriesCategory','ClothingCategory','Electronics',
                     'FoodAndBeverageCategory','FootwearCategory','FurnitureCategory','GardenAndPatioCategory','HealthAndBeauty',
                     'Home','JewelryCategory','Media','MusicalInstrument','OccasionAndSeasonal','OfficeCategory','OtherCategory',
                     'Photography','SportAndRecreation','ToolsAndHardware','ToysCategory','Vehicle','WatchesCategory']

    #Función para leer archivo y extraer categorías
    def extract_file_info(file):
        xsd_file_path = os.path.join(
            os.path.dirname(__file__), 'utils' ,'MP', f'{file}.xsd'
        )
        
        tree = ET.parse(xsd_file_path)
        root = tree.getroot()
        
        # Crear una lista para almacenar los resultados
        result = []
    
        # Definir los namespaces
        namespaces = {
            "xsd": "http://www.w3.org/2001/XMLSchema",
            "wm": "http://walmart.com/"
        }
    
        element_categories = root.find(f".//xsd:complexType[@name='{file}']", namespaces)
        
        for element in element_categories.findall(".//xsd:choice//xsd:element", namespaces):
            element_name = element.attrib.get("name", "")
            result.append(element_name)
        
        return result
        
    for group in category_names:
        categories = extract_file_info(group)

        for categ in categories:
            #Crear Categoria Tires
            categoria = env['marketplaces.category'].create({
                'marketplace_id': marketplace.id,
                'name': categ,
                # 'display_name': '',
                'group': group
            })
    
    # # Función para extraer la información de los elementos
    # def extract_info(element, namespaces):
    #     name = element.find("xsd:annotation/xsd:appinfo/wm:displayName", namespaces).text
    #     required = element.find("xsd:annotation/xsd:appinfo/wm:requiredLevel", namespaces).attrib.get("value", "Optional") == "Required"
    #     type = "string"
    #     return name, required , type

    # #Funcion para leer archivo y extraer campos
    # def extract_file_info(file, complexType):
    #     # Cargar el archivo XSD
    #     xsd_file_path = os.path.join(
    #         os.path.dirname(__file__), 'utils', 'MP', file
    #     )
    #     tree = ET.parse(xsd_file_path)
    #     root = tree.getroot()
        
    #     # Crear un diccionario para almacenar los resultados
    #     result_dict = {}
    
    #     # Definir los namespaces
    #     namespaces = {
    #         "xsd": "http://www.w3.org/2001/XMLSchema",
    #         "wm": "http://walmart.com/"
    #     }
        
    #     # Buscar elementos complejos de tipo "Tires" y extraer la información
    #     for element in root.findall(complexType, namespaces):
    #         for child in element.find("xsd:all", namespaces):
    #             if child.tag.endswith("element"):
    #                 name, required, type = extract_info(child, namespaces)
    #                 element_name = child.attrib.get("name", "")
    #                 nested_elements =  child.find('.//xsd:complexType', namespaces)
    #                 if nested_elements:
    #                     for elem in nested_elements.find("xsd:all", namespaces):
    #                         if elem.tag.endswith("element"):
    #                             if elem.attrib.get("name", "") in ("measure", "unit"):
    #                                 type = "number_unit"
    #                 result_dict[element_name] = {"name": element_name, "displayName": name, "required": required, "type": type}
        
    #     return result_dict

    # #Extraer campos de marketplace
    # marketplace_fields = extract_file_info('MPOffer.xsd', ".//xsd:complexType[@name='MPOffer']")

    # #Crear campo de marketplace
    # for key, value in marketplace_fields.items():
    #     env['marketplaces.marketplace.field'].create({
    #         'marketplace_id': marketplace.id,
    #         'complex_type': 'MPOffer',
    #         'name': value['name'],
    #         'display_name': value['displayName'],
    #         'required': value['required'],
    #         'type': value['type']
    #     })

    # #Extraer campos de categoria
    # categ_fields = extract_file_info('Vehicle.xsd', ".//xsd:complexType[@name='Tires']")
    
    # # Crear attributo de categoria Tires
    # for key, value in categ_fields.items():
    #     env['marketplaces.category.attribute'].create({
    #         'category_id': categoria_tires.id,
    #         'name': value['name'],
    #         'display_name': value['displayName'],
    #         'required': value['required'],
    #         'type': value['type']
    #     })

    # mpitem_fields = {
    #     "sku": {"name": "sku", "displayName": "SKU", "required": True, "type": "string"},
    #     "productIdType": {"name": "productIdType", "displayName": "Tipo de indentificador de producto", "required": True, "type": "string"},
    #     "productId": {"name": "productId", "displayName": "Identificador de producto", "required": True, "type": "string"}
    # }

    # # Crear campos de MPItem
    # for hey, value in mpitem_fields.items():
    #     env['marketplaces.marketplace.field'].create({
    #         'marketplace_id': marketplace.id,
    #         'complex_type': 'MPItem',
    #         'name': value['name'],
    #         'display_name': value['displayName'],
    #         'required': value['required'],
    #         'type': value['type']
    #     })