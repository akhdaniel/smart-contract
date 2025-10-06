#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class jenis_kontrak(models.Model):

    _name = "vit.jenis_kontrak"
    _description = "vit.jenis_kontrak"


    def action_reload_view(self):
        pass

    name = fields.Char( required=True, copy=False, string=_("Name"))
    type = fields.Selection(selection=[('fisik', 'Fisik'),('non_fisik', 'Non Fisik')],  string=_("Type"))


    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'name': self.name + ' (Copy)'
        })
        return super(jenis_kontrak, self).copy(default)

