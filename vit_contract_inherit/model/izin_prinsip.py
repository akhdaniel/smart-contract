#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class izin_prinsip(models.Model):
    _name = "vit.izin_prinsip"
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
    )

    @api.depends("job_izin_prinsip_ids.total_pagu_job")
    def _compute_total_pagu(self):
        for rec in self:
            rec.total_pagu = sum(job.total_pagu_job for job in rec.job_izin_prinsip_ids)