# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class UtilityTypeMultiplier(models.Model):
    _name = "utility.type_multiplier"
    _description = "Utility Type Multiplier"
    _order = "sequence, id"

    type_id = fields.Many2one(
        string="Utility Type",
        comodel_name="utility.type",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(
        string="Sequence",
        required=True,
        default=5,
    )
    item_id = fields.Many2one(
        string="Multiplier Item",
        comodel_name="utility.meter_reading_multiplier_item",
        required=True,
    )
    multiplier = fields.Float(
        string="Multiplier",
        required=True,
        default=1.0,
    )

    @api.onchange(
        "item_id",
    )
    def onchange_multiplier(self):
        self.multiplier = 1.0
        if self.item_id:
            self.multiplier = self.item_id.multiplier
