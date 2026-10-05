from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError

class job_izin_prinsip(models.Model):

    _name = "vit.job_izin_prinsip"
    _inherit = "vit.job_izin_prinsip"

    can_edit_kompleks = fields.Boolean(
        compute="_compute_can_edit_kompleks",
        string="Can Edit Kompleks Pergudangan",
    )

    def _compute_can_edit_kompleks(self):
        allowed = (
            self.env.su
            or self.env.user.has_group("vit_contract.group_vit_contract_manager")
            or self.env.user.has_group("vit_contract_inherit.group_vit_contract_pusat_umum")
        )
        for record in self:
            record.can_edit_kompleks = allowed

    def _check_kompleks_write_access(self, vals):
        if "kompleks_id" not in vals:
            return
        allowed = (
            self.env.su
            or self.env.user.has_group("vit_contract.group_vit_contract_manager")
            or self.env.user.has_group("vit_contract_inherit.group_vit_contract_pusat_umum")
        )
        if not allowed:
            raise AccessError(_(
                "Kompleks Pergudangan hanya dapat diatur oleh Pusat Umum atau Pusat Admin."
            ))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("kompleks_id"):
                self._check_kompleks_write_access(vals)
        return super().create(vals_list)

    def write(self, vals):
        self._check_kompleks_write_access(vals)
        return super().write(vals)

    def init(self):
        """Preserve existing contract warehouse links before contracts become related."""
        self.env.cr.execute("""
            UPDATE vit_job_izin_prinsip AS job
               SET kompleks_id = source.kompleks_id
              FROM (
                    SELECT DISTINCT ON (job_izin_prinsip_id)
                           job_izin_prinsip_id, kompleks_id
                      FROM vit_kontrak
                     WHERE job_izin_prinsip_id IS NOT NULL
                       AND kompleks_id IS NOT NULL
                     ORDER BY job_izin_prinsip_id, id
                   ) AS source
             WHERE job.id = source.job_izin_prinsip_id
               AND job.kompleks_id IS NULL
        """)
        self.env.cr.execute("""
            UPDATE vit_kontrak AS contract
               SET kompleks_id = job.kompleks_id
              FROM vit_job_izin_prinsip AS job
             WHERE contract.job_izin_prinsip_id = job.id
               AND contract.kompleks_id IS DISTINCT FROM job.kompleks_id
        """)

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

    kompleks_id = fields.Many2one(
        'vit.kompleks_pergudangan',
        string='Kompleks Pergudangan',
        domain="[('kanca_id', '=', kanca_id)]"
    )


    @api.onchange('kanca_id')
    def _onchange_kanca_id(self):
        self.kompleks_id = False



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
