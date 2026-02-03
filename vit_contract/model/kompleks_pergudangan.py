#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class kompleks_pergudangan(models.Model):

    _name = "vit.kompleks_pergudangan"
    _description = "vit.kompleks_pergudangan"


    def action_reload_view(self):
        pass

    name = fields.Char( required=True, copy=False, string=_("Name"))


    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'name': self.name + ' (Copy)'
        })
        return super(kompleks_pergudangan, self).copy(default)

    kanca_id = fields.Many2one(comodel_name="vit.kanca",  string=_("Kanca"))
