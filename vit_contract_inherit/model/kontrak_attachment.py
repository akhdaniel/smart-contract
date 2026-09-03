#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class KontrakAttachment(models.Model):
    _name = "vit.kontrak_attachment"
    _description = "Dokumen Kontrak per Termin"
    _order = "upload_date desc, id desc"

    name = fields.Char(string=_("Nama Dokumen"), required=True)
    kontrak_id = fields.Many2one(
        comodel_name="vit.kontrak",
        string=_("Kontrak"),
        required=True,
        ondelete="cascade",
    )
    termin_id = fields.Many2one(
        comodel_name="vit.termin",
        string=_("Termin"),
        required=True,
        ondelete="cascade",
    )
    document = fields.Binary(string=_("Dokumen"), required=True, attachment=True)
    filename = fields.Char(string=_("Filename"))
    upload_date = fields.Date(
        string=_("Upload Date"),
        default=fields.Date.context_today,
        required=True,
    )

    @api.constrains("kontrak_id", "termin_id")
    def _check_termin_contract(self):
        for rec in self:
            if rec.termin_id and rec.kontrak_id and rec.termin_id.kontrak_id != rec.kontrak_id:
                raise ValidationError(_("Termin harus berasal dari kontrak yang sama."))

    @api.onchange("filename")
    def _onchange_filename(self):
        for rec in self:
            if rec.filename and not rec.name:
                rec.name = rec.filename

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") and vals.get("filename"):
                vals["name"] = vals["filename"]
        return super().create(vals_list)
