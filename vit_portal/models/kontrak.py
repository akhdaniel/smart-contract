#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)

class kontrak(models.Model):
    _name = "vit.kontrak"
    _inherit = "vit.kontrak"

    payment_ids = fields.One2many(
        comodel_name='vit.payment', inverse_name="kontrak_id"
    )