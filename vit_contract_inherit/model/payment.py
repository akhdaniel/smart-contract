#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class payment(models.Model):
    _name = "vit.payment"
    _inherit = ["vit.payment", "mail.thread", "mail.activity.mixin"]

    attachments = fields.Many2many(
        'ir.attachment',
        string='Upload'
    )

    partner_bank_id = fields.Many2one(
        "res.partner.bank",
        related="kontrak_id.partner_bank_id",
        string="Rekening Pembayaran",
        store=True,
        readonly=True,
    )
    payment_bank_name = fields.Char(
        related="kontrak_id.payment_bank_name",
        string="Nama Bank",
        store=True,
        readonly=True,
    )
    payment_bank_acc_number = fields.Char(
        related="kontrak_id.payment_bank_acc_number",
        string="Nomor Rekening",
        store=True,
        readonly=True,
    )
    payment_bank_acc_holder = fields.Char(
        related="kontrak_id.payment_bank_acc_holder",
        string="Atas Nama Rekening",
        store=True,
        readonly=True,
    )

    name = fields.Char( required=True, copy=False, default="New", readonly=True,  string=_("Name"))



    def action_confirm(self):
        for rec in self:
            old_stage = rec.stage_id.name or "Unknown Stage"
            
            next_stage = self.env['vit.state_payment'].search(
                [('sequence', '>', rec.stage_id.sequence)],
                order='sequence asc',
                limit=1
            )
            if next_stage:
                rec.stage_id = next_stage.id
            else:
                raise UserError(_("Tidak ada stage berikutnya yang tersedia."))

            new_stage = rec.stage_id.name or "Unknown Stage"

            rec.message_post(
                body=_("✅ Stage pembayaran berpindah dari %s ke %s oleh %s.") % (
                    old_stage, new_stage, self.env.user.name),
                message_type="comment"
            )

        return True
    
    def action_cancel(self):
        for rec in self:
            old_stage = rec.stage_id.name or "Unknown Stage"

            prev_stage = self.env['vit.state_payment'].search(
                [('sequence', '<', rec.stage_id.sequence)],
                order='sequence desc',
                limit=1
            )
            if not prev_stage:
                raise UserError(_("Tidak ada stage sebelumnya."))

            rec.stage_id = prev_stage.id
            new_stage = rec.stage_id.name or "Unknown Stage"

            rec.message_post(
                body=_("❌ Stage pembayaran dibatalkan dari %s ke %s oleh %s.") % (
                    old_stage, new_stage, self.env.user.name),
                message_type="comment"
            )

        return True

    def kirim_request_pembayaran(self, ):
        pass
