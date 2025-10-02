#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
from odoo.exceptions import ValidationError, UserError
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

    due_date = fields.Date( 
        string=_("Due Date"),
        required=True,    
    )

    upload_date = fields.Date(
        string="Upload Date",
        readonly=True,
    )

    @api.constrains('due_date', 'termin_id')
    def _check_due_date_not_exceed_termin(self):
        for rec in self:
            if rec.due_date and rec.termin_id and rec.termin_id.due_date:
                if rec.due_date > rec.termin_id.due_date:
                    raise ValidationError(_(
                        "Due Date syarat termin (%s) tidak boleh lebih dari Due Date termin induknya (%s)."
                    ) % (rec.due_date, rec.termin_id.due_date))





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
        

    # def write(self, vals):
    #     if "document" in vals:  
    #         if vals.get("document"):  
    #             vals["upload_date"] = fields.Date.context_today(self)
    #         else: 
    #             vals["upload_date"] = False
    #     return super().write(vals)

    # @api.model
    # def create(self, vals):
    #     if vals.get("document"):
    #         vals["upload_date"] = fields.Date.context_today(self)
    #     else:
    #         vals["upload_date"] = False
    #     return super().create(vals)

    @api.model
    def create(self, vals):
        if "upload_date" not in vals:
            if vals.get("document"):
                vals["upload_date"] = fields.Date.context_today(self)
            else:
                vals["upload_date"] = False
        return super().create(vals)

    def write(self, vals):
        if "document" in vals and "upload_date" not in vals:
            if vals.get("document"):
                vals["upload_date"] = fields.Date.context_today(self)
            else:
                vals["upload_date"] = False
        return super().write(vals)


    @api.onchange('document')
    def _onchange_document_due_date(self):
        if self.document and self.due_date:
            today = fields.Date.context_today(self)
            if today > self.due_date:
                return {
                    'warning': {
                        'title': _("Peringatan"),
                        'message': _("Anda melewati tanggal Upload yang tertera (Due Date: %s)") % (self.due_date),
                    }
                }

