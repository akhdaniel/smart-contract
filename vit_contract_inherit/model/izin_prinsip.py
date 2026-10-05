#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError
from datetime import timedelta
import logging
_logger = logging.getLogger(__name__)

class izin_prinsip(models.Model):
    _name = "vit.izin_prinsip"
    _inherit = ["vit.izin_prinsip", "mail.thread", "mail.activity.mixin"]
    _description = "Izin Prinsip"

    name = fields.Char(required=True, copy=False, string="Name", default=False)

    nomor_tracker = fields.Char(
        string='Nomor Tracker',
        help='Nomor Tracker dari file import',
    )

    server_deploy_test = fields.Char(
        string='Tes Deploy Server',
        default='FIELD TEST BERHASIL MUNCUL',
    )

    created_by = fields.Many2one(
        'res.users',
        string='Dibuat Oleh',
        readonly=True,
        default=lambda self: self.env.user
    )

    allowed_kanca_id = fields.Many2one(
        'vit.kanca',
        string='Allowed Kanca',
        compute='_compute_allowed_kanca',
        store=True,
        readonly=False
    )

    attachments = fields.Many2many(
        'ir.attachment',
        string='Upload'
    )

    master_budget_id = fields.Many2one(
        comodel_name="vit.master_budget",
        string=_("Master Budget"),
        related="budget_id.master_budget_id",
        readonly=True,
    )

    amount_budget = fields.Float(
        string="Amount Budget",
        related="budget_id.amount",
        readonly=True,
    )

    tipe_kegiatan = fields.Selection(
        related="budget_id.tipe_kegiatan",
        string="Tipe Kegiatan",
        readonly=True,
    )

    jenis_penugasan = fields.Selection(
        related="budget_id.jenis_penugasan",
        string="Segmentasi",
        readonly=True,
    )

    amount_budget_remaining = fields.Float(
        string="Remaining",
        related="budget_id.remaining",
        readonly=True,
    )

    batas_waktu_izin_prinsip = fields.Date(
        string="Batas Waktu Izin Prinsip",
        tracking=True,
    )

    batas_waktu_reminder_sent = fields.Boolean(
        string="Reminder Batas Waktu Terkirim",
        default=False,
        copy=False,
    )

    is_expired = fields.Boolean(
        string="Tidak Berlaku",
        default=False,
        copy=False,
        readonly=True,
    )

    expired_date = fields.Date(
        string="Tanggal Tidak Berlaku",
        copy=False,
        readonly=True,
    )

    can_edit_batas_waktu = fields.Boolean(
        compute="_compute_can_edit_batas_waktu",
    )

    total_pagu = fields.Float(
        string="Total Pagu Izin Prinsip",
        compute="_compute_total_pagu",
        store=True,
    )

    total_qty_izin_prinsip = fields.Integer(
        string="Total Qty Izin Prinsip",
        compute="_compute_summary_totals",
        store=True,
    )

    total_amount_kontrak = fields.Float(
        string="Total Amount Kontrak",
        compute="_compute_summary_totals",
        store=True,
    )

    total_qty_kontrak = fields.Integer(
        string="Total Qty Kontrak",
        compute="_compute_summary_totals",
        store=True,
    )

    total_payment = fields.Float(
        string="Total Amount Payment",
        compute="_compute_total_payment",
        store=True,
    )

    total_amount_droping = fields.Float(
        string="Total Amount Droping",
        compute="_compute_summary_totals",
        readonly=True,
        store=True,
    )

    percent_realisasi_droping = fields.Float(
        string="Persentase Realisasi RKAP terhadap Dropping",
        related="budget_id.percent_realisasi_droping",
        readonly=True,
    )

    percent_realisasi_payment = fields.Float(
        string="Persentase Realisasi RKAP terhadap Payment",
        related="budget_id.percent_realisasi_payment",
        readonly=True,
    )

    previous_remaining = fields.Float(
        string="Previous Remaining",
        related="budget_id.previous_remaining",
        readonly=True,
        store=True,
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

    active = fields.Boolean(default=True)

    is_addendum = fields.Boolean(
        string="Is Addendum",
        default=False
    )

    addendum_origin_id = fields.Many2one(
        'vit.izin_prinsip',
        string="Izin Prinsip Induk",
        index=True,
        ondelete="cascade"
    )

    addendum_ids = fields.One2many(
        'vit.izin_prinsip',
        'addendum_origin_id',
        string="Addendums"
    )

    addendum_count = fields.Integer(
        string="Jumlah Addendum",
        compute="_compute_addendum_count",
        store=False,
    )

    def _compute_can_edit_batas_waktu(self):
        allowed = (
            self.env.su
            or self.env.user.has_group("vit_contract_inherit.group_vit_contract_pusat_umum")
            or self.env.user.has_group("vit_contract.group_vit_contract_manager")
        )
        for rec in self:
            rec.can_edit_batas_waktu = allowed

    @api.model_create_multi
    def create(self, vals_list):
        can_set_deadline = (
            self.env.context.get("allow_deadline_system_copy")
            or self.env.su
            or self.env.user.has_group("vit_contract_inherit.group_vit_contract_pusat_umum")
            or self.env.user.has_group("vit_contract.group_vit_contract_manager")
        )
        if not can_set_deadline:
            if any(vals.get("batas_waktu_izin_prinsip") for vals in vals_list):
                raise AccessError(_("Batas Waktu Izin Prinsip hanya dapat diisi oleh Pusat Umum atau Pusat Admin."))
        return super().create(vals_list)

    def write(self, vals):
        if "batas_waktu_izin_prinsip" in vals:
            can_edit_deadline = (
                self.env.su
                or self.env.user.has_group("vit_contract_inherit.group_vit_contract_pusat_umum")
                or self.env.user.has_group("vit_contract.group_vit_contract_manager")
            )
            if not can_edit_deadline:
                raise AccessError(_("Batas Waktu Izin Prinsip hanya dapat diubah oleh Pusat Umum atau Pusat Admin."))

            vals = dict(vals, batas_waktu_reminder_sent=False)
            new_deadline = fields.Date.to_date(vals.get("batas_waktu_izin_prinsip"))
            if new_deadline and new_deadline >= fields.Date.today():
                vals.update({
                    "active": True,
                    "is_expired": False,
                    "expired_date": False,
                })
        return super().write(vals)

    def action_confirm(self):
        missing_deadline = self.filtered(lambda record: not record.batas_waktu_izin_prinsip)
        if missing_deadline:
            raise ValidationError(_("Batas Waktu Izin Prinsip wajib diisi sebelum Izin Prinsip dikonfirmasi."))
        result = super().action_confirm()
        self._cron_check_izin_prinsip_deadline()
        self._send_activity_menu_refresh()
        return result

    def action_cancel(self):
        result = super().action_cancel()
        reminder_summary = _("Batas waktu Izin Prinsip akan berakhir")
        reminder_activities = self.mapped("activity_ids").filtered(
            lambda activity: activity.summary == reminder_summary
        )
        reminder_activities.sudo().unlink()
        self.sudo().write({"batas_waktu_reminder_sent": False})
        self._send_activity_menu_refresh()
        return result

    def _deadline_notification_users(self):
        self.ensure_one()
        kanca_ids = (self.kanca_id | self.job_izin_prinsip_ids.mapped("kanca_id")).ids
        Users = self.env["res.users"].sudo()
        kanwil_group = self.env.ref("vit_contract_inherit.group_vit_contract_kanwil")
        kanca_group = self.env.ref("vit_contract_inherit.group_vit_contract_kanca")
        users = Users.search([
            ("active", "=", True),
            ("share", "=", False),
            ("groups_id", "in", kanwil_group.id),
            ("multi_kanwil", "in", self.kanwil_id.ids),
        ])
        if kanca_ids:
            users |= Users.search([
                ("active", "=", True),
                ("share", "=", False),
                ("groups_id", "in", kanca_group.id),
                ("multi_kanca", "in", kanca_ids),
            ])
        return users

    def _send_activity_menu_refresh(self):
        users = self.env["res.users"]
        for record in self:
            users |= record._deadline_notification_users()
        partners = users.sudo().mapped("partner_id")
        if partners:
            self.env["bus.bus"]._sendmany([
                (partner, "vit.activity_menu/updated", {})
                for partner in partners
            ])

    @api.model
    def _cron_check_izin_prinsip_deadline(self):
        today = fields.Date.today()
        reminder_limit = today + timedelta(days=7)

        reminders = self.sudo().search([
            ("active", "=", True),
            ("stage_is_done", "=", True),
            ("batas_waktu_izin_prinsip", ">=", today),
            ("batas_waktu_izin_prinsip", "<=", reminder_limit),
            ("batas_waktu_reminder_sent", "=", False),
            ("kontrak_ids", "=", False),
        ])
        activity_type = self.env.ref("mail.mail_activity_data_todo")
        for record in reminders:
            for user in record._deadline_notification_users():
                record.activity_schedule(
                    activity_type_id=activity_type.id,
                    user_id=user.id,
                    date_deadline=record.batas_waktu_izin_prinsip,
                    summary=_("Batas waktu Izin Prinsip akan berakhir"),
                    note=_(
                        "Izin Prinsip %s akan berakhir pada %s dan belum memiliki kontrak. "
                        "Silakan tindak lanjuti kontrak atau koordinasikan pembatalan/perpanjangan "
                        "dengan Pusat Umum."
                    ) % (record.name, record.batas_waktu_izin_prinsip),
                )
            record.batas_waktu_reminder_sent = True

        expired_records = self.sudo().search([
            ("active", "=", True),
            ("stage_is_done", "=", True),
            ("batas_waktu_izin_prinsip", "<", today),
            ("kontrak_ids", "=", False),
            ("is_expired", "=", False),
        ])
        for record in expired_records:
            record.message_post(body=_(
                "Izin Prinsip otomatis menjadi tidak berlaku karena batas waktu %s telah lewat "
                "dan belum ada kontrak yang dibuat."
            ) % record.batas_waktu_izin_prinsip)
            record.write({
                "is_expired": True,
                "expired_date": today,
                "active": False,
            })

        return True

    # @api.model
    # def _domain_user(self, field_name):
    #     user = self.env.user

    #     if field_name == "kanwil_id":
    #         if user.multi_kanwil:
    #             return [("id", "in", user.multi_kanwil.ids)]
    #         else:
    #             return []

    #     elif field_name == "kanca_id":
    #         if user.multi_kanca:
    #             return [("id", "in", user.multi_kanca.ids)]
    #         else:
    #             return [] 

    #     return []

    def copy(self, default=None):
        default = dict(default or {})
        
        # Jika nama sudah di-set di default dict (saat addendum creation), gunakan itu
        # dan jangan tambahin "(Copy)"
        if 'name' in default:
            # Gunakan nama yang sudah di-set, jangan modify
            return models.BaseModel.copy(self, default)
        
        # Default behavior dari parent (dengan "(Copy)")
        return super(izin_prinsip, self).copy(default)

    @api.depends('created_by')
    def _compute_allowed_kanca(self):
        for rec in self:
            user = rec.created_by or self.env.user
            if user.multi_kanca:
                rec.allowed_kanca_id = user.multi_kanca[0].id
            else:
                rec.allowed_kanca_id = False

    def _get_root_origin(self):
        self.ensure_one()
        root = self
        while root.addendum_origin_id:
            root = root.addendum_origin_id
        return root

    @api.depends('addendum_ids', 'addendum_origin_id')
    def _compute_addendum_count(self):
        for rec in self:
            root = rec._get_root_origin()

            count = self.env['vit.izin_prinsip'].with_context(active_test=False).search_count(
                [('addendum_origin_id', '=', root.id)]
            )
            rec.addendum_count = count

    @api.model
    def check_access_rule(self, operation):
        res = super(izin_prinsip, self).check_access_rule(operation)

        if self.env.user.has_group('vit_contract_inherit.group_vit_contract_kanca'):
            for rec in self:
                if operation in ['write', 'unlink']:
                    if rec.created_by and rec.created_by.has_group('vit_contract_inherit.group_vit_contract_kanwil'):
                        raise AccessError(_("Record ini dibuat oleh User Kanwil. Anda adalah User Kanca tidak diperbolehkan mengubahnya."))
        return res

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




    # @api.model
    # def _domain_kanwil_user(self):
    #     user = self.env.user

    #     if user.has_group('vit_contract_inherit.group_vit_contract_kanwil'):
    #         return [('id', 'in', user.multi_kanwil.ids)] if user.multi_kanwil else [('id', '=', 0)]

    #     elif user.has_group('vit_contract_inherit.group_vit_contract_kanca'):
    #         kanwils = user.multi_kanca.mapped('kanwil_id')
    #         return [('id', 'in', kanwils.ids)] if kanwils else [('id', '=', 0)]

    #     return []
    # @api.model
    # def _domain_kanca_user(self):
    #     user = self.env.user
    #     if user.has_group("vit_contract_inherit.group_vit_contract_kanwil"):
    #         return [('kanwil_id', 'in', user.multi_kanwil.ids)] if user.multi_kanwil else [('id', '=', 0)]

    #     elif user.has_group("vit_contract_inherit.group_vit_contract_kanca"):
    #         return [('id', 'in', user.multi_kanca.ids)] if user.multi_kanca else [('id', '=', 0)]
    #     return []

    @api.depends("kontrak_ids.payment_ids.amount", "kanwil_id")
    def _compute_total_payment(self):
        for rec in self:
            total = 0.0
            if rec.kanwil_id and rec.kontrak_ids:
                payments = rec.mapped("kontrak_ids.payment_ids")

                filtered = payments.filtered(lambda p: p.kanwil_id == rec.kanwil_id)

                total = sum(filtered.mapped("amount"))

            rec.total_payment = total

    @api.depends("job_izin_prinsip_ids.total_pagu_job")
    def _compute_total_pagu(self):
        for rec in self:
            rec.total_pagu = sum(job.total_pagu_job for job in rec.job_izin_prinsip_ids)

    @api.depends(
        "kontrak_ids.amount_kontrak",
        "kontrak_ids.stage_is_done",
        "budget_id",
        "kanwil_id",
    )
    def _compute_summary_totals(self):
        Droping = self.env["vit.droping"].sudo()
        for rec in self:
            kontrak_done = rec.kontrak_ids.filtered(lambda k: k.stage_is_done)
            rec.total_qty_izin_prinsip = 1 if rec.id else 0
            rec.total_amount_kontrak = sum(kontrak_done.mapped("amount_kontrak"))
            rec.total_qty_kontrak = len(rec.kontrak_ids)

            total_droping = 0.0
            if rec.budget_id and rec.kanwil_id:
                dropings = Droping.search([
                    ("master_budget_id", "=", rec.budget_id.master_budget_id.id),
                    ("kanwil_id", "=", rec.kanwil_id.id),
                ])
                total_droping = sum(dropings.mapped("jumlah"))
            rec.total_amount_droping = total_droping

    # @api.constrains("total_pagu", "budget_id")
    # def _check_total_pagu_vs_budget(self):
    #     for rec in self:
    #         if rec.budget_id and rec.total_pagu > rec.budget_id.remaining:
    #             raise ValidationError(_(
    #                 "Total Pagu (%.2f) tidak boleh melebihi Remaining Budget RKAP (%.2f)!"
    #             ) % (rec.total_pagu, rec.budget_id.remaining))

    def action_create_addendum(self):
        from odoo.exceptions import UserError
        self.ensure_one()

        if self.addendum_ids:
            raise UserError(_("Izin Prinsip ini sudah punya Addendum, tidak bisa bikin lebih dari 1."))

        if not self.stage_id or self.stage_id.name.lower() != "draft":
            raise UserError(_("Addendum hanya bisa dibuat kalau Izin Prinsip di stage 'Draft'."))

        # Clean base name from (Copy) pattern
        base_name = self.name
        base_name = base_name.split(' (Copy)')[0] if ' (Copy)' in base_name else base_name
        
        if "-" in base_name:
            parts = base_name.split("-")
            try:
                last_num = int(parts[-1])
                new_name = f"{base_name}-{last_num+1}"
            except ValueError:
                new_name = f"{base_name}-1"
        else:
            new_name = f"{base_name}-1"

        draft_stage = self.env['vit.state_izin_prinsip'].search([('draft', '=', True)], limit=1)
        if not draft_stage:
            raise UserError(_("Stage DRAFT tidak ditemukan!"))

        # Determine root origin for addendum chain
        root_origin_id = self.addendum_origin_id.id if self.addendum_origin_id else self.id

        # Move current to done stage and set inactive
        done_stage = self.env['vit.state_izin_prinsip'].search([('name', '=ilike', 'done')], limit=1)
        if done_stage:
            self.stage_id = done_stage.id
        self.active = False

        # Create copy with addendum settings
        izin_copy = self.with_context(
            bypass_duplicate_check=True,
            skip_copy_name=True,
            allow_deadline_system_copy=True,
        ).copy({
            'name': new_name,
            'stage_id': draft_stage.id,
            'is_addendum': True,
            'addendum_origin_id': root_origin_id,
            'active': True,
        })

        # Copy job_izin_prinsip_ids
        new_jobs = []
        for job in self.job_izin_prinsip_ids:
            # Get base job name without (Copy) pattern
            base_job_name = job.name
            base_job_name = base_job_name.split(' (Copy)')[0] if ' (Copy)' in base_job_name else base_job_name
            
            # Generate new job name with numeric suffix like izin_prinsip
            if "-" in base_job_name:
                parts = base_job_name.split("-")
                try:
                    last_num = int(parts[-1])
                    new_job_name = f"{base_job_name}-{last_num+1}"
                except ValueError:
                    new_job_name = f"{base_job_name}-1"
            else:
                new_job_name = f"{base_job_name}-1"
            
            # Copy job with new name and all izin_prinsip_line_ids
            # Use context to prevent default (Copy) naming in copy method
            job_copy = job.with_context(skip_name_copy=True).copy({
                'izin_prinsip_id': izin_copy.id,
                'name': new_job_name,
            })
            
            # Manually copy izin_prinsip_line_ids dengan data lengkap
            new_lines = []
            for line in job.izin_prinsip_line_ids:
                line_copy = line.copy({
                    'job_izin_prinsip_id': job_copy.id,
                    'jenis_kontrak_id': line.jenis_kontrak_id.id if line.jenis_kontrak_id else False,
                    'kanwil_id': line.kanwil_id.id if line.kanwil_id else False,
                    'kanca_id': line.kanca_id.id if line.kanca_id else False,
                    'pagu': line.pagu,
                    'name': line.name,
                })
                new_lines.append(line_copy.id)
            
            # Update job dengan line yang baru
            if new_lines:
                job_copy.izin_prinsip_line_ids = [(6, 0, new_lines)]
            
            new_jobs.append(job_copy.id)

        izin_copy.job_izin_prinsip_ids = [(6, 0, new_jobs)]

        # Copy attachments
        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'vit.izin_prinsip'),
            ('res_id', '=', self.id)
        ])
        for att in attachments:
            att.copy({'res_id': izin_copy.id})

        return {
            'name': _('Izin Prinsip Addendum'),
            'type': 'ir.actions.act_window',
            'res_model': 'vit.izin_prinsip',
            'view_mode': 'form',
            'res_id': izin_copy.id,
            'target': 'current',
        }

    def action_view_addendums(self):
        self.ensure_one()
        # Find root origin if this is an addendum
        root_id = self.id
        if self.addendum_origin_id:
            root_id = self.addendum_origin_id.id
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Addendums'),
            'res_model': 'vit.izin_prinsip',
            'view_mode': 'tree,form',
            'domain': ['|', ('addendum_origin_id', '=', root_id), ('id', '=', root_id)],
            'context': dict(self.env.context, active_test=False, default_addendum_origin_id=root_id),
        }

    def action_view_origin_izin_prinsip(self):
        self.ensure_one()
        if not self.addendum_origin_id:
            return False
        
        root_id = self.addendum_origin_id.id
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Izin Prinsip Asal'),
            'res_model': 'vit.izin_prinsip',
            'view_mode': 'tree,form',
            'domain': ['|', ('addendum_origin_id', '=', root_id), ('id', '=', root_id)],
            'context': dict(self.env.context, active_test=False, default_addendum_origin_id=root_id),
        }
