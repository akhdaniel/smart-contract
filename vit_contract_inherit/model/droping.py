from odoo import models, fields, api, _
from odoo.exceptions import UserError
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

    droping_line_ids = fields.One2many(
        "vit.droping.line",
        "droping_id",
        string="Termin Kontrak",
    )

    date = fields.Date(
        string="Date",
        readonly=True,
    )

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

        if field_name == "kanwil_id":
            return [("id", "in", user.multi_kanwil.ids)] if user.multi_kanwil else []

        elif field_name == "kanca_id":
            if user.multi_kanca:
                return [("id", "in", user.multi_kanca.ids)]
            if user.multi_kanwil:
                return [("kanwil_id", "in", user.multi_kanwil.ids)]

            return [("kanwil_id", "=", self.kanwil_id.id)] if self.kanwil_id else []

        return []






    @api.model
    def create(self, vals):
        if not vals.get("date"):
            today = fields.Date.context_today(self)
            end_of_year = dt(today.year, 12, 31)
            vals["date"] = end_of_year
        rec = super(Droping, self).create(vals)
        rec._recompute_related_rkap_droping_totals()
        return rec


    # @api.model
    # def create(self, vals):
    #     user = self.env.user

    #     if not vals.get("kanwil_id") and user.multi_kanwil:
    #         if len(user.multi_kanwil) == 1:
    #             vals["kanwil_id"] = user.multi_kanwil.id

    #     if not vals.get("date"):
    #         today = fields.Date.context_today(self)
    #         end_of_year = dt(today.year, 12, 31)
    #         vals["date"] = end_of_year

    #     return super(Droping, self).create(vals)
    

    # @api.model
    # def create(self, vals):
    #     user = self.env.user

    #     if not vals.get("kanwil_id"):
    #         if user.multi_kanwil and len(user.multi_kanwil) == 1:
    #             vals["kanwil_id"] = user.multi_kanwil.id
    #     if not vals.get("date"):
    #         today = fields.Date.context_today(self)
    #         end_of_year = dt(today.year, 12, 31)
    #         vals["date"] = end_of_year

    #     return super(Droping, self).create(vals)






    def _get_available_termin_domain(self):
        self.ensure_one()
        domain = [
            ("stage_is_done", "=", False),
            ("droping_id", "=", False),
        ]
        if self.kanwil_id:
            domain.append(("kontrak_id.kanwil_id", "=", self.kanwil_id.id))
        if self.master_budget_id:
            domain.append(("kontrak_id.master_budget_id", "=", self.master_budget_id.id))
        return domain

    def action_add_available_termins(self):
        DropingLine = self.env["vit.droping.line"].sudo()
        total_added = 0
        for rec in self:
            if not rec.id:
                raise UserError(_("Simpan Droping dulu sebelum ambil semua termin."))
            if not rec.kanwil_id or not rec.master_budget_id:
                raise UserError(_("Pilih Kanwil dan Master Budget dulu."))

            rec._unlink_empty_droping_lines()
            termins = self.env["vit.termin"].search(rec._get_available_termin_domain())
            used_termins = DropingLine.search([
                ("termin_id", "!=", False),
                ("droping_id", "!=", rec.id),
            ]).mapped("termin_id")
            existing_termins = rec.droping_line_ids.mapped("termin_id")
            new_termins = termins - used_termins - existing_termins
            if new_termins:
                DropingLine.create([
                    {
                        "droping_id": rec.id,
                        "filter_kontrak_id": termin.kontrak_id.id,
                        "termin_id": termin.id,
                    }
                    for termin in new_termins
                ])
                total_added += len(new_termins)
            rec._recompute_related_rkap_droping_totals()

        message = _("%s termin berhasil diambil.") % total_added if total_added else _("Tidak ada termin yang bisa diambil.")
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Ambil Semua Termin"),
                "message": message,
                "type": "success" if total_added else "warning",
                "sticky": False,
                "next": {"type": "ir.actions.client", "tag": "reload"},
            },
        }

    @api.onchange("kanwil_id", "master_budget_id")
    def _onchange_filter_termin(self):
        for rec in self:
            rec.droping_line_ids = [(5, 0, 0)]

    def write(self, vals):
        res = super(Droping, self).write(vals)
        self._unlink_empty_droping_lines()
        self._recompute_related_rkap_droping_totals()
        return res

    def _unlink_empty_droping_lines(self):
        for rec in self:
            rec.droping_line_ids.filtered(lambda line: not line.termin_id).unlink()

    def _get_selected_termins(self):
        self.ensure_one()
        termins = self.droping_line_ids.mapped("termin_id")
        if not termins:
            termins = self.termin_kontrak_ids
        return termins

    def _check_all_selected_termins_done(self):
        for rec in self:
            not_done_termins = rec._get_selected_termins().filtered(lambda termin: not termin.stage_is_done)
            if not_done_termins:
                names = ", ".join(not_done_termins.mapped("name"))
                raise UserError(_(
                    "Droping tidak bisa dilanjutkan ke pengeksekusian dana karena masih ada Termin yang belum Done: %s. "
                    "Hapus Termin tersebut dari tabel Droping dulu supaya bisa dipakai lagi di Droping baru."
                ) % names)

    def action_confirm(self):
        for rec in self:
            next_stage = rec._get_next_stage()
            if next_stage.on_progress:
                rec._check_all_selected_termins_done()
        return super(Droping, self).action_confirm()

    def unlink(self):
        related = [(rec.master_budget_id.id, rec.kanwil_id.id) for rec in self]
        res = super(Droping, self).unlink()
        self._recompute_related_rkap_droping_totals(related)
        return res

    def _recompute_related_rkap_droping_totals(self, related=None):
        related = related or [(rec.master_budget_id.id, rec.kanwil_id.id) for rec in self]
        master_budget_ids = [master_id for master_id, _kanwil_id in related if master_id]
        kanwil_ids = [kanwil_id for _master_id, kanwil_id in related if kanwil_id]

        budgets = self.env["vit.budget_rkap"].sudo().search([
            ("master_budget_id", "in", master_budget_ids),
        ]) if master_budget_ids else self.env["vit.budget_rkap"]

        izins = self.env["vit.izin_prinsip"].sudo().search([
            ("budget_id.master_budget_id", "in", master_budget_ids),
            ("kanwil_id", "in", kanwil_ids),
        ]) if master_budget_ids and kanwil_ids else self.env["vit.izin_prinsip"]

        if budgets:
            budgets._compute_totals()
        if izins:
            izins._compute_summary_totals()





    @api.depends("droping_line_ids.nilai", "termin_kontrak_ids.nilai")
    def _compute_jumlah(self):
        for rec in self:
            if rec.droping_line_ids:
                rec.jumlah = sum(rec.droping_line_ids.mapped("nilai"))
            else:
                rec.jumlah = sum(rec.termin_kontrak_ids.mapped("nilai"))

    def _ensure_done_for_print(self):
        for rec in self:
            if not rec.stage_is_done:
                raise UserError(_("Cetak hanya bisa dilakukan jika dropping sudah Done."))

    def action_print_lembar_realokasi(self):
        self._ensure_done_for_print()
        return self.env.ref("vit_contract_inherit.action_report_droping_lembar_realokasi").report_action(self)

    def action_print_nota_permintaan_dropping(self):
        self._ensure_done_for_print()
        return self.env.ref("vit_contract_inherit.action_report_droping_nota_permintaan").report_action(self)


class DropingLine(models.Model):
    _name = "vit.droping.line"
    _description = "vit.droping.line"

    droping_id = fields.Many2one(
        "vit.droping",
        string="Droping",
        required=True,
        ondelete="cascade",
    )
    termin_id = fields.Many2one(
        "vit.termin",
        string="Termin",
        ondelete="restrict",
    )
    filter_kontrak_id = fields.Many2one(
        "vit.kontrak",
        string="Kontrak",
        compute="_compute_filter_kontrak_id",
        inverse="_inverse_filter_kontrak_id",
        store=True,
        readonly=False,
    )
    name = fields.Char(related="termin_id.name", string="Name", readonly=True)
    nilai = fields.Float(related="termin_id.nilai", string="Nilai", readonly=True)
    master_nama_termin_id = fields.Many2one(
        related="termin_id.master_nama_termin_id",
        string="Master Nama Termin",
        readonly=True,
    )
    persentase = fields.Float(related="termin_id.persentase", string="Persentase", readonly=True)
    stage_id = fields.Many2one(related="termin_id.stage_id", string="Stage", readonly=True)
    deskripsi = fields.Text(related="termin_id.deskripsi", string="Deskripsi", readonly=True)
    partner_id = fields.Many2one(related="termin_id.partner_id", string="Partner", readonly=True)
    kontrak_id = fields.Many2one(related="termin_id.kontrak_id", string="Kontrak", readonly=True)
    syarat_progress = fields.Float(related="termin_id.syarat_progress", string="Syarat Progress", readonly=True)
    actual_progress = fields.Float(related="termin_id.actual_progress", string="Actual Progress", readonly=True)
    syarat_output = fields.Text(related="termin_id.syarat_output", string="Syarat Output", readonly=True)
    actual_output = fields.Text(related="termin_id.actual_output", string="Actual Output", readonly=True)
    nomor_kontrak = fields.Char(related="termin_id.nomor_kontrak", string="Nomor Kontrak", readonly=True)
    partner_bank_id = fields.Many2one(related="termin_id.partner_bank_id", string="Rekening Pembayaran", readonly=True)
    payment_bank_name = fields.Char(related="termin_id.payment_bank_name", string="Nama Bank", readonly=True)
    payment_bank_acc_number = fields.Char(related="termin_id.payment_bank_acc_number", string="Nomor Rekening", readonly=True)
    payment_bank_acc_holder = fields.Char(related="termin_id.payment_bank_acc_holder", string="Atas Nama Rekening", readonly=True)

    @api.depends("termin_id", "termin_id.kontrak_id")
    def _compute_filter_kontrak_id(self):
        for rec in self:
            if rec.termin_id:
                rec.filter_kontrak_id = rec.termin_id.kontrak_id

    def _inverse_filter_kontrak_id(self):
        return True

    @api.onchange("filter_kontrak_id")
    def _onchange_filter_kontrak_id(self):
        for rec in self:
            if rec.termin_id and rec.termin_id.kontrak_id != rec.filter_kontrak_id:
                rec.termin_id = False

    @api.onchange("termin_id")
    def _onchange_termin_id(self):
        for rec in self:
            if rec.termin_id:
                rec.filter_kontrak_id = rec.termin_id.kontrak_id

    def action_open_termin(self):
        self.ensure_one()
        if not self.termin_id:
            raise UserError(_("Pilih Termin dulu."))
        return {
            "type": "ir.actions.act_window",
            "name": _("Termin"),
            "res_model": "vit.termin",
            "view_mode": "form",
            "res_id": self.termin_id.id,
            "target": "new",
        }

    _sql_constraints = [
        (
            "unique_termin_id",
            "unique(termin_id)",
            "Termin ini sudah dipilih di droping lain.",
        ),
    ]

    @api.constrains("termin_id", "droping_id")
    def _check_termin_allowed(self):
        for rec in self:
            termin = rec.termin_id
            droping = rec.droping_id
            if not termin:
                continue
            if rec.filter_kontrak_id and termin.kontrak_id != rec.filter_kontrak_id:
                raise UserError(_("Termin %s tidak sesuai Kontrak yang dipilih.") % termin.name)
            if termin.stage_is_done:
                raise UserError(_("Termin yang sudah Done tidak bisa dipilih untuk Droping."))
            if termin.droping_id:
                raise UserError(_("Termin %s sudah terhubung ke Droping lama.") % termin.name)
            if droping.kanwil_id and termin.kontrak_id.kanwil_id != droping.kanwil_id:
                raise UserError(_("Termin %s tidak sesuai Kanwil Droping.") % termin.name)
            if droping.master_budget_id and termin.kontrak_id.master_budget_id != droping.master_budget_id:
                raise UserError(_("Termin %s tidak sesuai Master Budget Droping.") % termin.name)


class TerminDropingLine(models.Model):
    _inherit = "vit.termin"

    droping_line_ids = fields.One2many(
        "vit.droping.line",
        "termin_id",
        string="Droping Lines",
    )
    is_in_droping_line = fields.Boolean(
        string="In Droping Line",
        compute="_compute_is_in_droping_line",
        store=True,
    )

    @api.depends("droping_line_ids")
    def _compute_is_in_droping_line(self):
        for rec in self:
            rec.is_in_droping_line = bool(rec.droping_line_ids)

    


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
