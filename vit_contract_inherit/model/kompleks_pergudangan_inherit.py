#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, _


class VitKompleksPergudangan(models.Model):
    _inherit = 'vit.kompleks_pergudangan'

    # derive kanwil from related kanca record; stored for searching/grouping
    kanwil_id = fields.Many2one(
        comodel_name='vit.kanwil',
        string=_('Kanwil'),
        related='kanca_id.kanwil_id',
        store=True,
    )
