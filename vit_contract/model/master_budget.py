#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class master_budget(models.Model):

    _name = "vit.master_budget"
    _description = "vit.master_budget"

    _order = "sequence asc"

    def action_reload_view(self):
        pass

    name = fields.Char( required=True, copy=False, string=_("Name"))
    jenis_penugasan = fields.Selection(selection=[('pso', 'Pso'),('kom', 'Kom')],  string=_("Jenis Penugasan"))
    sequence = fields.Integer( string=_("Sequence"))


    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'name': self.name + ' (Copy)'
        })
        return super(master_budget, self).copy(default)

