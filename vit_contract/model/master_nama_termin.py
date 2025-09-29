#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class master_nama_termin(models.Model):

    _name = "vit.master_nama_termin"
    _description = "vit.master_nama_termin"

    _order = "sequence asc"

    def action_reload_view(self):
        pass

    name = fields.Char( required=True, copy=False, string=_("Name"))
    sequence = fields.Integer( string=_("Sequence"))
    type = fields.Selection(selection=[('is_dp', 'DP'),('is_retensi', 'Retensi'),('is_termin', 'Termin')],  string=_("Type"))


    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'name': self.name + ' (Copy)'
        })
        return super(master_nama_termin, self).copy(default)

