from odoo import models, fields, api, _
import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
_logger = logging.getLogger(__name__)
import datetime

class PosSessionCreditLimit(models.Model):
    _inherit = 'pos.session'

    def require_approve_credit(self, order_name, cashier_id, employee_id):
        for rec in self:
            
            order = self.env['pos.order'].search([('pos_reference', '=', order_name)])
            emp = self.env['hr.employee'].search([('id', '=', employee_id)])
            
            actividad_tipo_id = rec.env.ref('mail.mail_activity_data_todo').id
            model_pos_order_id = rec.env.ref('point_of_sale.model_pos_order').id
            
            existing_activity = rec.env['mail.activity'].search([
                ('res_model', '=', 'pos.order'),
                ('res_id', '=', order.id),
                ('activity_type_id', '=', actividad_tipo_id),
                ('user_id', '=', employee_id if employee_id else False)
            ])
            
            if not existing_activity:
                if cashier_id:
                    rec.env['mail.activity'].create({
                        'res_model': 'pos.order',
                        'res_model_id': model_pos_order_id,
                        'res_id': order.id,
                        'activity_type_id': actividad_tipo_id,
                        'summary': 'Aprobar crédito pendiente',
                        'date_deadline': fields.Datetime.now(),
                        'user_id': emp.user_id.id,
                        'note': '',
                    })

    def require_approve_discount(self, order_name, cashier_id, employee_id):
        for rec in self:
            
            order = self.env['pos.order'].search([('pos_reference', '=', order_name)])
            emp = self.env['hr.employee'].search([('id', '=', employee_id)])
            
            actividad_tipo_id = rec.env.ref('mail.mail_activity_data_todo').id
            model_pos_order_id = rec.env.ref('point_of_sale.model_pos_order').id
            
            existing_activity = rec.env['mail.activity'].search([
                ('res_model', '=', 'pos.order'),
                ('res_id', '=', order.id),
                ('activity_type_id', '=', actividad_tipo_id),
                ('user_id', '=', employee_id if employee_id else False)
            ])
            
            if not existing_activity:
                if cashier_id:
                    rec.env['mail.activity'].create({
                        'res_model': 'pos.order',
                        'res_model_id': model_pos_order_id,
                        'res_id': order.id,
                        'activity_type_id': actividad_tipo_id,
                        'summary': 'Aprobar descuento',
                        'date_deadline': fields.Datetime.now(),
                        'user_id': emp.user_id.id,
                        'note': '',
                    })


    def _pos_data_process(self, loaded_data):
        super()._pos_data_process(loaded_data)
        if self.config_id.module_pos_hr:
            loaded_data['approbation_employee_by_id'] = {employee['id']: employee for employee in loaded_data['approbation.hr.employee']}
    
    @api.model
    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        if self.config_id.module_pos_hr:
            new_model = 'approbation.hr.employee'
            if new_model not in result:
                result.append(new_model)
        return result
        
    def _loader_params_approbation_hr_employee(self):
        if len(self.config_id.employee_ids) > 0:
            domain = ['&', ('company_id', '=', self.config_id.company_id.id), '|', ('user_id', '=', self.user_id.id), ('id', 'in', self.config_id.approbation_employee_ids.ids)]
        else:
            domain = [('company_id', '=', self.config_id.company_id.id)]
        return {'search_params': {'domain': domain, 'fields': ['name', 'id', 'user_id'], 'load': False}}

    def _get_pos_ui_approbation_hr_employee(self, params):
        app_employees = self.env['hr.employee'].search_read(**params['search_params'])
        app_employee_ids = [employee['id'] for employee in app_employees]
        user_ids = [employee['user_id'] for employee in app_employees if employee['user_id']]
        manager_ids = self.env['res.users'].browse(user_ids).filtered(lambda user: self.config_id.group_pos_manager_id in user.groups_id).mapped('id')

        employees_barcode_pin = self.env['hr.employee'].browse(app_employee_ids).get_barcodes_and_pin_hashed()
        bp_per_employee_id = {bp_e['id']: bp_e for bp_e in employees_barcode_pin}
        for app_employee in app_employees:
            app_employee['role'] = 'manager' if app_employee['user_id'] and app_employee['user_id'] in manager_ids else 'cashier'
            app_employee['barcode'] = bp_per_employee_id[app_employee['id']]['barcode']
            app_employee['pin'] = bp_per_employee_id[app_employee['id']]['pin']

        return app_employees

    
    
    @api.model
    def _loader_params_hr_employee(self):
        result = super()._loader_params_hr_employee()
        _logger.warning("PARAMS2")
        result['search_params']['fields'].append('allow_credit_sale')
        result['search_params']['fields'].append('allow_aplazo')
        return result

    @api.model
    def _loader_params_pos_payment_method(self):
        result = super()._loader_params_pos_payment_method()
        result['search_params']['fields'].append('is_credit')
        return result

    @api.model
    def _loader_params_res_partner(self):
        result = super()._loader_params_res_partner()
        result['search_params']['fields'].append('active_limit')
        result['search_params']['fields'].append('blocking_stage')
        result['search_params']['fields'].append('warning_stage')
        result['search_params']['fields'].append('credit_used')
        result['search_params']['fields'].append('aplazo_actual')
        result['search_params']['fields'].append('deny_credit')
        return result
    
    def get_partner_credit(self, partner_id):
        partner = self.env['res.partner'].browse(partner_id)
        return str(partner.credit)+"/"+str(partner.aplazo_actual)+"/"+str(partner.active_limit)

    def validate_approve_credit(self, order_name):
        _logger.warning(order_name)
        order = self.env['pos.order'].search([('pos_reference','=', order_name),('state','=','draft')])
        _logger.warning(order)
        return order.approve_credit_payment

    def create_postponement(self, partner_id, limit_date, motivo, solicito, aprobo):
        order = self.env['ctt_pos_credit_limit.debt_postponement'].create({
                'partner' : partner_id,
                'limit_date' : limit_date,
                'motive' : motivo,
                'request' : solicito,
                'authorized' : aprobo
        })
        return order

class PosConfigCreditLimit(models.Model):
    _inherit = 'pos.config'

    approbation_employee_ids = fields.Many2many(
        'hr.employee', 'hr_employee_approbation_rel', string="Empleados con permiso a autorizar credito/descuento")