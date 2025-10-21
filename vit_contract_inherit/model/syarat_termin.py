#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
from odoo.exceptions import ValidationError, UserError
_logger = logging.getLogger(__name__)

class syarat_termin(models.Model):
    _name = "vit.syarat_termin"
    _inherit = ["vit.syarat_termin", "mail.thread", "mail.activity.mixin"]


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
    )

    upload_date = fields.Date(
        string="Upload Date",
        readonly=True,
    )


    def write(self, vals):
        res = super(syarat_termin, self).write(vals)
        if "verified" in vals:
            for rec in self:
                if rec.termin_id:
                    rec.termin_id._compute_verifikasi_syarat()
        return res

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
        user_name = self.env.user.name or "Unknown User"

        if "document" in vals and "upload_date" not in vals:
            if vals.get("document"):
                vals["upload_date"] = fields.Date.context_today(self)
            else:
                vals["upload_date"] = False

        res = super().write(vals)

        for rec in self:
            kontrak = rec.termin_id.kontrak_id 
            termin = rec.termin_id

            if 'document' in vals and vals.get('document'):
                if kontrak:
                    kontrak.message_post(
                        body=_("📎 Dokumen '%s' telah diupload oleh %s.") % (
                            rec.name or "Tanpa Nama", user_name),
                        message_type='comment'
                    )
                if termin:
                    termin.message_post(
                        body=_("📎 Dokumen '%s' telah diupload oleh %s.") % (
                            rec.name or "Tanpa Nama", user_name),
                        message_type='comment'
                    )

            if 'verified' in vals and vals.get('verified'):
                if kontrak:
                    kontrak.message_post(
                        body=_("✅ Dokumen '%s' telah diverifikasi oleh %s.") % (
                            rec.name or "Tanpa Nama", user_name),
                        message_type='comment'
                    )
                if termin:
                    termin.message_post(
                        body=_("✅ Dokumen '%s' telah diverifikasi oleh %s.") % (
                            rec.name or "Tanpa Nama", user_name),
                        message_type='comment'
                    )

        return res



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



class SyaratTerminInherit(models.Model):
    _inherit = "vit.syarat_termin"

    def copy(self, default=None):
        default = dict(default or {})

        # Kalau sudah dikasih name (misal dari addendum termin), pakai langsung
        if default.get("name"):
            return models.BaseModel.copy(self, default)

        base_name = self.name
        if "-" in base_name:
            parts = base_name.split("-")
            try:
                last_num = int(parts[-1])
                new_name = f"{base_name}-{last_num+1}"
            except ValueError:
                new_name = f"{base_name}-1"
        else:
            new_name = f"{base_name}-1"

        default["name"] = new_name
        return models.BaseModel.copy(self, default)
