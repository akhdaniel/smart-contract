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
        compute="_compute_is_late_upload",
        store=False
    )

    late_termin_names = fields.Char(
        string="Termin Terlambat",
        compute="_compute_is_late_upload",
        store=False
    )

    overdue_days = fields.Integer(
        string="Overdue Days",
        compute="_compute_overdue_days",
        store=True,
    )
    amount_denda = fields.Float(
        string="Amount Denda",
        compute="_compute_overdue_days",
        store=True,
    )

    @api.depends("termin_ids.verification_date",
                 "termin_ids.syarat_termin_ids.upload_date",
                 "amount_kontrak", "persentasi_denda")
    def _compute_overdue_days(self):
        for rec in self:
            overdue = 0
            if rec.termin_ids:
                for termin in rec.termin_ids:
                    if termin.verification_date:
                        for syarat in termin.syarat_termin_ids:
                            if syarat.upload_date:
                                delta = (syarat.upload_date - termin.verification_date).days
                                if delta > overdue:
                                    overdue = delta
            rec.overdue_days = max(overdue, 0)

            if rec.overdue_days > 0 and rec.amount_kontrak and rec.persentasi_denda:
                rec.amount_denda = rec.amount_kontrak * (rec.persentasi_denda / 100.0) * rec.overdue_days
            else:
                rec.amount_denda = 0.0



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
        # pakai context special biar bisa bandingin nilai lama
        if self._origin and self._origin.izin_prinsip_id:
            old_izin = self._origin.izin_prinsip_id.id
        else:
            old_izin = False

        new_izin = self.izin_prinsip_id.id if self.izin_prinsip_id else False

        if old_izin and new_izin and old_izin == new_izin:
            # izin masih sama → tidak reset
            return

        # izin ganti → reset turunan
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
            

            
    @api.constrains("izin_prinsip_id", "jenis_kontrak_id", "partner_id")
    def _check_duplicate_izin_prinsip_jenis_kontrak(self):
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

