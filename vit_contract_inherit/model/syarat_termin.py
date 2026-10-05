#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
from odoo.exceptions import ValidationError, UserError
_logger = logging.getLogger(__name__)

class syarat_termin(models.Model):
    _name = "vit.syarat_termin"
    _inherit = ["vit.syarat_termin", "mail.thread", "mail.activity.mixin"]
    _description = "Dokumen Vendor"


    verified = fields.Boolean(
        string="Verified",
    )

    confirm = fields.Boolean(
        string="Confirm",
    )

    termin_id = fields.Many2one(
        comodel_name="vit.termin",  
        string=_("Termin"), 
        ondelete='cascade'
    )

    master_syarat_termin_id = fields.Many2one(
        comodel_name="vit.master_syarat_termin",
        required=True,
        string="Master Syarat Termin"
    )

    nomor_kontrak = fields.Char(
        string='Nomor Kontrak',
        related='termin_id.kontrak_id.nomor_kontrak',
        store=True,
    )


    due_date = fields.Date( 
        string=_("Due Date"),
    )

    upload_date = fields.Date(
        string="Upload Date",
        readonly=True,
    )

    correction_note = fields.Text(
        string="Keterangan Koreksi",
        tracking=True,
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
    
    @api.constrains('confirm', 'document')
    def _check_confirm_requires_document(self):
        for rec in self:
            if rec.confirm and not rec.document:
                raise ValidationError(_("Tidak bisa mengkonfirmasi tanpa upload Document."))
            
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
    
    @api.onchange('confirm')
    def _onchange_confirm(self):
        if self.confirm and not self.document:
            self.confirm = False
            return {
                'warning': {
                    'title': _("Gagal Konfirmasi"),
                    'message': _("Upload Document dulu sebelum centang Confirm."),
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

    def _payment_document_notification_users(self):
        self.ensure_one()
        kontrak = self.termin_id.kontrak_id
        if not kontrak:
            return self.env["res.users"]

        Users = self.env["res.users"].sudo()
        base_domain = [("active", "=", True), ("share", "=", False)]
        kanwil_group = self.env.ref(
            "vit_contract_inherit.group_vit_contract_kanwil"
        )
        kanca_group = self.env.ref(
            "vit_contract_inherit.group_vit_contract_kanca"
        )
        pusat_umum_group = self.env.ref(
            "vit_contract_inherit.group_vit_contract_pusat_umum"
        )

        users = Users.search(base_domain + [
            ("groups_id", "in", pusat_umum_group.id),
        ])
        if kontrak.kanwil_id:
            users |= Users.search(base_domain + [
                ("groups_id", "in", kanwil_group.id),
                ("multi_kanwil", "in", kontrak.kanwil_id.id),
            ])
        if kontrak.kanca_id:
            users |= Users.search(base_domain + [
                ("groups_id", "in", kanca_group.id),
                ("multi_kanca", "in", kontrak.kanca_id.id),
            ])
        return users

    def _send_activity_menu_refresh(self, users):
        partners = users.sudo().mapped("partner_id")
        if partners:
            self.env["bus.bus"]._sendmany([
                (partner, "vit.activity_menu/updated", {})
                for partner in partners
            ])

    def _notify_vendor_document_uploaded(self):
        activity_type = self.env.ref("mail.mail_activity_data_todo")
        summary = _("Dokumen pembayaran perlu diverifikasi")
        Activity = self.env["mail.activity"].sudo()

        for rec in self:
            kontrak = rec.termin_id.kontrak_id
            notification_users = rec._payment_document_notification_users()
            note = _(
                "Vendor telah mengunggah dokumen '%s' untuk termin '%s' "
                "pada kontrak %s. Silakan verifikasi dokumen tersebut."
            ) % (
                rec.name or _("Tanpa Nama"),
                rec.termin_id.name or _("Tanpa Nama"),
                kontrak.nomor_kontrak or kontrak.name or _("Tanpa Nomor"),
            )
            for user in notification_users:
                existing = Activity.search([
                    ("res_model", "=", rec._name),
                    ("res_id", "=", rec.id),
                    ("user_id", "=", user.id),
                    ("activity_type_id", "=", activity_type.id),
                    ("summary", "=", summary),
                ], limit=1)
                if existing:
                    existing.write({
                        "date_deadline": fields.Date.context_today(rec),
                        "note": note,
                    })
                    continue
                rec.sudo().activity_schedule(
                    activity_type_id=activity_type.id,
                    user_id=user.id,
                    date_deadline=fields.Date.context_today(rec),
                    summary=summary,
                    note=note,
                )
            rec._send_activity_menu_refresh(notification_users)

    def _close_payment_document_activities(self, group_xmlid):
        group = self.env.ref(group_xmlid)
        summary = _("Dokumen pembayaran perlu diverifikasi")
        for rec in self:
            rec.sudo().activity_ids.filtered(
                lambda activity: activity.summary == summary
                and group in activity.user_id.groups_id
            ).unlink()

    def write(self, vals):
        user_name = self.env.user.name or "Unknown User"
        previous_values = {
            rec.id: {
                "document": bool(rec.document),
                "verified": rec.verified,
                "confirm": rec.confirm,
            }
            for rec in self
        }

        if "document" in vals and "upload_date" not in vals:
            if vals.get("document"):
                vals["upload_date"] = fields.Date.context_today(self)
            else:
                vals["upload_date"] = False

        res = super().write(vals)

        for rec in self:
            kontrak = rec.termin_id.kontrak_id 
            termin = rec.termin_id
            previous = previous_values.get(rec.id, {})
            document_uploaded = (
                "document" in vals
                and bool(vals.get("document"))
                and not previous.get("document")
            )
            verified_enabled = (
                "verified" in vals
                and rec.verified
                and not previous.get("verified")
            )
            confirm_enabled = (
                "confirm" in vals
                and rec.confirm
                and not previous.get("confirm")
            )

            if document_uploaded:
                rec.message_post(
                    body=_("Dokumen '%s' telah diupload oleh %s.") % (
                        rec.name or "Tanpa Nama", user_name),
                    message_type='comment'
                )
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

            uploaded_by_vendor = (
                self.env.context.get("vendor_syarat_upload")
                or self.env.user.has_group(
                    "vit_contract_inherit.group_vit_contract_vendor"
                )
            )
            if uploaded_by_vendor and vals.get("document"):
                rec._notify_vendor_document_uploaded()

            if verified_enabled:
                rec._close_payment_document_activities(
                    "vit_contract_inherit.group_vit_contract_kanwil"
                )
                rec._close_payment_document_activities(
                    "vit_contract_inherit.group_vit_contract_kanca"
                )
                operational_users = rec._payment_document_notification_users().filtered(
                    lambda user: user.has_group(
                        "vit_contract_inherit.group_vit_contract_kanwil"
                    ) or user.has_group(
                        "vit_contract_inherit.group_vit_contract_kanca"
                    )
                )
                rec._send_activity_menu_refresh(operational_users)
                rec.message_post(
                    body=_("Dokumen '%s' telah diverifikasi oleh %s.") % (
                        rec.name or "Tanpa Nama", user_name),
                    message_type='comment'
                )
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

            if "verified" in vals and not verified_enabled:
                operational_users = rec._payment_document_notification_users().filtered(
                    lambda user: user.has_group(
                        "vit_contract_inherit.group_vit_contract_kanwil"
                    ) or user.has_group(
                        "vit_contract_inherit.group_vit_contract_kanca"
                    )
                )
                rec._send_activity_menu_refresh(operational_users)

            if confirm_enabled:
                rec._close_payment_document_activities(
                    "vit_contract_inherit.group_vit_contract_pusat_umum"
                )
                pusat_users = rec._payment_document_notification_users().filtered(
                    lambda user: user.has_group(
                        "vit_contract_inherit.group_vit_contract_pusat_umum"
                    )
                )
                rec._send_activity_menu_refresh(pusat_users)
                rec.message_post(
                    body=_("Dokumen '%s' telah dikonfirmasi oleh %s.") % (
                        rec.name or "Tanpa Nama", user_name),
                    message_type='comment'
                )
                if kontrak:
                    kontrak.message_post(
                        body=_("✔️ Dokumen '%s' telah dikonfirmasi oleh %s.") % (
                            rec.name or "Tanpa Nama", user_name),
                        message_type='comment'
                    )
                if termin:
                    termin.message_post(
                        body=_("✔️ Dokumen '%s' telah dikonfirmasi oleh %s.") % (
                            rec.name or "Tanpa Nama", user_name),
                        message_type='comment'
                    )

            if "confirm" in vals and not confirm_enabled:
                pusat_users = rec._payment_document_notification_users().filtered(
                    lambda user: user.has_group(
                        "vit_contract_inherit.group_vit_contract_pusat_umum"
                    )
                )
                rec._send_activity_menu_refresh(pusat_users)

            if "verified" in vals or "confirm" in vals:
                if termin:
                    termin._compute_verifikasi_syarat()

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
