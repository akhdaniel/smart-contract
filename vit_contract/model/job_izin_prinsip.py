#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class job_izin_prinsip(models.Model):

    _name = "vit.job_izin_prinsip"
    _description = "vit.job_izin_prinsip"


    def action_reload_view(self):
        pass

    name = fields.Char( required=True, copy=False, string=_("Name"))
    total_pagu_job = fields.Float( string=_("Total Pagu Job"))


    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'name': self.name + ' (Copy)'
        })
        return super(job_izin_prinsip, self).copy(default)

    izin_prinsip_line_ids = fields.One2many(comodel_name="vit.izin_prinsip_line",  inverse_name="job_izin_prinsip_id",  string=_("Izin Prinsip Line"))
    izin_prinsip_id = fields.Many2one(comodel_name="vit.izin_prinsip",  string=_("Izin Prinsip"))
    kanca_id = fields.Many2one(comodel_name="vit.kanca",  string=_("Kanca"))
    kompleks_id = fields.Many2one(comodel_name="vit.kompleks_pergudangan",  string=_("Kompleks"))
