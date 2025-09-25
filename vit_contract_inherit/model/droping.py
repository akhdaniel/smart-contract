from odoo import models, fields, api, _


class Droping(models.Model):
    _inherit = "vit.droping"

    jumlah = fields.Float(
        string="Jumlah",
        compute="_compute_jumlah",
        readonly=True,
    )

    izin_prinsip_ids = fields.One2many(
        comodel_name="vit.izin_prinsip",
        compute="_compute_izin_prinsip_ids",
        string="Izin Prinsip",
    )

    @api.depends("kanwil_kancab_id", "izin_prinsip_ids.total_pagu")
    def _compute_jumlah(self):
        for rec in self:
            total = 0.0
            if rec.kanwil_kancab_id:
                izin_prinsips = self.env["vit.izin_prinsip"].search([
                    ("kanwil_kancab_id", "=", rec.kanwil_kancab_id.id)
                ])
                total = sum(izin_prinsips.mapped("total_pagu"))
            rec.jumlah = total


    def _compute_izin_prinsip_ids(self):
        for rec in self:
            if rec.kanwil_kancab_id:
                rec.izin_prinsip_ids = self.env["vit.izin_prinsip"].search([
                    ("kanwil_kancab_id", "=", rec.kanwil_kancab_id.id)
                ])
            else:
                rec.izin_prinsip_ids = False