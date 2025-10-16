# file: vit_contract_inherit/models/res_partner.py

from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    kanwil_id = fields.Many2one(
        'vit.kanwil',
        string='Kanwil',
    )

    kanca_id = fields.Many2one(
        'vit.kanca',
        string='Kanca',
    )
