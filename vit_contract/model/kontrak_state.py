#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class kontrak_state(models.Model):
    """
    {
    "is_a_stage":true,
    "data":[{"name":"Draft","sequence":20,"draft":true, "on_progress":false, "done":false, "fold":false, "allow_confirm":true},
            {"name":"On Progress", "sequence":30,"draft":false, "on_progress":true, "done":false, "fold":false, "allow_confirm":true},
            {"name":"Done", "sequence":40,"draft":false, "on_progress":false, "done":true, "fold":false}]
    }
    """

    _name = "vit.kontrak_state"
    _description = "vit.kontrak_state"

    _order = "sequence asc"

    def action_reload_view(self):
        pass

    name = fields.Char( required=True, copy=False, string=_("Name"))
    sequence = fields.Integer( string=_("Sequence"))
    draft = fields.Boolean( string=_("Draft"))
    done = fields.Boolean( string=_("Done"))
    open = fields.Boolean( string=_("Open"))
    fold = fields.Boolean( string=_("Fold"))
    allow_confirm = fields.Boolean( string=_("Allow Confirm"))
    allow_cancel = fields.Boolean( string=_("Allow Cancel"))
    execute_enter = fields.Char( string=_("Execute Enter"))
    confirmation = fields.Char( string=_("Confirmation"))
    on_progress = fields.Boolean( string=_("On Progress"))


    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'name': self.name + ' (Copy)'
        })
        return super(kontrak_state, self).copy(default)

