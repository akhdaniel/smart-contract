from odoo import models, fields, api, _
from odoo.exceptions import UserError

class job_izin_prinsip(models.Model):

    _name = "vit.job_izin_prinsip"
    _inherit = "vit.job_izin_prinsip"

    kanwil_id = fields.Many2one(
        'vit.kanwil',
        string='Kanwil',
        domain=lambda self: self._domain_user("kanwil_id"),
    )

    kanca_id = fields.Many2one(
        "vit.kanca",
        string="Kanca",
        domain=lambda self: self._domain_user("kanca_id"),
    )


    @api.model
    def _domain_user(self, field_name):
        user = self.env.user

        # --- Kanwil ---
        if field_name == "kanwil_id":
            if user.multi_kanwil:
                return [("id", "in", user.multi_kanwil.ids)]
            return []

        # --- Kanca ---
        elif field_name == "kanca_id":
            if user.multi_kanca:
                # ✅ Kalau user punya multi_kanca → filter sesuai itu
                return [("id", "in", user.multi_kanca.ids)]
            else:
                # ✅ Kalau multi_kanca kosong (baik multi_kanwil isi atau enggak)
                # ikut parent.kanwil_id aja
                return "[('kanwil_id', '=', parent.kanwil_id)]"

        return []

    def copy(self, default=None):
        default = dict(default or {})
        
        # Jika nama sudah di-set di default dict (saat addendum creation), gunakan itu
        # dan jangan tambahin "(Copy)"
        if 'name' in default:
            # Gunakan nama yang sudah di-set, jangan modify
            from odoo import models
            return models.BaseModel.copy(self, default)
        
        # Default behavior dari parent (dengan "(Copy)")
        return super(job_izin_prinsip, self).copy(default)

    total_pagu_job = fields.Float(
        string="Total Pagu Job",
        compute="_compute_total_pagu_job",
    )

    @api.depends("izin_prinsip_line_ids.pagu")
    def _compute_total_pagu_job(self):
        for rec in self:
            rec.total_pagu_job = sum(line.pagu for line in rec.izin_prinsip_line_ids)