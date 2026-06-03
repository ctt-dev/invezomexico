from odoo import models, fields, api
from odoo.exceptions import UserError

class SaleOrderMassSearchWizard(models.TransientModel):
    _name = 'ctt.busquedas.masivas.wizard'
    _description = 'Wizard for Mass Search of Sale Orders'

    search_field = fields.Selection([
        # Campos principales
        ('name', 'Número de Orden (Folio)'),
        ('folio_venta', 'No. Venta (Campo personalizado)'),
        ('client_order_ref', 'Referencia del Cliente'),
        
        # Campos de cliente y ventas
        ('partner_id', 'Cliente'),
        ('user_id', 'Vendedor'),
        ('comprador_id', 'Comprador'),
        ('team_id', 'Equipo de Ventas'),
        
        # Campos de marketplace
        ('marketplace_name', 'Marketplace'),
        ('channel_order_reference', 'Referencia del Canal'),
        ('origin', 'Origen'),
        
        # Campos de envío
        ('guia', 'Guía de rastreo'),
        ('warehouse_id', 'Almacén'),
        
        # Campos de estado
        # ('state', 'Estado de la Orden'),
        # ('ventas_status', 'Estado de la Venta'),
        # ('invoice_status', 'Estado de Facturación'),
        # ('is_check', 'Disponibilidad Verificada'),
        # ('es_killer', 'Es Killer'),
        # ('es_venta_directa', 'Es Venta Directa'),
        
        # Campos financieros
        ('comision', 'Comisión'),
        ('envio', 'Envío'),
        
        # Fechas
        ('date_order', 'Fecha de Orden'),
        ('fecha_venta', 'Fecha de Venta'),
        
        # Otros
        ('company_id', 'Compañía'),
        ('tipo_factura', 'Tipo de Facturación'),
        ('link_venta', 'Link de Venta'),
    ], string='Campo a buscar', default='name', required=True)
    
    sale_order_names = fields.Text(
        string='Valores a buscar',
        placeholder='Ingrese valores separados por comas (,) o por línea\nEjemplo: SO001, SO002, SO003',
        help='Cada valor se buscará de forma independiente (operador OR)'
    )
    
    use_exact_match = fields.Boolean(
        string='Búsqueda exacta',
        help='Si está activado, busca coincidencias exactas. Si no, busca que contenga el texto.'
    )
    
    order_ids = fields.Many2many('sale.order', string='Órdenes Encontradas', readonly=True)
    result_count = fields.Integer(string='Resultados encontrados', compute='_compute_result_count')
    
    @api.depends('order_ids')
    def _compute_result_count(self):
        for rec in self:
            rec.result_count = len(rec.order_ids)

    def action_search_multiple_sales_orders(self):
        """Buscar y mostrar resultados en el mismo wizard"""
        if not self.sale_order_names:
            return {
                'warning': {
                    'title': 'Campos vacíos',
                    'message': 'Debe ingresar al menos un valor para buscar.',
                }
            }
    
        # Procesar los valores
        valores = []
        for linea in self.sale_order_names.replace('\n', ',').split(','):
            valor = linea.strip()
            if valor:
                valores.append(valor)
    
        if not valores:
            return {
                'warning': {
                    'title': 'Campos vacíos',
                    'message': 'Debe ingresar al menos un valor válido para buscar.',
                }
            }
    
        # Determinar el operador de búsqueda
        operator = '=' if self.use_exact_match else 'ilike'
    
        # Campo seleccionado
        search_field = self.search_field
    
        # Campos Many2one y su campo name relacionado
        many2one_fields = {
            'partner_id': 'partner_id.name',
            'user_id': 'user_id.name',
            'team_id': 'team_id.name',
            'comprador_id': 'comprador_id.name',
            'company_id': 'company_id.name',
            'warehouse_id': 'warehouse_id.name',
        }
    
        # Determinar el campo real a buscar
        field_to_search = many2one_fields.get(search_field, search_field)
    
        # Construir dominio OR
        if len(valores) == 1:
            domain = [(field_to_search, operator, valores[0])]
        else:
            domain = ['|'] * (len(valores) - 1)
            domain += [
                (field_to_search, operator, valor)
                for valor in valores
            ]
    
        # Buscar órdenes
        orders = self.env['sale.order'].search(domain)
    
        if not orders:
            field_name = dict(
                self._fields['search_field'].selection
            ).get(search_field, search_field)
    
            return {
                'warning': {
                    'title': 'Sin resultados',
                    'message': (
                        f'No se encontraron órdenes en el campo '
                        f'"{field_name}" con los valores proporcionados.'
                    ),
                }
            }
    
        # Actualizar wizard
        self.write({
            'order_ids': [(6, 0, orders.ids)]
        })
    
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    def action_open_orders(self):
        """Abrir las órdenes encontradas"""
    
        if not self.order_ids:
            return
    
        action = self.env.ref('sale.action_orders').read()[0]
    
        action['domain'] = [('id', 'in', self.order_ids.ids)]
    
        action['context'] = {
            'search_default_my_quotation': 0,
            'search_default_draft': 0,
            'search_default_sent': 0,
        }
    
        return action
    
    def action_clear_results(self):
        """Limpiar los resultados de búsqueda"""
        self.write({'order_ids': [(5, 0, 0)], 'sale_order_names': ''})
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }