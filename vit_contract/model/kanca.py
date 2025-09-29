#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class kanca(models.Model):

    _name = "vit.kanca"
    _description = "vit.kanca"


    def action_reload_view(self):
        pass

    name = fields.Char( required=True, copy=False, string=_("Name"))


    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'name': self.name + ' (Copy)'
        })
        return super(kanca, self).copy(default)

    kanwil_id = fields.Many2one(comodel_name="vit.kanwil",  string=_("Kanwil"))
