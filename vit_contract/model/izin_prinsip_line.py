#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class izin_prinsip_line(models.Model):

    _name = "vit.izin_prinsip_line"
    _description = "vit.izin_prinsip_line"


    def action_reload_view(self):
        pass

    name = fields.Char( required=True, copy=False, string=_("Name"))
    pagu = fields.Float( string=_("Pagu"))


    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'name': self.name + ' (Copy)'
        })
        return super(izin_prinsip_line, self).copy(default)

    jenis_kontrak_id = fields.Many2one(comodel_name="vit.jenis_kontrak",  string=_("Jenis Kontrak"))
    kanwil_id = fields.Many2one(comodel_name="vit.kanwil",  string=_("Kanwil"))
    kanca_id = fields.Many2one(comodel_name="vit.kanca",  string=_("Kanca"))
    job_izin_prinsip_id = fields.Many2one(comodel_name="vit.job_izin_prinsip",  string=_("Job Izin Prinsip"))
