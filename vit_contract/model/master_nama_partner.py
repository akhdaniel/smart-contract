#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class master_nama_partner(models.Model):

    _name = "vit.master_nama_partner"
    _description = "vit.master_nama_partner"


    def action_reload_view(self):
        pass

    name = fields.Char( required=True, copy=False, string=_("Name"))


    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'name': self.name + ' (Copy)'
        })
        return super(master_nama_partner, self).copy(default)

    partner_id = fields.Many2one(comodel_name="res.partner",  string=_("Partner"))
