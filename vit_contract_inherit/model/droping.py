from odoo import models, fields, api, _
from datetime import date

class Droping(models.Model):
    _inherit = "vit.droping"

    attachments = fields.Many2many(
        'ir.attachment',
        string='Upload'
    )

    jumlah = fields.Float(
        string="Jumlah",
        compute="_compute_jumlah",
        store=True,
        readonly=True,
    )

    termin_kontrak_ids = fields.One2many(
        "vit.termin", "droping_id",
        string="Termin Kontrak"
    )

    @api.onchange("due_date", "kanwil_id", "master_budget_id")
    def _onchange_filter_termin(self):
        """ Isi termin_kontrak_ids otomatis berdasarkan kanwil, budget, dan due_date """
        for rec in self:
            if rec.due_date and rec.kanwil_id and rec.master_budget_id:
                start_date = rec.due_date
                end_date = date(rec.due_date.year, 12, 31)

                domain = [
                    ("kontrak_id.kanwil_id", "=", rec.kanwil_id.id),
                    ("kontrak_id.master_budget_id", "=", rec.master_budget_id.id),
                    ("due_date", ">=", start_date),
                    ("due_date", "<=", end_date),
                ]

                termins = self.env["vit.termin"].search(domain)
                rec.termin_kontrak_ids = termins
