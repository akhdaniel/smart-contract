from odoo import models, fields, api, _


class Droping(models.Model):
    _inherit = "vit.droping"


    jumlah = fields.Float(
        string="Jumlah",
        compute="_compute_jumlah",
        store=True,
        readonly=True,
    )

    @api.depends("termin_kontrak_ids.nilai")
    def _compute_jumlah(self):
        for rec in self:
            rec.jumlah = sum(rec.termin_kontrak_ids.mapped("nilai"))
