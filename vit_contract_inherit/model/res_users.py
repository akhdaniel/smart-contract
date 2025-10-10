from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    kanca_id = fields.Many2one(
        'vit.kanca',
        string='Kanca',
    )


    kanwil_id = fields.Many2one(
        'vit.kanwil', 
        string='Kanwil'
    )

    is_kanca_group = fields.Boolean(
        string='Is Kanca Group',
        compute='_compute_is_kanca_group',
        store=True,
    )


    is_kanwil_group = fields.Boolean(
        string='Is Kanwil Group', 
        compute='_compute_is_kanwil_group',
        store=True,
    )

    @api.depends('groups_id')
    def _compute_is_kanca_group(self):
        for rec in self:
            rec.is_kanca_group = rec.has_group('vit_contract_inherit.group_vit_contract_kanca')
            if not rec.is_kanca_group:
                rec.kanca_id = False

    @api.depends('groups_id')
    def _compute_is_kanwil_group(self):
        for rec in self:
            rec.is_kanwil_group = rec.has_group('vit_contract_inherit.group_vit_contract_kanwil')
            if not rec.is_kanwil_group:
                rec.kanwil_id = False