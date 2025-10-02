#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)

class kontrak(models.Model):
    _inherit = "vit.kontrak"

    attachments = fields.Many2many(
        'ir.attachment',
        string='Upload'
    )

    izin_prinsip_id = fields.Many2one(
        comodel_name="vit.izin_prinsip",
        string="Izin Prinsip",
        domain=[('stage_is_done', '=', True)],  
    )

    job_izin_prinsip_id = fields.Many2one(
        'vit.job_izin_prinsip',
        string="Job Izin Prinsip",
        domain="[('izin_prinsip_id', '=', izin_prinsip_id)]",
    )

    jenis_kontrak_many = fields.Many2many(
        comodel_name="vit.jenis_kontrak",
        string="Jenis Kontrak Filter",
        help="Daftar jenis kontrak yang valid untuk Job Izin Prinsip ini"
    )

    jenis_kontrak_id = fields.Many2one(
        comodel_name="vit.jenis_kontrak",
        string="Jenis Kontrak",
        domain="[('id', 'in', jenis_kontrak_many)]",
    )

    budget_rkap_id = fields.Many2one(
        comodel_name="vit.budget_rkap",  
        related="izin_prinsip_id.budget_id", 
        string=_("Budget Rkap")
    )

    master_budget_id = fields.Many2one(
        comodel_name="vit.master_budget",  
        related="izin_prinsip_id.master_budget_id", 
        string=_("Master Budget")
    )

    kanwil_id = fields.Many2one(
        comodel_name="vit.kanwil",  
        related="izin_prinsip_id.kanwil_id", 
        string=_("Kanwil")
    )

    kanca_id = fields.Many2one(
        comodel_name="vit.kanca",
        string="Kanca",
        related="job_izin_prinsip_id.kanca_id",
    )
    

    is_late_upload = fields.Boolean(
        string="Late Upload",
        compute="_compute_overdue_and_late",
    )

    late_termin_names = fields.Char(
        string="Termin Terlambat",
        compute="_compute_overdue_and_late",
    )

    overdue_days = fields.Integer(
        string="Overdue Days",
        compute="_compute_overdue_and_late",
    )
    amount_denda = fields.Float(
        string="Amount Denda",
        compute="_compute_overdue_and_late",
    )

    @api.depends("termin_ids.syarat_termin_ids.upload_date",
             "termin_ids.due_date",
             "amount_kontrak", "persentasi_denda")
    def _compute_overdue_and_late(self):
        for rec in self:
            max_overdue = 0
            late_termins = []

            if rec.termin_ids:
                for termin in rec.termin_ids:
                    overdue = 0
                    if termin.due_date:
                        for syarat in termin.syarat_termin_ids:
                            if syarat.upload_date:
                                delta = (syarat.upload_date - termin.due_date).days
                                if delta > 0:
                                    overdue = max(overdue, delta)

                    if overdue > 0:
                        late_termins.append(termin.master_nama_termin_id.name or termin.name)
                        if overdue > max_overdue:
                            max_overdue = overdue

            rec.overdue_days = max_overdue
            if max_overdue > 0 and rec.amount_kontrak and rec.persentasi_denda:
                rec.amount_denda = rec.amount_kontrak * (rec.persentasi_denda / 100.0) * max_overdue
            else:
                rec.amount_denda = 0.0

            rec.is_late_upload = bool(late_termins)
            rec.late_termin_names = ", ".join(late_termins) if late_termins else ""







    # @api.onchange('izin_prinsip_id')
    # def _onchange_izin_prinsip_id(self):
    #     if self.izin_prinsip_id:
    #         self.job_izin_prinsip_id = False
    #         self.jenis_kontrak_id = False
    #         self.jenis_kontrak_many = [(5, 0, 0)]
    #     else:
    #         self.job_izin_prinsip_id = False
    #         self.jenis_kontrak_id = False
    #         self.jenis_kontrak_many = [(5, 0, 0)]

    @api.onchange('izin_prinsip_id')
    def _onchange_izin_prinsip_id(self):
        if self._origin and self._origin.izin_prinsip_id:
            old_izin = self._origin.izin_prinsip_id.id
        else:
            old_izin = False

        new_izin = self.izin_prinsip_id.id if self.izin_prinsip_id else False

        if old_izin and new_izin and old_izin == new_izin:
            return

        self.job_izin_prinsip_id = False
        self.jenis_kontrak_id = False
        self.jenis_kontrak_many = [(5, 0, 0)]




    @api.onchange('job_izin_prinsip_id')
    def _onchange_job_izin_prinsip_id(self):
        if self.job_izin_prinsip_id:
            jenis_ids = self.env['vit.izin_prinsip_line'].search([
                ('job_izin_prinsip_id', '=', self.job_izin_prinsip_id.id)
            ]).mapped('jenis_kontrak_id').ids

            # isi field Many2many
            self.jenis_kontrak_many = [(6, 0, jenis_ids)]

            return {'domain': {'jenis_kontrak_id': [('id', 'in', jenis_ids)]}}
        else:
            self.jenis_kontrak_many = [(5, 0, 0)]
            return {'domain': {'jenis_kontrak_id': []}}
        

    @api.constrains("persentasi_denda")
    def _check_persentasi_denda(self):
        for rec in self:
            if rec.persentasi_denda < 0 or rec.persentasi_denda > 100:
                raise ValidationError(_("Persentasi Denda harus antara 0 dan 100"))
    

    @api.onchange('jenis_kontrak_id')
    def _onchange_jenis_kontrak(self):
        if self.jenis_kontrak_id and self.job_izin_prinsip_id:
            for line in self.job_izin_prinsip_id.izin_prinsip_line_ids:
                if line.jenis_kontrak_id == self.jenis_kontrak_id:
                    self.amount_izin_prinsip = line.pagu
                    break

    

    @api.depends('termin_ids.syarat_termin_ids.upload_date',
                 'termin_ids.syarat_termin_ids.due_date')
    def _compute_is_late_upload(self):
        for rec in self:
            late_termins = []
            for t in rec.termin_ids:
                if any(
                    s.upload_date and s.due_date and s.upload_date > s.due_date
                    for s in t.syarat_termin_ids
                ):
                    # pakai nama master termin biar jelas
                    late_termins.append(t.master_nama_termin_id.name or t.name)
            rec.is_late_upload = bool(late_termins)
            rec.late_termin_names = ", ".join(late_termins) if late_termins else ""



    @api.constrains('amount_izin_prinsip', 'amount_kontrak')
    def _check_amount_kontrak(self):
        for rec in self:
            if rec.amount_izin_prinsip < rec.amount_kontrak:
                raise ValidationError("Amount Kontrak tidak boleh lebih besar dari Amount Izin Prinsip.")
            

            
    # @api.constrains("izin_prinsip_id", "jenis_kontrak_id", "partner_id")
    # def _check_duplicate_izin_prinsip_jenis_kontrak(self):
    #     for rec in self:
    #         if rec.izin_prinsip_id and rec.jenis_kontrak_id and rec.partner_id:
    #             dupe = self.search([
    #                 ("id", "!=", rec.id),
    #                 ("izin_prinsip_id", "=", rec.izin_prinsip_id.id),
    #                 ("partner_id", "=", rec.partner_id.id),
    #                 ("jenis_kontrak_id", "=", rec.jenis_kontrak_id.id),
    #             ], limit=1)
    #             if dupe:
    #                 raise ValidationError(
    #                     _("Jenis Kontrak %s sudah dipakai oleh Partner %s untuk Izin Prinsip %s, tidak boleh duplikat!") 
    #                     % (rec.jenis_kontrak_id.name, rec.partner_id.name, rec.izin_prinsip_id.name)
    #                 )


    @api.constrains("izin_prinsip_id", "jenis_kontrak_id", "partner_id")
    def _check_duplicate_izin_prinsip_jenis_kontrak(self):
        if self.env.context.get("bypass_duplicate_check"):
            return

        for rec in self:
            if rec.izin_prinsip_id and rec.jenis_kontrak_id and rec.partner_id:
                dupe = self.search([
                    ("id", "!=", rec.id),
                    ("izin_prinsip_id", "=", rec.izin_prinsip_id.id),
                    ("partner_id", "=", rec.partner_id.id),
                    ("jenis_kontrak_id", "=", rec.jenis_kontrak_id.id),
                ], limit=1)
                if dupe:
                    raise ValidationError(
                        _("Jenis Kontrak %s sudah dipakai oleh Partner %s untuk Izin Prinsip %s, tidak boleh duplikat!") 
                        % (rec.jenis_kontrak_id.name, rec.partner_id.name, rec.izin_prinsip_id.name)
                    )



    def action_confirm(self):
        for rec in self:
            if rec.stage_id and rec.stage_id.draft:
                if rec.amount_kontrak <= 0:
                    raise UserError(_("Amount Kontrak tidak boleh 0 untuk melanjutkan ke tahap berikutnya."))

            elif rec.stage_id and rec.stage_id.on_progress:
                all_done = all(t.stage_id.done for t in rec.termin_ids)
                if not all_done:
                    raise UserError(_("Kontrak tidak bisa langsung masuk ke Done. "
                                    "Masih ada Termin yang belum selesai."))

        return super(kontrak, self).action_confirm() 
    

    def action_cancel(self):
        for rec in self:
            self.env['vit.payment'].search([('termin_id', 'in', rec.termin_ids.ids)]).unlink()

            kontrak_stage = rec.stage_id
            new_stage = False

            if kontrak_stage.done:
                new_stage = self.env['vit.kontrak_state'].search([('on_progress', '=', True)], limit=1)

            elif kontrak_stage.on_progress:
                new_stage = self.env['vit.kontrak_state'].search([('draft', '=', True)], limit=1)

            elif kontrak_stage.draft:
                new_stage = kontrak_stage  

            if not new_stage:
                raise UserError(_("Stage tujuan untuk Cancel tidak ditemukan!"))

            rec.stage_id = new_stage.id

            rec._sync_termin_stage(new_stage)

        return {'type': 'ir.actions.client', 'tag': 'reload'}
    

    def _sync_termin_stage(self, kontrak_stage):
        for rec in self:
            if kontrak_stage.draft:
                termin_stage = self.env['vit.state_termin'].search([('draft', '=', True)], limit=1)
            elif kontrak_stage.on_progress:
                termin_stage = self.env['vit.state_termin'].search([('on_progress', '=', True)], limit=1)
            elif kontrak_stage.done:
                termin_stage = self.env['vit.state_termin'].search([('done', '=', True)], limit=1)
            else:
                termin_stage = False

            if termin_stage:
                self.env['vit.payment'].search([('termin_id', 'in', rec.termin_ids.ids)]).unlink()
                rec.termin_ids.write({'stage_id': termin_stage.id})


    # def action_create_addendum(self):
    #     self.ensure_one()
        
    #     # Copy kontrak dengan bypass constraint
    #     kontrak_copy = self.with_context(bypass_duplicate_check=True).copy({
    #         'name': self.env['ir.sequence'].next_by_code('vit.kontrak') or _('New'),
    #         'stage_id': self.stage_id.id,  # <-- paksa ikut stage aslinya
    #     })

    #     # Duplikasi termin
    #     new_termins = []
    #     for termin in self.termin_ids:
    #         new_termin = termin.with_context(bypass_duplicate_check=True).copy({
    #             'kontrak_id': kontrak_copy.id,
    #             'stage_id': termin.stage_id.id,  # <-- paksa termin ikut stage aslinya juga
    #         })
    #         new_termins.append(new_termin.id)
    #     kontrak_copy.termin_ids = [(6, 0, new_termins)]

    #     # Duplikasi payments
    #     new_payments = []
    #     for payment in self.payment_ids:
    #         new_payment = payment.with_context(bypass_duplicate_check=True).copy({
    #             'kontrak_id': kontrak_copy.id,
    #         })
    #         new_payments.append(new_payment.id)
    #     kontrak_copy.payment_ids = [(6, 0, new_payments)]

    #     # Duplikasi attachments
    #     attachments = self.env['ir.attachment'].search([
    #         ('res_model', '=', 'vit.kontrak'),
    #         ('res_id', '=', self.id)
    #     ])
    #     for att in attachments:
    #         att.copy({'res_id': kontrak_copy.id})

    #     return {
    #         'name': _('Kontrak Addendum'),
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'vit.kontrak',
    #         'view_mode': 'form',
    #         'res_id': kontrak_copy.id,
    #         'target': 'current',
    #     }


    def action_create_addendum(self):
        self.ensure_one()
        
        kontrak_copy = self.with_context(bypass_duplicate_check=True).copy({
            'name': self.env['ir.sequence'].next_by_code('vit.kontrak') or _('New'),
            'stage_id': self.stage_id.id,
        })

        new_termins = []
        for termin in self.termin_ids:
            new_termin = termin.with_context(bypass_duplicate_check=True).copy({
                'kontrak_id': kontrak_copy.id,
                'stage_id': termin.stage_id.id,
            })
            
            new_syarat = []
            for syarat in termin.syarat_termin_ids:
                syarat_copy = syarat.copy({
                    'termin_id': new_termin.id,
                })
                new_syarat.append(syarat_copy.id)
            new_termin.syarat_termin_ids = [(6, 0, new_syarat)]

            new_termins.append(new_termin.id)

        kontrak_copy.termin_ids = [(6, 0, new_termins)]

        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'vit.kontrak'),
            ('res_id', '=', self.id)
        ])
        for att in attachments:
            att.copy({'res_id': kontrak_copy.id})

        kontrak_copy._compute_overdue_and_late()
        kontrak_copy._compute_is_late_upload()

        return {
            'name': _('Kontrak Addendum'),
            'type': 'ir.actions.act_window',
            'res_model': 'vit.kontrak',
            'view_mode': 'form',
            'res_id': kontrak_copy.id,
            'target': 'current',
        }






