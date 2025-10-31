#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class master_users(models.Model):

    _name = "vit.master_users"
    _description = "vit.master_users"


    def action_reload_view(self):
        pass

    name = fields.Char( required=True, copy=False, string=_("Name"))


    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'name': self.name + ' (Copy)'
        })
        return super(master_users, self).copy(default)

    users_id = fields.Many2one(comodel_name="res.users",  string=_("Users"))
