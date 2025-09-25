#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class master_stage(models.Model):
    _name = "master.stage"
    _inherit = "master.stage"
