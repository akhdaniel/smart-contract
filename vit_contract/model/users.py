#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class users(models.Model):

    _name = "res.users"
    _description = "res.users"


    def action_reload_view(self):
        pass


    _inherit = "res.users"


