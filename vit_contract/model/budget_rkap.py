#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class budget_rkap(models.Model):

    _name = "vit.budget_rkap"
    _description = "vit.budget_rkap"


    def download_budget(self, ):
        pass


    def action_reload_view(self):
        pass

    name = fields.Char( required=True, copy=False, string=_("Name"))
    amount = fields.Float( string=_("Amount"))
    remaining = fields.Float( string=_("Remaining"))
    total_pagu_izin_prinsip = fields.Float( string=_("Total Pagu Izin Prinsip"))
    total_amount_kontrak = fields.Float( string=_("Total Amount Kontrak"))
    total_amount_payment = fields.Float( string=_("Total Amount Payment"))
    total_qty_izin_prinsip = fields.Integer( string=_("Total Qty Izin Prinsip"))
    total_qty_kontrak = fields.Integer( string=_("Total Qty Kontrak"))
    total_amount_droping = fields.Float( string=_("Total Amount Droping"))
    budget_date = fields.Date( string=_("Budget Date"))


    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'name': self.name + ' (Copy)'
        })
        return super(budget_rkap, self).copy(default)

    izin_prinsip_ids = fields.One2many(comodel_name="vit.izin_prinsip",  inverse_name="budget_id",  string=_("Izin Prinsip"))
    master_budget_id = fields.Many2one(comodel_name="vit.master_budget",  string=_("Master Budget"))
    kontrak_ids = fields.One2many(comodel_name="vit.kontrak",  inverse_name="budget_rkap_id",  string=_("Kontrak"))
    payment_ids = fields.One2many(comodel_name="vit.payment",  inverse_name="budget_rkap_id",  string=_("Payment"))
