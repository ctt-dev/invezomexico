from odoo import models, fields, api
from odoo.exceptions import UserError

class InvoiceMassSearchWizard(models.TransientModel):
    _name = 'ctt.busquedas.masivas.invoice.wizard'
    _description = 'Wizard for Mass Search of Invoices'

    search_field = fields.Selection([
        # Campos principales de factura
        ('name', 'Número de Factura'),
        ('ref', 'Referencia/Folio'),
        ('invoice_origin', 'Origen (Orden de Venta)'),
        
        # Campos de cliente
        ('partner_id', 'Cliente'),
        ('user_id', 'Vendedor'),
        ('team_id', 'Equipo de Ventas'),
        ('company_id', 'Compañía'),
        
        # Campos de factura
        ('invoice_date', 'Fecha de Factura'),
        ('invoice_date_due', 'Fecha de Vencimiento'),
        ('currency_id', 'Moneda'),
        
        # Campos de estado
        ('state', 'Estado'),
        ('payment_state', 'Estado de Pago'),
        ('invoice_payment_state', 'Estado de Pago (Legacy)'),
        
        # Campos de tipo
        ('move_type', 'Tipo de Factura'),
        
        # Campos de marketplace (si los tienes)
        ('marketplace_name', 'Marketplace'),
        ('folio_venta', 'No. Venta'),
        
        # Campos financieros
        ('amount_untaxed', 'Monto sin Impuestos'),
        ('amount_tax', 'Monto de Impuestos'),
        ('amount_total', 'Monto Total'),
        
        # Otros
        ('narration', 'Notas'),
        ('payment_reference', 'Referencia de Pago'),
    ], string='Campo a buscar', default='name', required=True)
    
    invoice_values = fields.Text(
        string='Valores a buscar',
        placeholder='Ingrese valores separados por comas (,) o por línea\nEjemplo: INV001, INV002, INV003',
        help='Cada valor se buscará de forma independiente (operador OR)'
    )
    
    use_exact_match = fields.Boolean(
        string='Búsqueda exacta',
        help='Si está activado, busca coincidencias exactas. Si no, busca que contenga el texto.'
    )
    
    invoice_ids = fields.Many2many('account.move', string='Facturas Encontradas', readonly=True)
    result_count = fields.Integer(string='Resultados encontrados', compute='_compute_result_count')
    
    @api.depends('invoice_ids')
    def _compute_result_count(self):
        for rec in self:
            rec.result_count = len(rec.invoice_ids)

    def action_search_multiple_invoices(self):
        """Buscar y mostrar resultados en el mismo wizard"""
        if not self.invoice_values:
            return {
                'warning': {
                    'title': 'Campos vacíos',
                    'message': 'Debe ingresar al menos un valor para buscar.',
                }
            }

        # Procesar los valores
        valores = []
        for linea in self.invoice_values.replace('\n', ',').split(','):
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
        many2one_fields = ['partner_id', 'user_id', 'team_id', 'company_id', 'currency_id']
        
        # Campos numéricos
        numeric_fields = ['amount_untaxed', 'amount_tax', 'amount_total']
        
        if search_field in many2one_fields:
            domain = []
            for valor in valores:
                domain.append('|')
                domain.append((search_field, operator, valor))
            if domain and domain[-1] == '|':
                domain.pop()
        elif search_field in numeric_fields:
            # Para campos numéricos, intentar convertir a float
            float_valores = []
            for valor in valores:
                try:
                    float_valores.append(float(valor))
                except ValueError:
                    pass
            if float_valores:
                if len(float_valores) == 1:
                    domain = [(search_field, '=', float_valores[0])]
                else:
                    domain = ['|'] * (len(float_valores) - 1) + [(search_field, '=', val) for val in float_valores]
            else:
                domain = []
        else:
            if len(valores) == 1:
                domain = [(search_field, operator, valores[0])]
            else:
                domain = ['|'] * (len(valores) - 1) + [(search_field, operator, valor) for valor in valores]

        if not domain:
            return

        # Buscar las facturas
        invoices = self.env['account.move'].search(domain)
        
        if not invoices:
            field_name = dict(self._fields['search_field'].selection).get(search_field, search_field)
            return {
                'warning': {
                    'title': 'Sin resultados',
                    'message': f'No se encontraron facturas en el campo "{field_name}" con los valores proporcionados.',
                }
            }

        # Actualizar el wizard con los resultados
        self.write({'invoice_ids': [(6, 0, invoices.ids)]})
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    def action_open_invoices(self):
        """Abrir las facturas encontradas"""
    
        if not self.invoice_ids:
            return
    
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
    
        action['domain'] = [('id', 'in', self.invoice_ids.ids)]
    
        action['context'] = {
            'default_move_type': 'out_invoice',
            'search_default_posted': 0,
            'create': False,
        }
    
        return action
    
    def action_clear_results(self):
        """Limpiar los resultados de búsqueda"""
        self.write({'invoice_ids': [(5, 0, 0)], 'invoice_values': ''})
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }