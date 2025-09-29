#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class izin_prinsip(models.Model):
    _name = "vit.izin_prinsip"
    _inherit = "vit.izin_prinsip"


    master_budget_id = fields.Many2one(
        comodel_name="vit.master_budget",
        string=_("Master Budget"),
        related="budget_id.master_budget_id",
        store=True,
        readonly=True,
    )

    kanwil_id = fields.Many2one(
        comodel_name="vit.kanwil",
        string=_("Kanwil"),
        related="budget_id.kanwil_id",
        store=True,
        readonly=True,
    )


    total_pagu = fields.Float( string=_("Total Pagu"), compute="_compute_total_pagu", store=True)


    @api.depends('izin_prinsip_line_ids.pagu')
    def _compute_total_pagu(self):
        for rec in self:
            rec.total_pagu = sum(line.pagu for line in rec.izin_prinsip_line_ids)
