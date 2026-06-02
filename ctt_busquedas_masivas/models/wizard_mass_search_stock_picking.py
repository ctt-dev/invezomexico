from odoo import models, fields, api
from odoo.exceptions import UserError


class StockPickingMassSearchWizard(models.TransientModel):
    _name = 'ctt.busquedas.masivas.stock.picking.wizard'
    _description = 'Wizard for Mass Search of Stock Pickings'

    search_field = fields.Selection([
        ('name', 'Transferencia'),
        ('origin', 'Origen'),
        ('reference', 'Referencia'),
        ('partner_id', 'Contacto'),
        ('carrier_id', 'Transportista'),
        ('picking_type_id', 'Tipo de Operación'),
        ('location_id', 'Ubicación Origen'),
        ('location_dest_id', 'Ubicación Destino'),
        ('state', 'Estado'),
        ('company_id', 'Compañía'),
    ], string='Campo a buscar',
       default='name',
       required=True)

    picking_values = fields.Text(
        string='Valores a buscar',
        placeholder='Ingrese valores separados por coma o por línea'
    )

    use_exact_match = fields.Boolean(
        string='Búsqueda exacta'
    )

    picking_ids = fields.Many2many(
        'stock.picking',
        string='Transferencias Encontradas',
        readonly=True
    )

    result_count = fields.Integer(
        compute='_compute_result_count'
    )

    @api.depends('picking_ids')
    def _compute_result_count(self):
        for rec in self:
            rec.result_count = len(rec.picking_ids)

    def action_search_multiple_pickings(self):
        self.ensure_one()

        if not self.picking_values:
            raise UserError('Debe ingresar al menos un valor.')

        # Procesar valores (soporta coma, nueva línea, punto y coma)
        valores = []
        for linea in self.picking_values.replace('\n', ',').replace(';', ',').split(','):
            valor = linea.strip()
            if valor:
                valores.append(valor)

        if not valores:
            raise UserError('No se encontraron valores válidos para buscar.')

        operator = '=' if self.use_exact_match else 'ilike'
        search_field = self.search_field

        # Construir dominio correctamente
        domain = []
        
        if len(valores) == 1:
            domain = [(search_field, operator, valores[0])]
        else:
            # Construir dominio con operadores OR
            sub_domains = [(search_field, operator, valor) for valor in valores]
            domain = ['|'] * (len(valores) - 1) + sub_domains

        pickings = self.env['stock.picking'].search(domain)

        if not pickings:
            raise UserError('No se encontraron transferencias.')

        self.write({
            'picking_ids': [(6, 0, pickings.ids)]
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_open_pickings(self):
        self.ensure_one()

        if not self.picking_ids:
            raise UserError('No hay transferencias para mostrar.')

        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")
        
        action['domain'] = [('id', 'in', self.picking_ids.ids)]
        action['view_mode'] = 'tree,form'
        
        return action

    def action_clear_results(self):
        self.ensure_one()
        
        self.write({
            'picking_ids': [(5, 0, 0)],
            'picking_values': '',
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }