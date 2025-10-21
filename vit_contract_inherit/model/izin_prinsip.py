#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class izin_prinsip(models.Model):
    _inherit = "vit.izin_prinsip"

    attachments = fields.Many2many(
        'ir.attachment',
        string='Upload'
    )

    master_budget_id = fields.Many2one(
        comodel_name="vit.master_budget",
        string=_("Master Budget"),
        related="budget_id.master_budget_id",
        readonly=True,
    )

    total_pagu = fields.Float(
        string="Total Pagu",
        compute="_compute_total_pagu",
        store=True,
    )

    total_payment = fields.Float(
        string="Total Payment",
        compute="_compute_total_payment",
        store=True,
    )

    @api.depends("kontrak_ids.payment_ids.amount", "kanwil_id")
    def _compute_total_payment(self):
        for rec in self:
            total = 0.0
            if rec.kanwil_id and rec.kontrak_ids:
                # ambil semua payment dari kontrak terkait
                payments = rec.mapped("kontrak_ids.payment_ids")

                # filter payment berdasarkan kanwil yang sama
                filtered = payments.filtered(lambda p: p.kanwil_id == rec.kanwil_id)

                # jumlahkan amount-nya
                total = sum(filtered.mapped("amount"))

            rec.total_payment = total

    @api.depends("job_izin_prinsip_ids.total_pagu_job")
    def _compute_total_pagu(self):
        for rec in self:
            rec.total_pagu = sum(job.total_pagu_job for job in rec.job_izin_prinsip_ids)

    @api.constrains("total_pagu", "budget_id")
    def _check_total_pagu_vs_budget(self):
        for rec in self:
            if rec.budget_id and rec.total_pagu > rec.budget_id.amount:
                raise ValidationError(_(
                    "Total Pagu (%.2f) tidak boleh melebihi Amount Budget RKAP (%.2f)!"
                ) % (rec.total_pagu, rec.budget_id.amount))
