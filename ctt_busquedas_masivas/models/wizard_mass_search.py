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
            return

        # Determinar el operador de búsqueda
        operator = '=' if self.use_exact_match else 'ilike'

        # Construir el dominio
        search_field = self.search_field
        
        # Para campos Many2one, buscar por nombre
        many2one_fields = ['partner_id', 'user_id', 'team_id', 'comprador_id', 
                          'company_id', 'warehouse_id']
        
        if search_field in many2one_fields:
            domain = []
            for valor in valores:
                domain.append('|')
                domain.append((search_field, operator, valor))
            if domain and domain[-1] == '|':
                domain.pop()
        else:
            if len(valores) == 1:
                domain = [(search_field, operator, valores[0])]
            else:
                domain = ['|'] * (len(valores) - 1) + [(search_field, operator, valor) for valor in valores]

        if not domain:
            return

        # Buscar las órdenes
        orders = self.env['sale.order'].search(domain)
        
        if not orders:
            field_name = dict(self._fields['search_field'].selection).get(search_field, search_field)
            return {
                'warning': {
                    'title': 'Sin resultados',
                    'message': f'No se encontraron órdenes en el campo "{field_name}" con los valores proporcionados.',
                }
            }

        # Actualizar el wizard con los resultados
        self.write({'order_ids': [(6, 0, orders.ids)]})
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    def action_open_orders(self):
        """Abrir las órdenes encontradas en una lista"""
        if not self.order_ids:
            return
            
        return {
            'type': 'ir.actions.act_window',
            'name': f'Órdenes de Venta Encontradas ({self.result_count})',
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.order_ids.ids)],
            'target': 'current',
        }
    
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