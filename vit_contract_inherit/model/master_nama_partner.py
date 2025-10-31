#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class master_nama_partner(models.Model):

    _inherit = "vit.master_nama_partner"


    name = fields.Char( required=False, copy=False, string=_("Nama Vendor"))