# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import os
import csv
from odoo.exceptions import ValidationError , UserError

_EFOS_DOWNLOAD_PATH_ROOT = '/home/odoo/data/filestore/EFOS/'

class l10n_mx_cfdi_fiel(models.Model):
    _name = 'l10n_mx.efos'
    _description = 'Modelo para efos'
    
    partner_id = fields.Many2one(
        'res.partner',
        string="Contribuyente"
    )  
    
    partner_id_vat = fields.Char(
        string="RFC del contribuyente",
        related="partner_id.vat",
        store=True
    )    
    
    rfc = fields.Char(
        string="RFC"
    )
    
    contribuyente = fields.Char(
        string="Nombre del contribuyente"
    )
    
    status = fields.Char(
        string="Situación del contribuyente"
    )
    
    presunto_sat_char = fields.Char(
        string="Número y fecha de oficio global de presución SAT"
    )
    
    presunto_sat_date = fields.Char(
        string="Publicación página SAT presuntos"
    )
    
    presunto_dof_char = fields.Char(
        string="Número y fecha de oficio global de presución DOF"
    )
    
    presunto_dof_date = fields.Char(
        string="Publicación DOF presuntos"
    )
    
    desvirtuado_sat_char = fields.Char(
        string="Número y fecha de oficio global de contribuyentes que desvirtuaron SAT"
    )
    
    desvirtuado_sat_date = fields.Char(
        string="Publicación página SAT desvirtuados"
    )
    
    desvirtuado_dof_char = fields.Char(
        string="Número y fecha de oficio global de contribuyentes que desvirtuaron DOF"
    )
    
    desvirtuado_dof_date = fields.Char(
        string="Publicación DOF desvirtuados"
    )
    
    definitivo_sat_char = fields.Char(
        string="Número y fecha de oficio global de definitivos SAT"
    )
    
    definitivo_sat_date = fields.Char(
        string="Publicación página SAT definitivos"
    )
    
    definitivo_dof_char = fields.Char(
        string="Número y fecha de oficio global de definitivos DOF"
    )
    
    definitivo_dof_date = fields.Char(
        string="Publicación DOF definitivos"
    )
    
    favorable_sat_char = fields.Char(
        string="Número y fecha de oficio global de sentencia favorable SAT"
    )
    
    favorable_sat_date = fields.Char(
        string="Publicación página SAT sentencia favorable"
    )
    
    favorable_dof_char = fields.Char(
        string="Número y fecha de oficio global de sentencia favorable DOF"
    )
    
    favorable_dof_date = fields.Char(
        string="Publicación DOF sentencia favorable"
    )
    
    def download_efos_list_sat(self):
        if not os.path.exists(_EFOS_DOWNLOAD_PATH_ROOT):
            os.makedirs(_EFOS_DOWNLOAD_PATH_ROOT)
        
        url = 'http://omawww.sat.gob.mx/cifras_sat/Documents/Listado_Completo_69-B.csv'
        r = requests.get(url, allow_redirects=True)
        filename = url.split('/')[-1]
        open(_EFOS_DOWNLOAD_PATH_ROOT+filename, 'wb').write(r.content)
        
        efos_ids = self.env['l10n_mx.efos'].search([])
        for efos in efos_ids:
            efos.unlink()
        
        datafile = open(_EFOS_DOWNLOAD_PATH_ROOT+filename, 'r', encoding='latin-1')
        myreader = csv.reader(datafile)
        m = ""
        c = 0
        for line in myreader:
            c += 1
            if c >= 4:
                m += str(len(line)) + " -->  " + str(line) + "\n"
                partner = False
                partners = self.env['res.partner'].search([('vat','=',line[1]),('is_company','=',True)], limit=1)
                if len(partners) > 0:
                    partner = partners[0].id
                self.env['l10n_mx.efos'].create({
                    'partner_id': partner,
                    'rfc': line[1],
                    'contribuyente': line[2],
                    'status': line[3],
                    'presunto_sat_char': line[4],
                    'presunto_sat_date': line[5],
                    'presunto_dof_char': line[6],
                    'presunto_dof_date': line[7],
                    'desvirtuado_sat_char': line[8],
                    'desvirtuado_sat_date': line[9],
                    'desvirtuado_dof_char': line[10],
                    'desvirtuado_dof_date': line[11],
                    'definitivo_sat_char': line[12],
                    'definitivo_sat_date': line[13],
                    'definitivo_dof_char': line[14],
                    'definitivo_dof_date': line[15],
                    'favorable_sat_char': line[16],
                    'favorable_sat_date': line[17],
                    'favorable_dof_char': line[18],
                    'favorable_dof_date': line[19],
                })