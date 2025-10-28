#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging
_logger = logging.getLogger(__name__)

class budget_rkap(models.Model):
    _inherit = "vit.budget_rkap"

    name = fields.Char( 
        required=True, 
        copy=False, 
        string=_("Name")
    )

    amount = fields.Float(
        required=True, 
        string=_("Amount"),
    )

    master_budget_id = fields.Many2one(
        required=True, 
        comodel_name="vit.master_budget",  
        string=_("Master Budget"),
    )

    budget_date = fields.Date(
        string="Budget Date",
    )

    budget_year = fields.Char(
        string="Budget Year",
        compute="_compute_budget_year",
    )


    previous_year_id = fields.Many2one(
        comodel_name="vit.budget_rkap",
        string="Previous Year Budget",
        readonly=True,
        store=True,
    )


    previous_remaining = fields.Float(
        string="Previous Remaining",
        compute="_compute_previous_remaining",
        store=True,
        readonly=True,
    )


    remaining = fields.Float(
        string="Remaining",
        compute="_compute_remaining",
        readonly=True,
        store=True,
    )

    total_pagu_izin_prinsip = fields.Float(
        string="Total Pagu Izin Prinsip",
        compute="_compute_totals",
        readonly=True,
        store=True,
    )
    total_amount_kontrak = fields.Float(
        string="Total Amount Kontrak",
        compute="_compute_totals",
        readonly=True,
        store=True,
    )
    total_amount_payment = fields.Float(
        string="Total Amount Payment",
        compute="_compute_totals",
        readonly=True,
        store=True,
    )
    total_qty_izin_prinsip = fields.Integer(
        string="Total Qty Izin Prinsip",
        readonly=True,
        compute="_compute_totals",
        store=True,
    )
    total_qty_kontrak = fields.Integer(
        string="Total Qty Kontrak",
        readonly=True,
        store=True,
    )

    total_qty_termin = fields.Integer(
        string="Total Qty Termin",
        compute="_compute_total_qty_termin",
        store=True,
        readonly=True,
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

    @api.depends('budget_date')
    def _compute_budget_year(self):
        for rec in self:
            rec.budget_year = rec.budget_date.strftime("%Y") if rec.budget_date else ''



    @api.model
    def create(self, vals):
        if not vals.get('budget_date'):
            vals['budget_date'] = fields.Date.today()

        if (not vals.get('name') or vals['name'] in [False, None, '', 'New']) and vals.get('master_budget_id'):
            master = self.env['vit.master_budget'].browse(vals['master_budget_id'])
            if master and master.name:
                vals['name'] = master.name

        if not vals.get('name'):
            vals['name'] = 'Tanpa Nama'

        budget_date = fields.Date.from_string(vals['budget_date'])
        tahun_ini = budget_date.year
        tahun_lalu = tahun_ini - 1

        master_budget_id = vals.get('master_budget_id')
        previous_year_id = False

        if master_budget_id:
            prev_budget = self.env['vit.budget_rkap'].search([
                ('master_budget_id', '=', master_budget_id),
                ('budget_date', '>=', f'{tahun_lalu}-01-01'),
                ('budget_date', '<=', f'{tahun_lalu}-12-31'),
            ], limit=1, order='budget_date desc')

            if prev_budget:
                previous_year_id = prev_budget.id

        vals['previous_year_id'] = previous_year_id

        record = super(budget_rkap, self).create(vals)
        return record


    @api.depends('previous_year_id.remaining')
    def _compute_previous_remaining(self):
        for rec in self:
            rec.previous_remaining = rec.previous_year_id.remaining if rec.previous_year_id else 0.0










    
    # def write(self, vals):
    #     if 'budget_date' in vals:
    #         vals.pop('budget_date')
    #     return super(budget_rkap, self).write(vals)


    @api.constrains('amount')
    def _check_amount_not_empty(self):
        for rec in self:
            if not rec.amount or rec.amount == 0.0:
                raise ValidationError(_("Amount tidak boleh kosong atau bernilai 0."))






    @api.depends(
        "izin_prinsip_ids.total_pagu",
        "izin_prinsip_ids.stage_is_done",
        "kontrak_ids.amount_kontrak",
        "kontrak_ids.stage_is_done",
        "payment_ids.amount",
        "payment_ids.stage_is_done",
    )
    def _compute_totals(self):
        Droping = self.env["vit.droping"].sudo()
        for rec in self.sudo():
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
            rec.total_qty_kontrak = len(rec.kontrak_ids)
            rec.total_qty_payment = len(payment_done)







    @api.depends("amount", "total_amount_payment")
    def _compute_remaining(self):
        for rec in self:
            rec.remaining = rec.amount - rec.total_amount_payment


    def download_budget(self):
        pass
