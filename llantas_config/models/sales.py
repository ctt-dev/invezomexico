from odoo import models, fields, api, _
import logging
import json
from odoo import exceptions
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__) 
from datetime import datetime, date
import unicodedata

class sale_order_inherit(models.Model):
    _inherit = 'sale.order'
    _description = 'Orden de venta'


    ganancia = fields.Float(string="Ganancia", compute="_compute_ganancia", store=True)
    margin_percent = fields.Float(string="Margen (%)", compute="_compute_ganancia", store=True)


    @api.depends('amount_untaxed', 'amount_tax', 'order_line', 'comision', 'envio')
    def _compute_ganancia(self):
        # Cache de OC por origin
        origins = self.mapped("name")
        purchase_map = {
            po["origin"]: po["amount_total"]
            for po in self.env["purchase.order"].read_group(
                [("origin", "in", origins)],
                ["origin", "amount_total"],
                ["origin"],
            )
        }
    
        for order in self:
            # Usar amount_untaxed (sin IVA) para la base de cálculo
            base_venta = order.amount_untaxed or 0
            comision = order.comision or 0
            envio = order.envio or 0
            
            # Costo de productos (sin IVA)
            costo_productos = 0
            for line in order.order_line:
                if line.costo_promedio:
                    # costo_promedio ya debe ser sin IVA
                    costo_productos += line.costo_promedio * line.product_uom_qty
    
            # Obtener total de OC si existe
            total_oc = purchase_map.get(order.name, 0)
            if total_oc:
                # Si total_oc viene con IVA, lo dividimos entre 1.16
                costo_total = total_oc / 1.16
            else:
                costo_total = costo_productos
    
            # Cálculo de ganancia (todo sin IVA para consistencia)
            ganancia_neta = base_venta - comision - envio - costo_total
            
            # Asignar valores
            order.ganancia = ganancia_neta
    
            # Calcular margen sobre base_venta (sin IVA)
            if base_venta:
                order.margin_percent = round((ganancia_neta / base_venta) * 100, 1)
            else:
                order.margin_percent = 0

    


    @api.onchange('marketplace')
    def onchange_marketplace_for_llantas_config(self):
        if self.company_id and getattr(self.company_id, 'name', '') != 'ADRONE':
            if self.marketplace.id: 
                if self.marketplace.diarios_id.id:
                    self.journal_id = self.marketplace.diarios_id
                    # raise UserError(str(self.journal_id.name))
            
    is_check=fields.Boolean(
        string="Revisar disponibilidad",
        default=False,
        tracking=True,
    )
    
    def revisar_disponibilidad(self):
        all_lines_available = True
        preferred_warehouse = None
        current_company = self.company_id.name  # Nombre de la compañía actual
    
        for line in self.order_line:
            # Verificar si el producto de la línea es un paquete
            if line.product_id.bom_ids and line.product_id.bom_ids[0].type == 'phantom':
                # Si es un paquete, reemplazar por líneas de BOM
                for bom_line in line.product_id.bom_ids[0].bom_line_ids:
                    product = bom_line.product_id
                    quantity_needed = bom_line.product_qty * line.product_uom_qty
    
                    # Verificar disponibilidad
                    available = self._check_product_availability(product, quantity_needed)
                    if not available:
                        all_lines_available = False
    
                    # Calcular el precio unitario basado en el precio del paquete
                    price_unit = (
                        line.price_unit / bom_line.product_qty
                        if bom_line.product_qty > 0
                        else 0.0
                    )
    
                    # CORREGIDO: Asegurar que product_uom esté incluido
                    self.env['sale.order.line'].create({
                        'order_id': self.id,
                        'product_id': product.id,
                        'product_uom_qty': quantity_needed,
                        'product_uom_id': bom_line.product_uom_id.id or product.uom_id.id,  # CORRECCIÓN: Usar la UOM de la BOM o la del producto
                        'price_unit': price_unit,
                    })
                
                # Eliminar la línea original del paquete
                line.unlink()
            else:
                # Si no es un paquete, procesar normalmente
                available = self._check_product_availability(line.product_id, line.product_uom_qty)
                if not available:
                    all_lines_available = False
    
        # Verificar si hay un almacén "3PL Virtual" disponible
        if not all_lines_available:
            preferred_warehouse = self._get_preferred_3pl_warehouse(current_company)
    
        # Asignar el almacén final
        if preferred_warehouse:
            self.write({'warehouse_id': preferred_warehouse.id})
        elif all_lines_available:
            # Seleccionar almacén con mayor stock (puede ser cualquier almacén regular)
            warehouse_id = self._select_warehouse_with_max_stock()
            if warehouse_id:
                self.write({'warehouse_id': warehouse_id})
            else:
                # Asignar el primer almacén interno que encuentre
                fallback_warehouse = self._get_first_internal_warehouse()
                if fallback_warehouse:
                    self.write({'warehouse_id': fallback_warehouse.id})
                else:
                    raise UserError(f"No se encontró un almacén interno configurado para la empresa {current_company}.")
        else:
            # Asignar el primer almacén interno si no hay stock suficiente ni 3PL
            fallback_warehouse = self._get_first_internal_warehouse()
            if fallback_warehouse:
                self.write({'warehouse_id': fallback_warehouse.id})
            else:
                raise UserError(f"No hay stock disponible y no se encontró un almacén 3PL Virtual ni un almacén interno para la empresa {current_company}.")
    
        # Marcar como revisado
        self.is_check = True


    
    def _check_product_availability(self, product, quantity_needed):
        """
        Verifica si un producto tiene disponibilidad suficiente considerando
        solo cantidades positivas en ubicaciones internas.
        """
        _logger.warning(f"Verificando disponibilidad para {product.name}, cantidad necesaria: {quantity_needed}")
        
        # Verificar el tipo de producto
        if product.type == 'service':
            return True
        
        # Obtener la cantidad disponible en ubicaciones internas
        available_quantity = 0.0
        for quant in product.stock_quant_ids:
            if quant.quantity > 0 and quant.location_id.usage == 'internal':
                available_quantity += quant.quantity
        
        _logger.warning(f"Cantidad disponible: {available_quantity}")
        
        return available_quantity >= quantity_needed
    
    def _get_preferred_3pl_warehouse(self, company_name):
        # Buscar el almacén 3PL Virtual según la empresa
        if company_name == 'LLANTIRED':
            return self.env['stock.warehouse'].search([('name', '=', 'ALMACEN LLANTIRED- 3PL VIRTUAL')], limit=1)
        elif company_name == 'LA BODEGA LLANTAS Y ACCESORIOS':
            return self.env['stock.warehouse'].search([('name', '=', 'ALMACEN LA BODEGA- 3PL VIRTUAL')], limit=1)
        return None
    
    def _select_warehouse_with_max_stock(self):
        """
        Selecciona el almacén con mayor stock disponible considerando
        solo cantidades positivas.
        """
        stock_by_warehouse = {}
        for line in self.order_line:
            for quant in line.product_id.stock_quant_ids:
                if quant.quantity > 0 and quant.location_id.usage == 'internal':
                    warehouse = quant.location_id.warehouse_id
                    if warehouse:
                        stock_by_warehouse[warehouse.id] = stock_by_warehouse.get(warehouse.id, 0) + quant.quantity
        if stock_by_warehouse:
            return max(stock_by_warehouse, key=stock_by_warehouse.get)
        return None
    
    def _get_first_internal_warehouse(self):
        """
        Busca el primer almacén interno disponible.
        """
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.company_id.id)], limit=1)
        return warehouse



    
    marketplace = fields.Many2one(
        "llantas_config.marketplaces",
        string="Marketplace",
        tracking=True,
        store=True,
        
    )
    
    @api.depends('marketplace','marketplace.name')
    def _compute_marketplace_name(self):
        for rec in self:
            marketplace_name = ""
            # raise UserError('.....' + str(rec.marketplace.name))
            if rec.marketplace.id:
                marketplace_name = rec.marketplace.name
            rec.marketplace_name = marketplace_name
    marketplace_name = fields.Char(
        string="Marketplace",
        compute=_compute_marketplace_name,
        store=True,
    )

    marketplace_name2 = fields.Char(
        string="Canal de venta",
        related="marketplace.name",
        store=True,
    )
    
    comision=fields.Float(
        string="Comisión",
        tracking=True,
    )
    envio=fields.Float(
        string="Envio",
        tracking=True,
    )

    comprador_id=fields.Many2one(
        "hr.employee",
        string="Comprador",
        tracking=True,
        store=True,
    )

    folio_venta=fields.Char(
        string="No. Venta",
        tracking=True,
        store=True,

    )


    json_data = fields.Text(string="JSON Data")

    es_venta_directa = fields.Boolean(
        string="Es Venta Directa",
        compute="_compute_es_venta_directa",
        store=False  # No es necesario almacenar si solo se usa en vistas
    )
    
    @api.depends('marketplace_name')
    def _compute_es_venta_directa(self):
        # Palabras clave que identifican una venta directa
        keywords = ['VENTA DIRECTA', 'VENTA DIRECTA CON', 'VENTA DIRECTA CON', 'VENTA DIRECTA CONTADO']
        
        for rec in self:
            es_directa = False
            if rec.marketplace_name:
                # Convertir a mayúsculas para comparación insensible
                marketplace_upper = rec.marketplace_name.upper()
                
                # Verificar si alguna keyword está contenida en el texto
                for keyword in keywords:
                    if keyword in marketplace_upper:
                        es_directa = True
                        break
            
        rec.es_venta_directa = es_directa

    # @api.model
    # def create(self, values):
    #     if 'channel_order_reference' in values:
    #         values['folio_venta'] = values['channel_order_reference']
    #     elif 'channel_order_id' in values and not values.get('folio_venta'):
    #         # Si el valor no viene en `values`, tomar el valor actual de `rec`
    #         values['folio_venta'] = values['channel_order_id']

    #     if 'yuju_seller_shipping_cost' in values:
    #         values['envio'] = values['yuju_seller_shipping_cost']
    #     if 'yuju_marketplace_fee' in values:
    #         values['comision'] = values['yuju_marketplace_fee']
                
    #     # Verificación de unicidad de 'folio_venta'
    #     if 'folio_venta' in values:
    #         venta_ids = self.search([
    #             ('folio_venta', '=', values['folio_venta']),
    #             ('folio_venta', '!=', False)
    #         ])
    #         if venta_ids:
    #             raise UserError('El número de venta debe ser único.')
    
    #     # Asignar 'guia' si se ha proporcionado 'yuju_carrier_tracking_ref'
    #     if 'yuju_carrier_tracking_ref' in values:
    #         values['guia'] = values['yuju_carrier_tracking_ref']
        
    #     # Verificación de unicidad de 'guia'
    #     guia = values.get('guia')
    #     if guia:
    #         ventas = self.search([
    #             ('guia', '=', guia),
    #             ('guia', '!=', False)
    #         ])
    #         if ventas:
    #             raise UserError('El número de guía debe ser único.')
    
    #     # Actualizar marketplace en create
    #     channel = values.get('channel')
    #     if channel:
    #         # Quitar espacios y acentos
    #         channel = self.remove_accents(channel.strip())
    
    #         # Buscar el marketplace usando solo el nombre
    #         marketplace_record = self.env['llantas_config.marketplaces'].search([
    #             ('company_id', '=', values.get('company_id')),
    #             ('name', '=', channel)
    #         ], limit=1)
    
    #         # Si no se encuentra, dejar el valor de 'marketplace' como False
    #         values['marketplace'] = marketplace_record.id if marketplace_record else False
    
    #     # Llamada al método create del super para crear el registro
    #     _logger.warning(values)
    #     sale = super(sale_order_inherit, self).create(values)
    #     data = []
    #     for rec in sale.order_line:
    #         if rec.product_template_id.es_paquete:
    #             lista = rec.product_template_id.bom_ids[0]
    #             _logger.warning(lista)
    #             cont = 0
    #             for prod in lista.bom_line_ids:
    #                 if cont == 0:
    #                     price = rec.price_unit
    #                 else:
    #                     price = 0
    #                 ol = self.env['sale.order.line'].create({
    #                     'order_id': sale.id,
    #                     'customer_lead': 0.0,
    #                     'name': prod.product_id.name,
    #                     'product_id': prod.product_id.id,
    #                     'product_uom_qty': (prod.product_qty*rec.product_uom_qty),
    #                     'price_unit': price/(prod.product_qty*rec.product_uom_qty)
    #                 })
    #                 sale.order_line = [(4, ol.id)]
    #         data.append(rec.id)
    #     for id in data:
    #         sale.order_line = [(3, id)]
    #     return sale

    # @api.model
    # def create(self, values):
    #     # Verificación de campos y asignación de valores
    #     if 'channel_order_reference' in values:
    #         values['folio_venta'] = values['channel_order_reference']
    #     elif 'channel_order_id' in values and not values.get('folio_venta'):
    #         values['folio_venta'] = values['channel_order_id']
    
    #     if 'yuju_seller_shipping_cost' in values:
    #         values['envio'] = values['yuju_seller_shipping_cost']
    #     else:
    #         total_shipping_cost = sum(line['product_uom_qty'] * values['marketplace'].shipping_cost for line in values.get('order_line', []))
    #         values['envio'] = total_shipping_cost
            
    #     if 'yuju_marketplace_fee' in values:
    #         values['comision'] = values['yuju_marketplace_fee']
        
    #     # Verificación de unicidad de 'folio_venta'
    #     if 'folio_venta' in values:
    #         venta_ids = self.search([
    #             ('folio_venta', '=', values['folio_venta']),
    #             ('folio_venta', '!=', False)
    #         ])
    #         if venta_ids:
    #             raise UserError('El número de venta debe ser único.')
        
    #     # Asignar 'guia' si se ha proporcionado 'yuju_carrier_tracking_ref'
    #     if 'yuju_carrier_tracking_ref' in values:
    #         values['guia'] = values['yuju_carrier_tracking_ref']
        
    #     # Verificación de unicidad de 'guia'
    #     guia = values.get('guia')
    #     if guia:
    #         ventas = self.search([
    #             ('guia', '=', guia),
    #             ('guia', '!=', False)
    #         ])
    #         if ventas:
    #             raise UserError('El número de guía debe ser único.')
    
    #     # Actualizar marketplace en create
    #     channel = values.get('channel')
    #     if channel:
    #         channel = self.remove_accents(channel.strip())
    #         marketplace_record = self.env['llantas_config.marketplaces'].search([
    #             ('company_id', '=', values.get('company_id')),
    #             ('name', '=', channel)
    #         ], limit=1)
    #         values['marketplace'] = marketplace_record.id if marketplace_record else False

    #     # Crear la venta usando el método estándar de Odoo
    #     sale = super(sale_order_inherit, self).create(values)
        
    #     # # Asignar warehouse_id a la venta
    #     # warehouse_id = False
    #     # for line in sale.order_line:
    #     #     # Obtener las ubicaciones internas donde hay existencia del producto
    #     #     locations = []
    #     #     for quant in line.product_id.stock_quant_ids:
    #     #         if quant.quantity > 0 and quant.location_id.usage == 'internal':
    #     #             locations.append(quant.location_id.display_name)
    #     #             if quant.location_id.location_id:
    #     #                 warehouse_id = quant.location_id.location_id.warehouse_id  # Almacén asociado a la ubicación interna
            
    #     #     if not locations:
    #     #         # Si no hay inventario en ubicaciones internas, asignar el almacén predeterminado
    #     #         warehouse = self.env['stock.warehouse'].search([('name', '=', 'ALMACEN LLANTIRED- 3PL VIRTUAL')], limit=1)
    #     #         if not warehouse:
    #     #             raise UserError("No se encontró el almacén predeterminado 'ALMACEN LLANTIRED- 3PL VIRTUAL' en el sistema.")
    #     #         warehouse_id = warehouse

    #     #     # Asignamos el warehouse_id encontrado o el predeterminado
    #     #     sale.write({'warehouse_id': warehouse_id.id})
        
    #     # Crear líneas de orden para productos empaquetados (si aplica)
    #     for line in sale.order_line:
    #         if line.product_template_id.es_paquete:
    #             # Aquí tenemos la lógica para los productos empaquetados
    #             bom = line.product_template_id.bom_ids[0]  # Suponemos que existe una única BOM asociada
    #             for prod in bom.bom_line_ids:
    #                 price = line.price_unit
    #                 # Creamos las nuevas líneas de orden basadas en la BOM
    #                 ol = self.env['sale.order.line'].create({
    #                     'order_id': sale.id,
    #                     'customer_lead': 0.0,
    #                     'name': prod.product_id.name,
    #                     'product_id': prod.product_id.id,
    #                     'product_uom': prod.product_uom_id.id,
    #                     'product_uom_qty': prod.product_qty * line.product_uom_qty,  # Multiplicamos por la cantidad del paquete
    #                     'price_unit': price / (prod.product_qty * line.product_uom_qty),  # Ajustamos el precio unitario
    #                 })
    #                 sale.order_line = [(4, ol.id)]  # Añadimos la nueva línea al pedido
    #             # Finalmente eliminamos la línea original del pedido
    #             sale.order_line = [(3, line.id)]
        
    #     return sale

    @api.model
    def create(self, vals_list):
        _logger.warning('create')
        
        # Asegurarnos de que vals_list sea una lista
        if not isinstance(vals_list, list):
            vals_list = [vals_list]
        
        processed_vals_list = []
        
        for values in vals_list:
            # Lógica simplificada en el método create
            if 'channel_order_reference' in values:
                values['folio_venta'] = values['channel_order_reference']
            
            if 'yuju_seller_shipping_cost' in values:
                values['envio'] = values['yuju_seller_shipping_cost']
            
            if 'yuju_marketplace_fee' in values:
                values['comision'] = values['yuju_marketplace_fee']
            
            # Verificación de unicidad de 'folio_venta'
            if 'folio_venta' in values:
                venta_ids = self.search([
                    ('folio_venta', '=', values['folio_venta']),
                    ('folio_venta', '!=', False)
                ])
                if venta_ids:
                    raise UserError('El número de venta debe ser único.')
            
            # Verificación de unicidad de 'guia' - CORREGIDO
            if 'guia' in values:
                guia = values.get('guia')
                if guia:
                    ventas = self.search([
                        ('guia', '=', guia),
                        ('guia', '!=', False)
                    ])
                    if ventas:
                        raise UserError('El número de guía debe ser único.')
            
            # Actualizar marketplace en create
            channel = values.get('channel')
            if channel:
                channel = self.remove_accents(channel.strip())
                marketplace_record = self.env['llantas_config.marketplaces'].search([
                    ('company_id', '=', values.get('company_id')),
                    ('name', '=', channel)
                ], limit=1)
                values['marketplace'] = marketplace_record.id if marketplace_record else False
            
            # Verificación de unicidad de 'folio_venta' - SOLO si no estamos en contexto de copia
            if not self.env.context.get('skip_folio_validation'):
                if 'folio_venta' in values:
                    venta_ids = self.search([
                        ('folio_venta', '=', values['folio_venta']),
                        ('folio_venta', '!=', False)
                    ])
                    if venta_ids:
                        raise UserError('El número de venta debe ser único.')
            
            # Verificación de unicidad de 'guia' - SOLO si no estamos en contexto de copia
            if not self.env.context.get('skip_folio_validation'):
                if 'guia' in values:
                    guia = values.get('guia')
                    if guia:
                        ventas = self.search([
                            ('guia', '=', guia),
                            ('guia', '!=', False)
                        ])
                        if ventas:
                            raise UserError('El número de guía debe ser único.')
            
            processed_vals_list.append(values)
        
        # Crear la venta usando el método estándar de Odoo
        sales = super(sale_order_inherit, self).create(processed_vals_list)
        return sales


    auto_warehouse_id = fields.Many2one(
        'stock.warehouse',
        string="Almacén Automático",
        readonly=True,
        help="Este es el almacén sugerido automáticamente. Puede ser diferente al seleccionado manualmente."
    )
    
    @api.onchange('order_line')
    def change_lines(self):
        _logger.warning('change')
        for sale in self:
            _logger.warning(sale)
            _logger.warning(sale.order_line)
            _logger.warning(sale.marketplace)
        
            # Procesar líneas que son paquetes
            for line in sale.order_line:
                new_lines = []
                if line.product_template_id.es_paquete:
                    # Obtenemos la primera BOM asociada al producto
                    bom = line.product_template_id.bom_ids[:1]  # Usar [:1] para mayor seguridad
                    if not bom:
                        continue
    
                    # Calculamos el precio para dividir entre los productos de la BOM
                    price_per_unit = line.price_unit / (line.product_uom_qty or 1)
    
                    for prod in bom.bom_line_ids:
                        new_line_vals = {
                            'order_id': sale.id,
                            'customer_lead': 0.0,
                            'name': prod.product_id.name,
                            'product_id': prod.product_id.id,
                            'product_uom': prod.product_uom_id.id,
                            'product_uom_qty': prod.product_qty * line.product_uom_qty,
                            'price_unit': price_per_unit,  # Precio ajustado
                        }
                        new_lines.append((0, 0, new_line_vals))  # Añadir la nueva línea
    
                    # Remover la línea original después de agregar sus componentes
                    sale.order_line = [(3, line.id)]
                    sale.order_line = new_lines
                    _logger.warning(new_lines)
    
            # Asignar el almacén automáticamente, pero sin afectar el seleccionado manualmente
            warehouse_id = self._find_warehouse(sale)
            sale.auto_warehouse_id = warehouse_id

    def _find_warehouse(self, sale):
        """
        Función auxiliar para encontrar y retornar el almacén adecuado para la orden.
        Prioriza el stock disponible en la empresa actual.
        """
        _logger.warning('find')
        warehouse_id = False
        current_company = sale.company_id
        
        # Recolectar ubicaciones con stock por empresa
        for line in sale.order_line:
            # CORREGIDO: En Odoo 19 usar line.product_id.type en lugar de detailed_type
            product_type = line.product_id.type
            
            locations = [
                quant.location_id
                for quant in line.product_id.stock_quant_ids
                if quant.quantity > 0
                and quant.location_id.usage == 'internal'
                and quant.location_id.company_id == current_company
            ]
            
            # CORREGIDO: Verificar el tipo de producto usando product_id.type
            if product_type == 'service':
                continue
    
            if locations:
                # Priorizar el almacén con mayor stock dentro de la misma empresa
                warehouse_stock = {}
                for loc in locations:
                    warehouse = loc.warehouse_id
                    if warehouse:
                        # Sumar las cantidades de stock en esa ubicación
                        total_stock = sum(
                            quant.quantity
                            for quant in self.env['stock.quant'].search([('location_id', '=', loc.id)])
                        )
                        if warehouse.id not in warehouse_stock:
                            warehouse_stock[warehouse.id] = total_stock
                        else:
                            warehouse_stock[warehouse.id] += total_stock
    
                # Seleccionar el almacén con mayor stock
                if warehouse_stock:
                    warehouse_id = max(warehouse_stock, key=warehouse_stock.get)
    
            # Si no hay stock en la misma empresa, usar el almacén 3PL Virtual
            if not warehouse_id:
                preferred_warehouse = self.env['stock.warehouse'].search([
                    ('name', '=', f'ALMACEN {current_company.name.upper()}- 3PL VIRTUAL'),
                    ('company_id', '=', current_company.id)
                ], limit=1)
                if preferred_warehouse:
                    warehouse_id = preferred_warehouse.id
                else:
                    # Seleccionar cualquier almacén disponible como último recurso
                    fallback_warehouse = self.env['stock.warehouse'].search([
                        ('company_id', '=', current_company.id)
                    ], limit=1)
                    if fallback_warehouse:
                        warehouse_id = fallback_warehouse.id
                    else:
                        raise UserError(f"No se encontró un almacén configurado para la empresa {current_company.name}.")
        
        return warehouse_id

    
    
    
    @api.onchange('comprador_id')
    def _change_vendedor(self):
        _logger.warning('change comprador')
        for rec in self:
            if rec.comprador_id and rec.comprador_id.user_id:
                rec.user_id = rec.comprador_id.user_id
            else:
                user = self.env['res.users'].search([('name','=','Yuju')])
                if user:
                    rec.user_id = user.id



    def remove_accents(self, input_str):
        # Normalizar la cadena eliminando los acentos
        nfkd_form = unicodedata.normalize('NFKD', input_str)
        return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
    
    def write(self, values):
        if self.env.context.get('skip_carrier_update'):
            _logger.info("Se omite actualización de carrier para evitar recursión.")
            return super(sale_order_inherit, self).write(values)
        
        for rec in self:
            for line in rec.order_line:
                if line.product_id:
                    # Guardar el costo promedio (standard_price) en la línea
                    line.costo_promedio = line.product_id.standard_price
            
            # Omitir validaciones si la acción es cancelar
            if values.get('state') == 'cancel':
                _logger.info("La orden se está cancelando, se omiten validaciones.")
                return super(sale_order_inherit, self).write(values)
            
            # Actualizar marketplace en write - CORREGIDO
            # Usar yuju_channel en lugar de channel
            channel = rec.yuju_channel if hasattr(rec, 'yuju_channel') else None
            if channel:
                channel = self.remove_accents(channel.strip())
                yuju_tag_selection = dict(self.env['llantas_config.marketplaces']
                                           .fields_get(allfields=['yuju_tag'])['yuju_tag']['selection'])
                yuju_tag_key = next((key for key, label in yuju_tag_selection.items() 
                                     if self.remove_accents(label.lower()) == channel.lower()), None)
                
                domain = [('company_id', '=', rec.company_id.id)]
                if yuju_tag_key:
                    domain.append(('yuju_tag', '=', yuju_tag_key))
                else:
                    domain.append(('name', '=', channel))
        
                marketplace_record = self.env['llantas_config.marketplaces'].search(domain, limit=1)
        
                if not marketplace_record:
                    _logger.warning(f"No se encontró el marketplace con el nombre o tag '{channel}' para la empresa actual.")
                    values['marketplace'] = False
                else:
                    values.update({
                        'marketplace': marketplace_record.id,
                        'fee_import': marketplace_record.fee_marketplace,
                    })
            
            # 🔥 Actualización del carrier
            if 'yuju_carrier' in values:
                yuju_carrier = values.get('yuju_carrier', '').strip()
                carrier_record = self.env['llantas_config.carrier'].search([
                    ('name', '=ilike', yuju_carrier)
                ], limit=1)
    
                new_carrier_id = carrier_record.id if carrier_record else False
    
                if rec.llantas_config_carrier_id.id != new_carrier_id:
                    values['llantas_config_carrier_id'] = new_carrier_id
                    _logger.info(f"Carrier actualizado a: {yuju_carrier}")
                else:
                    _logger.info("Carrier ya asignado, se omite escritura.")
    
            # Asignar y verificar 'folio_venta'
            if 'folio_venta' in values:
                values['folio_venta'] = values['folio_venta'] or False
                if values['folio_venta'] and values['folio_venta'] != rec.folio_venta:
                    venta_ids = rec.env['sale.order'].search([
                        ('folio_venta', '=', values['folio_venta']),
                        ('id', '!=', rec.id),
                        ('folio_venta', '!=', False)
                    ])
                    if venta_ids:
                        raise ValidationError(f"El folio de venta '{values['folio_venta']}' ya existe en otra orden.")
            
            # Asignar y verificar 'guia'
            if 'guia' in values:
                values['guia'] = values['guia'] or False
                if values['guia'] and values['guia'] != rec.guia:
                    ventas = self.env['sale.order'].search([
                        ('guia', '=', values['guia']),
                        ('id', '!=', rec.id),
                        ('guia', '!=', False)
                    ])
                    if ventas:
                        raise ValidationError(f"Número de guía duplicado: {values['guia']}.")
        
        # Llamada al método write del super para guardar los cambios
        return super(sale_order_inherit, self.with_context(skip_carrier_update=True)).write(values)



    def update_existing_order(self):
        """
        Busca y actualiza una orden existente basada en la referencia de canal.
        Si la orden existe, actualiza los campos proporcionados en 'values'.
        """
        for rec in self:
            if rec.channel_order_reference and rec.channel:
                order_reference = rec.channel_order_reference
                channel = rec.channel
                link=""
                if channel == 'Mercado Libre México':
                    link=f'https://www.mercadolibre.com.mx/{order_reference}'
                    rec.write({'link_venta':link})
    
            

    
    
    purchase_order = fields.Char(string="Purchase Order")
    
    link_venta=fields.Char(
        string="Link de venta",
        tracking=True,
    )

    link_facturacion=fields.Char(
        string="Link de facturacion",
        tracking=True,
        compute="_compute_link"
    )

    @api.depends('folio_venta', 'company_id.url_autofacturacion')
    def _compute_link(self):
        for order in self:
            try:
                if order.folio_venta:
                    if order.company_id.url_autofacturacion:
                        order.link_facturacion = f"{order.company_id.url_autofacturacion}/autofacturador/{order.folio_venta}"
                    else:
                        order.link_facturacion = ""
                else:
                    order.link_facturacion = ""
            except Exception as e:
                order.link_facturacion = ""
                _logger.error(f"Error computing link_facturacion for sale.order({order.id}): {e}")
                raise UserError(f"An error occurred while computing the invoicing link: {e}")
            
    status_ventas=fields.Many2one(
        "llantas_config.status_ventas",
        string="Estatus",
        tracking=True,
    
    )

    status_venta=fields.One2many(
        "llantas_config.status_ventas",
        "name",
        string="Estatus",
        tracking=True,

    )

    ventas_status = fields.Selection([
        ('01','Pendiente'),
        ('02','Debito en curso'),
        ('03','Traspaso'),
        ('04','Guia pendiente'),
        ('05','Enviado'),
        ('06','Entregado'),
        ('07','Cerrado'),
        ('08','Incidencia'),
        ('09','Devolución'),
        ('10','Cancelado por stock'),
        ('11','Cancelado por el cliente'),
        ('12','Cancelado'),], 
        string="Estado de la venta", 
        default='01', 
        tracking=True, 
        store=True)

    lineas_orden = fields.Many2one(
        "sale.order.line",
        string="lineas",
    )

    fecha_venta=fields.Datetime(
        string="Fecha venta",
        default=fields.Datetime.now,
        tracking=True,
        store=True
    )

    mostrar_comision=fields.Boolean(
        related="marketplace.mostrar_comision",
    )

    mostrar_envio=fields.Boolean(
        related="marketplace.mostrar_envio",
    )

    es_killer = fields.Boolean(
        string="Es killer?",
        default=False,
        compute='_compute_es_killer',
        store=True,
    )

    @api.depends('order_line.is_killer')
    def _compute_es_killer(self):
        for rec in self:
            rec.es_killer = any(line.is_killer for line in rec.order_line)

    @api.onchange('marketplace', 'comision', 'iva', 'envio', 'guia', 'folio_venta', 'marketplace_name', 'partner_id', 'comprador_id', 'fecha_venta')
    def _onchange_sale(self):
        for rec in self:
            tab = self.env['llantas_config.ctt_llantas'].search([('sale_id','=',rec.id)])
            if tab:
                tab.write({
                    'partner_name': rec.partner_id.id,
                    'marketplace': rec.marketplace,
                    'fecha': rec.fecha_venta,
                    'comprador_id':rec.comprador_id.id,
                    'comprador_name':rec.comprador_id.name,
                    'comision':rec.comision,
                    'envio':rec.envio,
                    'marketplace_name':rec.marketplace.name,
                    'tipo_factura': rec.tipo_factura,
                    'no_recoleccion': rec.guia,
                    'numero_guia' : rec.yuju_carrier_tracking_ref
                })
        
    

    disponibilidad_verificada = fields.Boolean(
        string="Disponibilidad verificada",
        default=False,
        readonly=True
    )
    
    
    def action_confirm(self):
        for order in self:
            # Solo validar si está en borrador
            if order.state not in ['draft', 'sent']:
                return super(sale_order_inherit, order).action_confirm()
    
            # Permitir si viene con contexto especial
            if order.env.context.get('skip_availability_check') or order.disponibilidad_verificada:
                return super(sale_order_inherit, order).action_confirm()
    
            if order.is_check:
                res = super(sale_order_inherit, order).action_confirm()
    
                if order.marketplace.category_id:
                    if order.marketplace.category_id not in order.partner_id.category_id:
                        order.partner_id.category_id += order.marketplace.category_id
    
                if order.yuju_seller_shipping_cost == 0.0:
                    total_shipping_cost = sum(
                        line.product_uom_qty for line in order.order_line
                    ) * order.marketplace.shipping_cost
                    order.write({'envio': total_shipping_cost})
    
                for line in order.order_line:
                    if line.costo_proveedor:
                        line.write({'costo_proveedor_2': line.costo_proveedor})
                        line.compute_costo_proveedor_total()
    
                return res
    
            raise UserError("Debe de comprobar disponibilidad primero.")






    # def _prepare_invoice(self):
    #     inv = super(sale_order_inherit, self)._prepare_invoice()
    #     if self.marketplace.id:
    #         if self.marketplace.diarios_id.id:
    #             if self.marketplace.diarios_id not in self.journal_id:
    #                 self.journal_id = self.marketplace.diarios_id
    #     return inv
    
    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        if self.company_id and getattr(self.company_id, 'name', '') != 'ADRONE':
            if self.marketplace.id:
                if self.marketplace.diarios_id.id:
                    invoice_vals.update({'journal_id': self.marketplace.diarios_id.id})
        return invoice_vals

    # Agrega este método para preservar las descripciones personalizadas en la factura
    def _prepare_invoice_line(self, line):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.
        Preserve the custom description from sale order line.
        """
        vals = super(sale_order_inherit, self)._prepare_invoice_line(line)
        
        # Preservar la descripción personalizada de la línea de venta
        if line.name and line.name != line.product_id.name:
            vals['name'] = line.name
        
        return vals

    def copy(self, default=None):
        default = dict(default or {})
        
        # Generar nuevo número de orden usando el método estándar de Odoo
        new_sequence = self.env['ir.sequence'].next_by_code('sale.order') or '/'
        
        default.update({
            'name': new_sequence,
            'folio_venta': False,
            'guia': False,
            'link_venta': False,  # También limpiar links si existen
        })
        
        # Crear una copia sin ejecutar validaciones de unicidad
        return super(sale_order_inherit, self.with_context(
            skip_folio_validation=True,
            mail_create_nolog=True  # Evitar logs innecesarios
        )).copy(default)

    
    def create_purchase_for_sale_order(self):
        _logger.warning('Iniciando creación de órdenes de compra...')
        for rec in self:
            if rec.state != 'sale':
                raise UserError("La orden de venta debe estar confirmada para generar una orden de compra.")
            
            # Agrupar líneas por proveedor
            lines_by_supplier = {}
            for line in rec.order_line:
                if line.proveedor_id:
                    lines_by_supplier.setdefault(line.proveedor_id, []).append(line)
            
            if not lines_by_supplier:
                raise UserError("No se encontraron líneas con proveedores asignados en esta orden de venta.")
            
            for proveedor, lines in lines_by_supplier.items():
                # Validaciones
                if any(line.qty_available_today > 0 for line in lines):
                    raise UserError("No se puede generar una orden de compra porque hay productos disponibles en stock.")
                
                total_compra = sum(line.product_uom_qty * line.costo_proveedor for line in lines)
                if total_compra > rec.amount_total and not rec.es_killer:
                    raise UserError("El total de la orden de compra excede el total de la orden de venta asociada.")
                
                # Obtener la moneda
                moneda = self.env['res.currency'].search([('name', '=', rec.currency_id.name)], limit=1)
                if not moneda:
                    raise UserError("No se encontró la moneda asociada a la orden de venta.")
                
                # Crear orden de compra
                try:
                    nueva_cotizacion_compra = self.env['purchase.order'].create({
                        'partner_id': proveedor.partner_id.id,
                        'currency_id': moneda.id,
                        'company_id': self.env.company.id,
                        'picking_type_id': rec.warehouse_id.in_type_id.id,
                        'auto_sale_order_id': rec.id,
                    })
                    _logger.info(f"Orden de compra creada: {nueva_cotizacion_compra.name}")
                except Exception as e:
                    _logger.error(f"Error creando la orden de compra: {str(e)}")
                    raise UserError("Ocurrió un error al intentar crear la orden de compra.")
                
                # Procesar líneas de compra
                for line in lines:
                    if not line.product_id.product_tmpl_id.es_paquete:
                        # Crear línea de compra para productos normales
                        purchase_line = self.env['purchase.order.line'].create({
                            'order_id': nueva_cotizacion_compra.id,
                            'product_id': line.product_id.id,
                            'name': line.product_id.name,
                            'product_qty': line.product_uom_qty,
                            'product_uom_id': line.product_uom_id.id,
                            'price_unit': line.costo_proveedor,
                            'sale_order_id': rec.id,
                            'codigo_proveedor': line.codigo_proveedor,
                        })
                        line.write({'purchase_line_ids': [(4, purchase_line.id)]})
                    else:
                        # Crear líneas de compra para materiales del paquete
                        lmateriales = self.env['mrp.bom.line'].search([('parent_product_tmpl_id', '=', line.product_id.product_tmpl_id.id)])
                        if not lmateriales:
                            raise UserError(f"El paquete '{line.product_id.name}' no tiene lista de materiales asignada.")
                        for lmat in lmateriales:
                            purchase_line = self.env['purchase.order.line'].create({
                                'order_id': nueva_cotizacion_compra.id,
                                'product_id': lmat.product_id.id,
                                'name': lmat.product_id.product_tmpl_id.name,
                                'product_qty': lmat.product_qty * line.product_uom_qty,  # Considerar cantidades del paquete
                                'product_uom_id': line.product_uom_id.id,
                                'price_unit': line.costo_proveedor,
                                'sale_order_id': rec.id,
                                'codigo_proveedor': line.codigo_proveedor,
                            })
                            line.write({'purchase_line_ids': [(4, purchase_line.id)]})
                
                # Notificar al usuario
                if rec.user_id:
                    rec.message_post(
                        body=f"Se generó la orden de compra {nueva_cotizacion_compra.name}.",
                        subtype_id=self.env.ref('mail.mt_note').id
                    )
        
        _logger.warning('Finalizó la creación de órdenes de compra.')



    


    detailed_info = fields.Html(
        string="Información de entrega",
        compute='_compute_detailed_info',
        inverse='_set_detailed_info',
        # store=True
    )

    traspaso_name=fields.Char(
        string="Traspaso",
        related="picking_ids.name",
        tracking=True
    )
    
    
    guia=fields.Char(
        string="Guía de rastreo",
        tracking=True
    )
    
    # @api.model
    # def create(self, values):
    #     guia = values.get('guia', self.guia)
    #     if guia:
    #         ventas = rec.env['sale.order'].search([
    #                 ('guia', '=', guia),
    #                 ('guia', 'not in', [False, ""]),
    #                 ('guia', '!=', False),])
    #         if len(ventas) > 0:
    #             raise UserError('El número de guía debe ser único.')
    #     return super(sale_order_inherit, self).create(values)
    
    link_guia=fields.Char(
        string="Link guia",
        tracking=True
    )

    estado_traspaso = fields.Selection([
        ('draft','Borrador'),
        ('waiting','En espera de otra operación'),
        ('confirmed','En espera'),
        ('assigned','Listo'),
        ('done','Hecho'),
        ('cancel','Cancelado'),
    ], string="Estado publicación", related="picking_ids.state", tracking=True, store=True)

    llantas_config_carrier_id=fields.Many2one(
        "llantas_config.carrier",
        string="Carrier"
    )

    @api.depends('picking_ids', 'picking_ids.carrier_tracking_ref')
    def _compute_detailed_info(self):
        for rec in self:
            detailed_info = "<table class='table'>"
            detailed_info += "<tr>"
            detailed_info += "<th>Entrega</th>"
            detailed_info += "<th>Carrier</th>"
            detailed_info += "<th>Guía</th>"
            detailed_info += "<th>Link</th>"
            detailed_info += "<th>Estado</th>"
            detailed_info += "</tr>"
            
            for orden in rec.picking_ids:
                detailed_info += "<tr>"
                detailed_info += "<td>{}</td>".format(orden.display_name)
                detailed_info += "<td>{}</td>".format(orden.carrier.display_name)
                detailed_info += "<td>{}</td>".format(orden.carrier_tracking_ref)
                detailed_info += "<td>{}</td>".format(orden.link_guia)
                detailed_info += "<td>{}</td>".format(orden.state)
                detailed_info += "</tr>"

            detailed_info += "</table>"
            rec.detailed_info = detailed_info

    def _set_detailed_info(self):
        for rec in self:
            # Verifica si el campo 'carrier_tracking_ref' pertenece a 'stock.picking'
            if rec.picking_ids:
                # Tomamos el primer registro de picking_ids y actualizamos su carrier_tracking_ref
                picking = rec.picking_ids[0]
                picking.write({'carrier_tracking_ref': rec.detailed_info})
            # Puedes agregar el código aquí para procesar la entrada del usuario si es necesario
            # Puedes acceder al valor ingresado por el usuario con rec.detailed_info
            pass


    detailed_name=fields.Char(
        string="Folio entrega",
        related="picking_ids.name",
    )

    def crear_actividad(self):
        for rec in self:
            if rec.comprador_id:
                actividad_tipo_id = self.env.ref('mail.mail_activity_data_todo').id
                model_sale_order_id = self.env.ref('sale.model_sale_order').id
                
                existing_activity = rec.env['mail.activity'].search([
                    ('res_model', '=', 'sale.order'),
                    ('res_id', '=', rec.id),
                    ('activity_type_id', '=', actividad_tipo_id),
                    ('user_id', '=', rec.comprador_id.user_id.id if rec.comprador_id.user_id.id else False)
                ])
    
                if not existing_activity:
                    if rec.comprador_id.user_id.id:
                        rec.env['mail.activity'].create({
                            'res_model': 'sale.order',
                            'res_model_id': model_sale_order_id,
                            'res_id': rec.id,
                            'activity_type_id': actividad_tipo_id,
                            'summary': 'Orden de venta pendiente',
                            'date_deadline': fields.Datetime.now(),
                            'user_id': rec.comprador_id.user_id.id,
                            'note': '',
                        })
                    else:
                        raise UserError("Debe seleccionar un usuario de compras válido")
                else:
                    pass

    tipo_factura = fields.Selection([
        ('01','Publico en general'),
        ('02','Cliente')], string="Tipo de facturación", store=True, tracking=True)

    def compute_orden_compra(self):
        for rec in self:
            purchase_orders = rec._get_purchase_orders()
            if purchase_orders:
                # Verifica si hay más de un pedido de compra
                if len(purchase_orders) > 1:
                    _logger.warning(f"Se encontraron múltiples órdenes de compra para {rec.id}. Usando la primera orden de compra.")
                rec.purchase_order_id = purchase_orders[0].id  # Asignar el primer pedido de compra
            else:
                rec.purchase_order_id = False


    purchase_order_id = fields.Many2one(
        'purchase.order',
        compute='compute_orden_compra',
        string='Orden de compra',
        store=True,
    )

    fee_import = fields.Float(string='Fee Import', compute='compute_fee_import', store=True)

    fee_sale = fields.Float(
        string="Cargo por venta",
        compute="_compute_amounts",
        store=True,
    )

    
    def normalize_string(self, s):
        """Elimina acentos y convierte a minúsculas."""
        return ''.join(
            c for c in unicodedata.normalize('NFD', s)
            if unicodedata.category(c) != 'Mn'
        ).lower()


    def compute_fee_import(self):
        for rec in self:
            fee = 0.0  # Valor por defecto si no se encuentra tarifa
    
            if rec.marketplace and rec.yuju_order_data and rec.yuju_marketplace_fee == 0.00:
                # Buscamos el marketplace en la misma compañía
                marketplace = self.env['llantas_config.marketplaces'].search([
                    ('name', 'ilike', rec.marketplace.name),
                    ('company_id', '=', rec.company_id.id)
                ], limit=1)
    
                if marketplace:
                    # Si encontramos el marketplace, obtenemos la tarifa del campo 'fee_marketplace'
                    fee = marketplace.fee_marketplace or 0.0
                else:
                    raise UserError(
                        f"No se encontró un marketplace que coincida con '{rec.marketplace.name}' para la compañía '{rec.company_id.name}'."
                    )
    
            # Asignamos el valor de la tarifa al campo fee_import
            rec.fee_import = fee
    

    
    
    @api.depends('order_line.price_subtotal', 'order_line.price_tax', 'order_line.price_total', 'fee_sale')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        # PRIMERO: Llamar al método base para calcular los montos estándar
        # Esto asegura que amount_untaxed, amount_tax y amount_total se calculen correctamente
        super(sale_order_inherit, self)._compute_amounts()
        
        # SEGUNDO: Agregar nuestra lógica personalizada para fee_sale
        for order in self:
            if order.marketplace and order.yuju_order_data and order.yuju_marketplace_fee == 0.00:
                order.fee_sale = (order.amount_untaxed + order.amount_tax) * order.fee_import

     
class sale_order_line_inherit(models.Model):
    _inherit = 'sale.order.line'
    _description='Lineas de la orden de venta'

    proveedor_id=fields.Many2one(
        "product.supplierinfo",
        # related="product_id.product_tmpl_id.partner_id",
        store=True,
        tracking=True,
    )

    costo_promedio = fields.Float(
        "Costo Promedio",
        store=True
    )

    costo_promedio_historico = fields.Float(
        "Costo promedio historico",
        compute="_compute_costo_promedio_historico",
        # store=True
    )

    @api.depends('product_id', 'order_id.date_order')
    def _compute_costo_promedio_historico(self):
        for line in self:
            costo_promedio_historico = 0.0
            if line.product_id and line.order_id and line.order_id.date_order:
                try:
                    # Intentar primero con stock.valuation.layer
                    if 'stock.valuation.layer' in self.env:
                        valuation_layers = self.env['stock.valuation.layer'].search([
                            ('product_id', '=', line.product_id.id),
                            ('create_date', '<=', line.order_id.date_order)
                        ])
                        
                        if valuation_layers:
                            sum_value = sum(valuation_layers.mapped('value'))
                            sum_qty = sum(valuation_layers.mapped('quantity'))
                            
                            if sum_qty > 0:
                                costo_promedio_historico = sum_value / sum_qty
                            else:
                                costo_promedio_historico = line.product_id.standard_price
                        else:
                            costo_promedio_historico = line.product_id.standard_price
                    else:
                        # Si no existe valuation.layer, usar standard_price
                        costo_promedio_historico = line.product_id.standard_price
                        
                except Exception as e:
                    _logger.warning(f"Error calculando costo histórico: {e}")
                    costo_promedio_historico = line.product_id.standard_price
            else:
                costo_promedio_historico = line.product_id.standard_price if line.product_id else 0.0
    
            line.costo_promedio_historico = costo_promedio_historico
    
    costo_proveedor=fields.Float(
        related="proveedor_id.price",
        string="Costo",
        tracking=True,
    )
    
    
    @api.depends('purchase_line_ids')
    def compute_costo_proveedor_total(self):
        for rec in self:
            costo_proveedor_total = sum(line.price_unit for line in rec.purchase_line_ids)
            rec.costo_proveedor_total = costo_proveedor_total

    @api.onchange('proveedor_id')
    def _onchange_proveedor_id(self):
        for line in self:
            if line.proveedor_id:
                # Solo validar si existe_actual está definido y es mayor a 0
                if hasattr(line.proveedor_id, 'existencia_actual'):
                    existencia = line.proveedor_id.existencia_actual or 0
                    
                    # Si existencia_actual es 0, probablemente no está calculado
                    if existencia == 0:
                        _logger.warning(f"existencia_actual es 0 para {line.proveedor_id.partner_id.name}")
                        # No bloquear, solo advertir
                        continue
                    
                    if existencia < line.product_uom_qty:
                        raise UserError(
                            f"El proveedor '{line.proveedor_id.partner_id.name}' no tiene suficiente cantidad disponible "
                            f"({existencia}) para cubrir la cantidad requerida ({line.product_uom_qty})."
                        )
        
    # def compute_costo_proveedor_total(self):
    #     for rec in self:
    #         if rec.costo_proveedor:
    #             costo_proveedor_total = rec.costo_proveedor * rec.product_uom_qty
    #         rec.write({'costo_proveedor_total': costo_proveedor_total})
            
    costo_proveedor_total=fields.Float(
        compute="compute_costo_proveedor_total",
        string="Costo total",
        store=True,
    )

    

    costo_proveedor_2=fields.Float(
        string="Costo proveedor guardado",
    )

    
    codigo_proveedor=fields.Char(
        related="proveedor_id.product_code",
        string="Codigo proveedor",
        trackin=True,
    )

    importe_descuento=fields.Float(
        string="Importe descuento",
    )

    def compute_precio_antes_dec(self):
        for rec in self:
            rec.precio_antes_dec = rec.price_unit + rec.importe_descuento
    precio_antes_dec=fields.Float(
        string="Precio antes descuento",
        compute=compute_precio_antes_dec,
    )

    # @api.onchange('product_id', 'price_unit')
    # def _onchange_product_id_check_stock(self):

    #     # Obtener ubicaciones internas donde existe el producto
    #     locations = []
    #     warehouse_id = False

    #     for quant in self.product_id.stock_quant_ids:
    #         # Verificar que la ubicación sea interna y tenga inventario
    #         if quant.quantity > 0 and quant.location_id.usage == 'internal':
    #             locations.append(quant.location_id.display_name)

    #             # Obtener el warehouse_id de la ubicación si aún no se ha asignado
    #             if quant.location_id.location_id:
    #                 warehouse_id = quant.location_id.location_id.warehouse_id.id
    #                 break  # Terminar el loop al encontrar un warehouse_id válido

    #     if locations:
    #         # Si hay ubicaciones internas con inventario, asignamos el warehouse_id
    #         self.write({'warehouse_id': warehouse_id})
    #     else:
    #         # Si no hay existencia, asignar el almacén predeterminado
    #         default_warehouse = self.env['stock.warehouse'].search(
    #             [('name', '=', 'ALMACEN LLANTIRED- 3PL VIRTUAL')],
    #             limit=1
    #         )
    #         if default_warehouse:
    #             # Asignar el almacén predeterminado
    #             self.write({'warehouse_id': default_warehouse.id})
            
    @api.onchange('product_id')
    def onchange_product_id_for_llantas_config(self):
        if self.product_id.id:
            self.name = self.product_id.name

    marketplace_id = fields.Char(
        string="Canal de venta",
        compute="_compute_marketplace_id",
        store=True
    )

    @api.depends('order_id.marketplace.name')
    def _compute_marketplace_id(self):
        for line in self:
            line.marketplace_id = line.order_id.marketplace.name
    
    link_venta=fields.Char(
        string="Link de venta",
        related="order_id.link_venta",
        store=True
    )
    folio_venta=fields.Char(
        string="Folio de venta",
        related="order_id.folio_venta",
        store=True
    )
    ganancia= fields.Float(
        string="Ganancia",
        related="order_id.ganancia",
    )
    
    margin_percent= fields.Float(
        string="Margen de ganancia",
        related="order_id.margin_percent",
    )
    
    fecha_venta=fields.Datetime(
        string="Fecha venta",
        related="order_id.fecha_venta",
        store=True
    )
    partner_id=fields.Many2one(
        string="Cliente",
        related="order_id.partner_id",
        store=True,
    )
    comprador=fields.Char(
        string="Comprador",
        related="order_id.comprador_id.name",
        store=True
    )
    estado_venta=fields.Selection([
        ('01','Pendiente'),
        ('02','Debito en curso'),
        ('03','Traspaso'),
        ('04','Guia pendiente'),
        ('05','Enviado'),
        ('06','Entregado'),
        ('07','Cerrado'),
        ('08','Incidencia'),
        ('09','Devolución'),], string="Estatus", related="order_id.ventas_status", store=True)
    
    comision=fields.Float(
        string="Comisión",
        related="order_id.comision",
        store=True
    )
    envio=fields.Float(
        string="Envio",
        related="order_id.envio",
        store=True
    )

    nombre_producto=fields.Char(
        string="Producto",
        related="product_id.product_tmpl_id.name",
        store=True,
        # company_dependent=True,
    )

    codigo_prod=fields.Char(
        string="sku",
        related="product_id.product_tmpl_id.default_code",
        store=True
    )
    #Listas de precios
    @api.onchange('product_id','proveedor_id')
    def onchange_product_id_for_llantired(self):
        if self.product_id.id and self.order_id.id and self.order_id.partner_id.id and self.order_id.pricelist_id.id:
            self.price_unit = self.pricelist_item_id._compute_price(self.product_id, self.product_uom_qty, self.product_uom_id, self.order_id.date_order, self.order_id.currency_id, self.costo_proveedor)


    is_killer = fields.Boolean(
        string="Es killer?",
        compute='_compute_killer',
        store=True,
        default=False,
    )
    
    killer_id = fields.Many2one(
        'llantas_config.killer_list',
        string="Killer ID",
        compute='_compute_killer',
        store=True,
    )
    
    killer_id_killer_price = fields.Float(
        string="Precio killer",
        store=True,
    )
    
    killer_id_base_price = fields.Float(
        string="Precio base killer",
        store=True,
    )
    
    killer_id_promotion_price = fields.Float(
        string="Precio de promoción killer",
        store=True,
    )
    
    total_con_killer = fields.Float(
        string="Total con killer",
        compute='_compute_total_con_killer',
        store=True,
    )
    
    @api.depends('product_id', 'order_id.marketplace')
    def _compute_killer(self):
        fecha_actual = datetime.now()  # Obtener la fecha actual
        for line in self:
            # Filtrar los registros 'killer' activos y válidos para la fecha actual
            killers = line.product_id.product_tmpl_id.killer_ids.filtered(
                lambda k: k.marketplace_id == line.order_id.marketplace and
                          k.initial_date and 
                          k.initial_date <= fecha_actual <= (k.final_date or fecha_actual) and
                          k.status == 'active'
            )
            # Asignar el primer registro que cumpla con los criterios o None si no hay
            killer = killers[:1] if killers else None
            line.killer_id = killer.id if killer else None
            line.is_killer = bool(killer)
    
            if killer:
                # Guardar los valores directamente en los campos persistentes
                line.killer_id_killer_price = killer.killer_price
                line.killer_id_base_price = killer.base_price
                line.killer_id_promotion_price = killer.promotion_price
    
                # Si cumple la condición de killer, actualizar price_unit con el precio de promoción
                line.price_unit = line.killer_id_promotion_price
            else:
                # Limpiar los valores si no hay killer aplicable
                line.killer_id_killer_price = 0.0
                line.killer_id_base_price = 0.0
                line.killer_id_promotion_price = 0.0
    
    @api.depends('price_total', 'killer_id_killer_price')
    def _compute_total_con_killer(self):
        for rec in self:
            # Calcular el total considerando el precio killer si es aplicable
            rec.total_con_killer = rec.price_total + (rec.killer_id_killer_price or 0)

    
        
    link_venta=fields.Char(
        string="Link de venta",
        store=True
    )

    @api.depends('purchase_line_ids', 'purchase_line_ids.price_unit')
    def compute_costo_orden_compra(self):
        for rec in self:
            costo_orden_compra = 0
            for purchase_line in rec.purchase_line_ids:
                costo_orden_compra += purchase_line.price_unit * purchase_line.product_uom_qty  # Sumar el costo total de la orden de compra
            rec.costo_orden_compra = costo_orden_compra
    
    costo_orden_compra = fields.Float(
        compute=compute_costo_orden_compra,
        string="Costo Orden de Compra",
        store=False,  # Cambiado a False si no necesitas almacenar el valor
    )

    @api.depends('purchase_line_ids', 'purchase_line_ids.invoice_lines', 'purchase_line_ids.invoice_lines.quantity', 'purchase_line_ids.invoice_lines.price_unit')
    def compute_costo_orden_facturada(self):
        for rec in self:
            costo_orden_facturada = 0
            for purchase_line in rec.purchase_line_ids:
                for invoice_line in purchase_line.invoice_lines:
                    costo_orden_facturada += (invoice_line.price_unit * invoice_line.quantity)  # Acumular el costo facturado
            rec.costo_orden_facturada = costo_orden_facturada
    
    costo_orden_facturada = fields.Float(
        string="Costo Orden Facturada",
        compute=compute_costo_orden_facturada,
        store=False,  # Cambiado a False si no necesitas almacenar el valor
    )

    order_id=fields.Many2one(
        "sale.order",
        string="Orden de venta",
        store=True,
    )


    @api.depends('envio', 'comision', 'order_id', 'order_id.amount_untaxed', 'costo_orden_facturada', 'costo_orden_compra', 'killer_id_killer_price')
    def _compute_t1(self):
        for rec in self:
            # Inicializamos las variables
            t1 = t2 = t3 = 0
            t1_porcentaje = t2_porcentaje = t3_porcentaje = "0.00%"
    
            if rec.order_id and rec.killer_id_killer_price and rec.order_id.amount_untaxed != 0:
                killer_price = rec.killer_id_killer_price
                
                # Cálculo para T1
                t1 = (rec.order_id.amount_untaxed - (rec.comision / 1.16) - (rec.envio / 1.16) + (killer_price / 1.16) - rec.product_id.standard_price)
                t1_porcentaje = "{:.2f}%".format((t1 / rec.order_id.amount_untaxed) * 100)
    
                # Cálculo para T2 (solo si hay costo de orden de compra)
                if rec.costo_orden_compra > 0:
                    t2 = (rec.order_id.amount_untaxed - (rec.comision / 1.16) - (rec.envio / 1.16) + (killer_price / 1.16) - rec.costo_orden_compra)
                    t2_porcentaje = "{:.2f}%".format((t2 / rec.order_id.amount_untaxed) * 100)
    
                # Cálculo para T3 (solo si hay costo facturado)
                if rec.costo_orden_facturada > 0:
                    t3 = (rec.order_id.amount_untaxed - (rec.comision / 1.16) - (rec.envio / 1.16) + (killer_price / 1.16) - rec.costo_orden_facturada)
                    t3_porcentaje = "{:.2f}%".format((t3 / rec.order_id.amount_untaxed) * 100)
    
            # Asignar valores a los campos
            rec.t1 = t1
            rec.t2 = t2
            rec.t3 = t3
            rec.t1_porcentaje = t1_porcentaje
            rec.t2_porcentaje = t2_porcentaje
            rec.t3_porcentaje = t3_porcentaje


    t1=fields.Float(
        string="T1",
        compute="_compute_t1",
        store=True,
    )

    t1_porcentaje=fields.Char(
        string="T1 %",
        compute="_compute_t1",
        store=True,
        

    )

    t2=fields.Float(
        string="T2",
        compute="_compute_t1",
        store=True,


    )

    t2_porcentaje=fields.Char(
        string="T2 %",
        compute="_compute_t1",
        store=True,

    )

    t3=fields.Float(
        string="T3",
        compute="_compute_t1",
        store=True,


    )

    t3_porcentaje=fields.Char(
        string="T3 %",
        compute="_compute_t1",
        store=True,

    )
    


    
           
