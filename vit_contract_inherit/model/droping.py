from odoo import models, fields, api, _
from datetime import date as dt

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

    date = fields.Date(
        string="Date",
        readonly=True,
    )





    @api.model
    def create(self, vals):
        if not vals.get("date"):
            today = fields.Date.context_today(self)
            end_of_year = dt(today.year, 12, 31)
            vals["date"] = end_of_year
        return super(Droping, self).create(vals)






    @api.onchange("kanwil_id", "master_budget_id")
    def _onchange_filter_termin(self):
        """ Isi termin_kontrak_ids otomatis berdasarkan kanwil, budget,
            hanya tarik termin yang belum punya droping,
            dan due_date termin maksimal di tahun droping.date """
        for rec in self:
            if rec.kanwil_id and rec.master_budget_id:
                domain = [
                    ("kontrak_id.kanwil_id", "=", rec.kanwil_id.id),
                    ("kontrak_id.master_budget_id", "=", rec.master_budget_id.id),
                    ("droping_id", "=", False),
                    ("is_droping_done", "=", False),
                ]

                if rec.date:
                    year_limit = rec.date.year
                    end_date = dt(year_limit, 12, 31)
                    domain.append(("due_date", "<=", end_date))

                termins = self.env["vit.termin"].search(domain)
                rec.termin_kontrak_ids = termins
            else:
                rec.termin_kontrak_ids = [(5, 0, 0)]




    def write(self, vals):
        res = super(Droping, self).write(vals)
        for rec in self:
            if "termin_kontrak_ids" in vals:
                rec.termin_kontrak_ids.write({"is_droping_done": True})
        return res





    @api.depends("termin_kontrak_ids.nilai")
    def _compute_jumlah(self):
        for rec in self:
            rec.jumlah = sum(rec.termin_kontrak_ids.mapped("nilai"))

    


    # @api.onchange("due_date", "kanwil_id", "master_budget_id")
    # def _onchange_filter_termin(self):
    #     """ Isi termin_kontrak_ids otomatis berdasarkan kanwil, budget, dan due_date """
    #     for rec in self:
    #         if rec.due_date and rec.kanwil_id and rec.master_budget_id:
    #             start_date = rec.due_date
    #             end_date = date(rec.due_date.year, 12, 31)

    #             domain = [
    #                 ("kontrak_id.kanwil_id", "=", rec.kanwil_id.id),
    #                 ("kontrak_id.master_budget_id", "=", rec.master_budget_id.id),
    #                 ("due_date", ">=", start_date),
    #                 ("due_date", "<=", end_date),
    #             ]

    #             termins = self.env["vit.termin"].search(domain)
    #             rec.termin_kontrak_ids = termins