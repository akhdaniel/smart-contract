from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class syarat_termin(models.Model):
    _inherit = "vit.termin"


    name = fields.Char( required=True, copy=False, string=_("Name"))


    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        related="kontrak_id.partner_id",
        readonly=True,
    )

    kontrak_id = fields.Many2one(
        comodel_name="vit.kontrak",
        string="Kontrak",
        ondelete="cascade"
    )

    due_date = fields.Date(
        required=True,
        string=_("Due Date"),
    )

    verification_date = fields.Date(
        string=_("Verification Date"),
    )


    @api.onchange('persentase', 'kontrak_id')
    def _onchange_persentase(self):
        if not self.kontrak_id:
            return

        if self.persentase and self.persentase > 100:
            raise UserError("Persentase per termin tidak boleh lebih dari 100%.")

        total = sum(self.kontrak_id.termin_ids.mapped('persentase'))
        if total > 100:
            raise UserError("Total persentase semua termin dalam kontrak tidak boleh lebih dari 100%.")

        if self.kontrak_id.amount_kontrak and self.persentase:
            self.nilai = (self.kontrak_id.amount_kontrak * self.persentase) / 100
        else:
            self.nilai = 0.0


    @api.constrains("master_nama_termin_id", "kontrak_id")
    def _check_duplicate_master_nama_termin(self):
        for rec in self:
            if rec.kontrak_id and rec.master_nama_termin_id:
                dupe = rec.kontrak_id.termin_ids.filtered(
                    lambda l: l.id != rec.id and l.master_nama_termin_id == rec.master_nama_termin_id
                )
                if dupe:
                    raise ValidationError(
                        _("Master Nama Termin %s sudah ada di Kontrak %s, tidak boleh duplikat!")
                        % (rec.master_nama_termin_id.name, rec.kontrak_id.name)
                    )

    @api.constrains('persentase', 'kontrak_id')
    def _check_persentase_total(self):
        for rec in self:
            # per termin
            if rec.persentase < 0 or rec.persentase > 100:
                raise ValidationError("Persentase per termin harus antara 0 sampai 100%.")
            # total semua termin
            if rec.kontrak_id:
                total = sum(rec.kontrak_id.termin_ids.mapped('persentase'))
                if total > 100:
                    raise ValidationError("Total persentase semua termin dalam kontrak tidak boleh lebih dari 100%.")


    # def action_confirm(self):
    #     for rec in self:
    #         if not rec.kontrak_id:
    #             raise UserError(_("Termin %s tidak punya Kontrak.") % rec.name)

    #         if rec.kontrak_id.stage_name != "On Progress":
    #             raise UserError(_("Kontrak %s tidak dalam status On Progress, tidak bisa konfirmasi termin.") % rec.kontrak_id.name)

    #         if rec.persentase <= 0:
    #             raise UserError(_("Termin %s memiliki persentase 0 atau kurang, tidak bisa dikonfirmasi.") % rec.name)

    #         stage = rec._get_next_stage()

    #         if stage and stage.done:
    #             not_verified = rec.syarat_termin_ids.filtered(lambda l: not l.verified)
    #             if not_verified:
    #                 raise UserError(_("Tidak bisa di konfirmasi! Masih ada syarat termin yang belum diverifikasi:\n- %s") %
    #                                 "\n- ".join(not_verified.mapped("name")))

    #         rec.stage_id = stage

    #         method_name = rec.stage_id.execute_enter
    #         if isinstance(method_name, str) and method_name.strip():
    #             method = getattr(rec, method_name, None)
    #             if callable(method):
    #                 method()


    #         if rec.stage_id.done:
    #             if rec.nilai <= 0:
    #                 raise UserError(_("Termin %s memiliki nilai 0 atau kurang, tidak bisa dipindahkan ke Done.") % rec.name)

    #             kontrak = rec.kontrak_id
    #             if not kontrak.budget_rkap_id:
    #                 raise UserError(_("Kontrak %s tidak memiliki Budget RKAP!") % kontrak.name)

    #             payment = self.env['vit.payment'].search([('termin_id', '=', rec.id)], limit=1)
    #             vals = {
    #                 'name': self.env['ir.sequence'].next_by_code('vit.payment') or 'New',
    #                 'amount': rec.nilai,
    #                 'amount_denda': kontrak.amount_denda or 0.0,
    #                 'partner_id': kontrak.partner_id.id,
    #                 'budget_rkap_id': kontrak.budget_rkap_id.id,
    #                 'kanwil_id': kontrak.kanwil_id.id,
    #                 'master_budget_id': kontrak.master_budget_id.id,
    #                 'termin_id': rec.id,
    #                 'kontrak_id': kontrak.id,
    #                 'master_nama_termin_id': rec.master_nama_termin_id.id,
    #                 'payment_date': fields.Date.context_today(self),
    #             }
    #             if payment:
    #                 payment.write(vals)
    #             else:
    #                 self.env['vit.payment'].create(vals)

    #             all_done = all(k.stage_id and k.stage_id.done for k in kontrak.termin_ids)
    #             if all_done:
    #                 done_stage = self.env['vit.kontrak_state'].search([('done', '=', True)], limit=1)
    #                 if not done_stage:
    #                     raise UserError(_("Stage Done untuk Kontrak tidak ditemukan!"))
    #                 kontrak.stage_id = done_stage.id
    #         else:
    #             self.env['vit.payment'].search([('termin_id', '=', rec.id)]).unlink()

    #     return {'type': 'ir.actions.client', 'tag': 'reload'}



    def action_confirm(self):
        for rec in self:
            if not rec.kontrak_id:
                raise UserError(_("Termin %s tidak punya Kontrak.") % rec.name)

            if rec.kontrak_id.stage_name != "On Progress":
                raise UserError(_("Kontrak %s tidak dalam status On Progress, tidak bisa konfirmasi termin.") % rec.kontrak_id.name)
            
            if rec.persentase <= 0:
                raise UserError(_("Termin %s memiliki persentase 0 atau kurang, tidak bisa dikonfirmasi.") % rec.name)

            stage = rec._get_next_stage()

            if stage and stage.done:
                not_verified = rec.syarat_termin_ids.filtered(lambda l: not l.verified)
                if not_verified:
                    raise UserError(_("Tidak bisa di konfirmasi! Masih ada syarat termin yang belum diverifikasi:\n- %s") %
                                    "\n- ".join(not_verified.mapped("name")))


            rec.stage_id = stage

            if rec.stage_id.execute_enter and hasattr(rec, rec.stage_id.execute_enter) and callable(getattr(rec, rec.stage_id.execute_enter)):
                eval(f"rec.{rec.stage_id.execute_enter}()")

            if rec.stage_id.done:
                if rec.nilai <= 0:
                    raise UserError(_("Termin %s memiliki nilai 0 atau kurang, tidak bisa dipindahkan ke Done.") % rec.name)

                kontrak = rec.kontrak_id
                if not kontrak.budget_rkap_id:
                    raise UserError(_("Kontrak %s tidak memiliki Budget RKAP!") % kontrak.name)

                old_payments = self.env['vit.payment'].search([('termin_id', '=', rec.id)])
                old_payments.unlink()

                self.env['vit.payment'].create({
                    'name': 'PAY/' + rec.name,
                    'amount': rec.nilai,
                    'amount_denda': kontrak.amount_denda or 0.0,
                    'amount_budget_rkap': kontrak.budget_rkap_id.amount or 0.0,
                    'amount_izin_prinsip': kontrak.amount_izin_prinsip or 0.0,
                    'amount_kontrak': kontrak.amount_kontrak or 0.0,
                    'partner_id': kontrak.partner_id.id,
                    'budget_rkap_id': kontrak.budget_rkap_id.id,
                    'kanwil_id': kontrak.kanwil_id.id,
                    'master_budget_id': kontrak.master_budget_id.id,
                    'termin_id': rec.id,
                    'kontrak_id': kontrak.id, 
                    'master_nama_termin_id': rec.master_nama_termin_id.id,
                    'payment_date': fields.Date.context_today(self),
                })

                all_done = all(k.stage_id.done for k in kontrak.termin_ids)
                if all_done:
                    done_stage = self.env['vit.kontrak_state'].search([('done', '=', True)], limit=1)
                    if not done_stage:
                        raise UserError(_("Stage Done untuk Kontrak tidak ditemukan!"))
                    kontrak.write({'stage_id': done_stage.id})

            else:
                payments = self.env['vit.payment'].search([('termin_id', '=', rec.id)])
                payments.unlink()

        return {'type': 'ir.actions.client', 'tag': 'reload'}


    # def action_cancel(self):
    #     for rec in self:
    #         kontrak = rec.kontrak_id

    #         payments = self.env['vit.payment'].search([('termin_id', '=', rec.id)])
    #         payments.unlink()

    #         old_stage = rec.stage_id

    #         cancel_stage = self.env['vit.state_termin'].search([('draft', '=', True)], limit=1)
    #         if cancel_stage:
    #             rec.stage_id = cancel_stage.id

    #         progress_stage = self.env['vit.kontrak_state'].search([('on_progress', '=', True)], limit=1)
    #         if not progress_stage:
    #             raise UserError(_("Stage On Progress untuk Kontrak tidak ditemukan!"))
    #         kontrak.write({'stage_id': progress_stage.id})

    #         if old_stage.done and rec.stage_id == cancel_stage:
    #             return {'type': 'ir.actions.client', 'tag': 'reload'}

    #     return True




    def action_cancel(self):
        for rec in self:
            kontrak = rec.kontrak_id

            payments = self.env['vit.payment'].search([('termin_id', '=', rec.id)])
            payments.unlink()

            old_stage = rec.stage_id

            draft_stage = self.env['vit.state_termin'].search([('draft', '=', True)], limit=1)
            progress_stage = self.env['vit.state_termin'].search([('on_progress', '=', True)], limit=1)
            done_stage = self.env['vit.state_termin'].search([('done', '=', True)], limit=1)

            if not draft_stage or not progress_stage or not done_stage:
                raise UserError(_("Stage Draft / On Progress / Done untuk Termin tidak ditemukan!"))

            # logika bertahap termin
            if old_stage == done_stage:
                rec.stage_id = progress_stage.id
                kontrak.write({'stage_id': self.env['vit.kontrak_state'].search([('on_progress', '=', True)], limit=1).id})

            elif old_stage == progress_stage:
                rec.stage_id = draft_stage.id
                kontrak.write({'stage_id': self.env['vit.kontrak_state'].search([('draft', '=', True)], limit=1).id})

            elif old_stage == draft_stage:
                rec.stage_id = draft_stage.id  # tetap di draft

            return {'type': 'ir.actions.client', 'tag': 'reload'}

        return True

















    # @api.onchange('persentase', 'kontrak_id')
    # def _onchange_persentase(self):
    #     if self.kontrak_id and self.kontrak_id.amount_kontrak and self.persentase:
    #         self.nilai = (self.kontrak_id.amount_kontrak * self.persentase) / 100
    #     else:
    #         self.nilai = 0.0


    # @api.constrains('persentase', 'kontrak_id')
    # def _check_persentase_total(self):
    #     for rec in self:
    #         if rec.persentase < 0 or rec.persentase > 100:
    #             raise ValidationError("Persentase per termin harus antara 0 sampai 100.")

    #         if rec.kontrak_id:
    #             total = sum(rec.kontrak_id.termin_ids.mapped('persentase'))
    #             if total > 100:
    #                 raise ValidationError("Total semua persentase termin pada kontrak ini tidak boleh lebih dari 100%.")