from odoo import models, fields, api, _


class Droping(models.Model):
    _inherit = "vit.droping"

    jumlah = fields.Float(
        string="Jumlah",
        compute="_compute_jumlah",
        store=True,
        readonly=True,
    )

    total_pagu = fields.Float(
        string="Total Pagu",
        compute="_compute_total_pagu",
        store=True,
    )

    remaining = fields.Float(
        string="Remaining",
        compute="_compute_remaining",
        store=True,
    )

    @api.depends("izin_prinsip_ids.total_pagu")
    def _compute_total_pagu(self):
        for rec in self:
            rec.total_pagu = sum(rec.izin_prinsip_ids.mapped("total_pagu"))

    @api.depends("izin_prinsip_ids.total_pagu", "izin_prinsip_ids.stage_id.done")
    def _compute_jumlah(self):
        for rec in self:
            done_izin = rec.izin_prinsip_ids.filtered(lambda i: i.stage_id.done)
            rec.jumlah = sum(done_izin.mapped("total_pagu"))


    @api.depends("jumlah", "total_pagu")
    def _compute_remaining(self):
        for rec in self:
            rec.remaining = rec.total_pagu - rec.jumlah