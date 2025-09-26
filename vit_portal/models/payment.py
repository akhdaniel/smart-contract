#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class payment(models.Model):
    _name = "vit.payment"
    _inherit = "vit.payment"

    kontrak_id = fields.Many2one(
        comodel_name='vit.kontrak',
        string="Kontrak"
    )