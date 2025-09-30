from odoo import models, fields, api, _
from odoo.exceptions import UserError

class job_izin_prinsip(models.Model):

    _name = "vit.job_izin_prinsip"
    _inherit = "vit.job_izin_prinsip"

    kanca_id = fields.Many2one(
        comodel_name="vit.kanca",
        string="Kanca",
        domain="[('kanwil_id', '=', parent.kanwil_id)]",
    )


    total_pagu_job = fields.Float(
        string="Total Pagu Job",
        compute="_compute_total_pagu_job",
    )

    @api.depends("izin_prinsip_line_ids.pagu")
    def _compute_total_pagu_job(self):
        for rec in self:
            rec.total_pagu_job = sum(line.pagu for line in rec.izin_prinsip_line_ids)