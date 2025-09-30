#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class kontrak(models.Model):

    _name = "vit.kontrak"
    _description = "vit.kontrak"


    def action_create_addendum(self, ):
        pass


    def action_reload_view(self):
        pass

    name = fields.Char( required=True, copy=False, default="New", readonly=True,  string=_("Name"))
    start_date = fields.Date( string=_("Start Date"))
    end_date = fields.Date( string=_("End Date"))
    stage_is_draft = fields.Boolean(related="stage_id.draft", store=True,  string=_("Stage Is Draft"))
    stage_is_done = fields.Boolean(related="stage_id.done", store=True,  string=_("Stage Is Done"))
    allow_confirm = fields.Boolean(related="stage_id.allow_confirm", store=True,  string=_("Allow Confirm"))
    allow_cancel = fields.Boolean(related="stage_id.allow_cancel", store=True,  string=_("Allow Cancel"))
    stage_name = fields.Char(related="stage_id.name", store=True,  string=_("Stage Name"))
    amount_izin_prinsip = fields.Float(readonly=True,  string=_("Amount Izin Prinsip"))
    amount_kontrak = fields.Float( string=_("Amount Kontrak"))
    amount_denda = fields.Float( string=_("Amount Denda"))
    persentasi_denda = fields.Float( string=_("Persentasi Denda"))
    overdue_days = fields.Integer( string=_("Overdue Days"))


    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if not val.get("name", False) or val["name"] == "New":
                val["name"] = self.env["ir.sequence"].next_by_code("vit.kontrak") or "Error Number!!!"
        return super(kontrak, self).create(vals)

    def _get_first_stage(self):
        try:
            data_id = self.env["vit.kontrak_state"].sudo().search([], limit=1, order="sequence asc")
            if data_id:
                return data_id
        except KeyError:
            return False

    def action_confirm(self):
        stage = self._get_next_stage()
        self.stage_id=stage
        if self.stage_id.execute_enter and hasattr(self, self.stage_id.execute_enter) and callable(getattr(self, self.stage_id.execute_enter)):
            eval(f"self.{self.stage_id.execute_enter}()")

    def action_cancel(self):
        stage = self._get_previous_stage()
        self.stage_id=stage

    def _get_next_stage(self):
        current_stage_seq = self.stage_id.sequence
        data_id = self.env["vit.kontrak_state"].sudo().search([("sequence",">",current_stage_seq)], limit=1, order="sequence asc")
        if data_id:
            return data_id
        else:
            return self.stage_id

    def _get_previous_stage(self):
        current_stage_seq = self.stage_id.sequence
        data_id = self.env["vit.kontrak_state"].sudo().search([("sequence","<",current_stage_seq)], limit=1, order="sequence desc")
        if data_id:
            return data_id
        else:
            return self.stage_id

    @api.model
    def _group_expand_states(self, stages, domain, order):
        return self.env['vit.kontrak_state'].search([])

    def unlink(self):
        for me_id in self :
            if not me_id.stage_id.draft:
                raise UserError("Cannot delete non draft record!  Make sure that the Stage draft flag is checked.")
        return super(kontrak, self).unlink()

    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'name': self.name + ' (Copy)'
        })
        return super(kontrak, self).copy(default)

    izin_prinsip_id = fields.Many2one(comodel_name="vit.izin_prinsip",  string=_("Izin Prinsip"))
    budget_rkap_id = fields.Many2one(comodel_name="vit.budget_rkap",  string=_("Budget Rkap"))
    stage_id = fields.Many2one(comodel_name="vit.kontrak_state",  default=_get_first_stage, copy=False, group_expand="_group_expand_states",  string=_("Stage"))
    jenis_kontrak_id = fields.Many2one(comodel_name="vit.jenis_kontrak",  string=_("Jenis Kontrak"))
    master_budget_id = fields.Many2one(comodel_name="vit.master_budget",  string=_("Master Budget"))
    kanca_id = fields.Many2one(comodel_name="vit.kanca",  string=_("Kanca"))
    kanwil_id = fields.Many2one(comodel_name="vit.kanwil",  string=_("Kanwil"))
    partner_id = fields.Many2one(comodel_name="res.partner",  string=_("Partner"))
    job_izin_prinsip_id = fields.Many2one(comodel_name="vit.job_izin_prinsip",  string=_("Job Izin Prinsip"))
    payment_ids = fields.One2many(comodel_name="vit.payment",  inverse_name="kontrak_id",  string=_("Payment"))
    termin_ids = fields.One2many(comodel_name="vit.termin",  inverse_name="kontrak_id",  string=_("Termin"))
