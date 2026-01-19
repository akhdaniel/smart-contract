#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError
import logging
_logger = logging.getLogger(__name__)

class izin_prinsip(models.Model):
    _inherit = "vit.izin_prinsip"

    name = fields.Char(required=True, copy=False, string="Name", default=False)

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

    total_pagu = fields.Float(
        string="Total Pagu",
        compute="_compute_total_pagu",
        store=True,
    )

    total_payment = fields.Float(
        string="Total Payment",
        compute="_compute_total_payment",
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


    @api.depends('created_by')
    def _compute_allowed_kanca(self):
        for rec in self:
            user = rec.created_by or self.env.user
            if user.multi_kanca:
                rec.allowed_kanca_id = user.multi_kanca[0].id
            else:
                rec.allowed_kanca_id = False

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

    @api.constrains("total_pagu", "budget_id")
    def _check_total_pagu_vs_budget(self):
        for rec in self:
            if rec.budget_id and rec.total_pagu > rec.budget_id.amount:
                raise ValidationError(_(
                    "Total Pagu (%.2f) tidak boleh melebihi Amount Budget RKAP (%.2f)!"
                ) % (rec.total_pagu, rec.budget_id.amount))
