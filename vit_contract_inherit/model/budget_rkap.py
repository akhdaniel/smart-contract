#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class budget_rkap(models.Model):
    _inherit = "vit.budget_rkap"

    budget_date = fields.Date(
        string='Budget Date',
    )

    remaining = fields.Float(
        string="Remaining",
        compute="_compute_remaining",
        store=True,
    )

    total_pagu_izin_prinsip = fields.Float(
        string="Total Pagu Izin Prinsip",
        compute="_compute_totals",
        store=True,
    )
    total_amount_kontrak = fields.Float(
        string="Total Amount Kontrak",
        compute="_compute_totals",
        store=True,
    )
    total_amount_payment = fields.Float(
        string="Total Amount Payment",
        compute="_compute_totals",
        store=True,
    )
    total_qty_izin_prinsip = fields.Integer(
        string="Total Qty Izin Prinsip",
        compute="_compute_totals",
        store=True,
    )
    total_qty_kontrak = fields.Integer(
        string="Total Qty Kontrak",
        compute="_compute_totals",
        store=True,
    )
    total_qty_payment = fields.Integer(
        string="Total Qty Payment",
        compute="_compute_totals",
        store=True,
    )

    total_amount_droping = fields.Float(
        string="Total Amount Droping",
        compute="_compute_totals",
        store=False,
    )


    @api.model
    def create(self, vals):
        if not vals.get('budget_date'):
            vals['budget_date'] = fields.Date.today()
        return super(budget_rkap, self).create(vals)
    
    def write(self, vals):
        if 'budget_date' in vals:
            vals.pop('budget_date')
        return super(budget_rkap, self).write(vals)



    @api.depends(
        "izin_prinsip_ids.total_pagu",
        "izin_prinsip_ids.stage_is_done",
        "kontrak_ids.amount_kontrak",
        "kontrak_ids.stage_is_done",
        "payment_ids.amount",
        "payment_ids.stage_is_done",
    )
    def _compute_totals(self):
        Droping = self.env["vit.droping"]

        for rec in self:
            izin_done = rec.izin_prinsip_ids.filtered(lambda i: i.stage_is_done)
            kontrak_done = rec.kontrak_ids.filtered(lambda k: k.stage_is_done)
            payment_done = rec.payment_ids.filtered(lambda p: p.stage_is_done)

            total_droping = 0
            if rec.master_budget_id:
                dropings = Droping.search([("master_budget_id", "=", rec.master_budget_id.id)])
                total_droping = sum(dropings.mapped("jumlah"))

            rec.total_pagu_izin_prinsip = sum(izin_done.mapped("total_pagu"))
            rec.total_amount_kontrak = sum(kontrak_done.mapped("amount_kontrak"))
            rec.total_amount_payment = sum(payment_done.mapped("amount"))
            rec.total_amount_droping = total_droping

            rec.total_qty_izin_prinsip = len(izin_done)
            rec.total_qty_kontrak = len(kontrak_done)
            rec.total_qty_payment = len(payment_done)







    @api.depends("amount", "total_amount_payment")
    def _compute_remaining(self):
        for rec in self:
            rec.remaining = rec.amount - rec.total_amount_payment


    def download_budget(self):
        pass
