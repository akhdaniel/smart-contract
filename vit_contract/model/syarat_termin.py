#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class syarat_termin(models.Model):

    _name = "vit.syarat_termin"
    _description = "vit.syarat_termin"


    def action_reload_view(self):
        pass

    name = fields.Char( required=True, copy=False, string=_("Name"))
    verified = fields.Boolean( string=_("Verified"))
    due_date = fields.Date( string=_("Due Date"))
    document = fields.Binary(filename="document_filename",  string=_("Document"))
    document_filename = fields.Char( string=_("Document Filename"))
    upload_date = fields.Date( string=_("Upload Date"))


    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'name': self.name + ' (Copy)'
        })
        return super(syarat_termin, self).copy(default)

    termin_id = fields.Many2one(comodel_name="vit.termin",  string=_("Termin"))
    master_syarat_termin_id = fields.Many2one(comodel_name="vit.master_syarat_termin",  string=_("Master Syarat Termin"))
