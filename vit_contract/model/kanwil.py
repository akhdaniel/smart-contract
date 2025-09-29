#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class kanwil(models.Model):

    _name = "vit.kanwil"
    _description = "vit.kanwil"


    def action_reload_view(self):
        pass

    name = fields.Char( required=True, copy=False, string=_("Name"))


    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'name': self.name + ' (Copy)'
        })
        return super(kanwil, self).copy(default)

    kontrak_ids = fields.One2many(comodel_name="vit.kontrak",  inverse_name="kanwil_id",  string=_("Kontrak"))
    droping_ids = fields.One2many(comodel_name="vit.droping",  inverse_name="kanwil_id",  string=_("Droping"))
    kanca_ids = fields.One2many(comodel_name="vit.kanca",  inverse_name="kanwil_id",  string=_("Kanca"))
