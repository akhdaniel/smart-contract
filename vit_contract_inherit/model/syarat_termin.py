#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)

class syarat_termin(models.Model):
    _name = "vit.syarat_termin"
    _inherit = "vit.syarat_termin"


    verified = fields.Boolean(
        string="Verified",
    )

    master_syarat_termin_id = fields.Many2one(
        comodel_name="vit.master_syarat_termin",
        required=True,
        string="Master Syarat Termin"
    )





    def action_open_syarat_termin(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Syarat Termin',
            'res_model': 'vit.syarat_termin',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }




    @api.onchange('master_syarat_termin_id')
    def _onchange_master_syarat_termin(self):
        if self.master_syarat_termin_id:
            self.name = self.master_syarat_termin_id.name

    @api.constrains('verified', 'document')
    def _check_verified_requires_document(self):
        for rec in self:
            if rec.verified and not rec.document:
                raise ValidationError(_("Tidak bisa memverifikasi tanpa upload Document."))
            
    @api.onchange('verified')
    def _onchange_verified(self):
        if self.verified and not self.document:
            self.verified = False
            return {
                'warning': {
                    'title': _("Gagal Verifikasi"),
                    'message': _("Upload Document dulu sebelum centang Verified."),
                }
            }