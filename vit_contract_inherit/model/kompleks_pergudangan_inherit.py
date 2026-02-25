#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VitKompleksPergudangan(models.Model):
    _inherit = 'vit.kompleks_pergudangan'


    name = fields.Char( required=True, copy=False, string=_("Name"))

    kanwil_id = fields.Many2many(
        string=_('Kanwil'),
        store=True,
    )

    kanca_id = fields.Many2many(
        comodel_name='vit.kanca',
        string=_('Kanca'),
        store=True,
    )
