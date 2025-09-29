#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class partner(models.Model):

    _name = "res.partner"
    _description = "res.partner"


    def action_reload_view(self):
        pass

    _inherit = "res.partner"



    payment_ids = fields.One2many(comodel_name="vit.payment",  inverse_name="partner_id",  string=_("Payment"))
