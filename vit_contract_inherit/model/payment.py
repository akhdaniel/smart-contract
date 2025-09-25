#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class payment(models.Model):
    _name = "vit.payment"
    _inherit = "vit.payment"

    name = fields.Char( required=True, copy=False, default="New", readonly=True,  string=_("Name"))

    def kirim_request_pembayaran(self, ):
        pass

