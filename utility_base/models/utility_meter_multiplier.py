# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class UtilityMeterMultiplier(models.Model):
    _name = "utility.meter_multiplier"
    _description = "Utility Meter Multiplier"
    _order = "sequence, id"

    meter_id = fields.Many2one(
        string="Utility Meter",
        comodel_name="utility.meter",
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

    @api.multi
    def _generate_multiplier(self):
        self.ensure_one()
        return (0, 0, {
            "item_id": self.item_id.id,
            "sequence": self.sequence,
            "multiplier": self.multiplier,
        })

    @api.onchange(
        "item_id",
    )
    def onchange_multiplier(self):
        self.multiplier = 1.0
        obj_multiplier = self.env["utility.type_multiplier"]
        if self.item_id:
            criteria = [
                ("type_id", "=", self.meter_id.type_id.id),
                ("item_id", "=", self.item_id.id)
            ]
            multipliers = obj_multiplier.search(criteria)
            if len(multipliers) > 0:
                multiplier = multipliers[0]
                self.multiplier = multiplier.multiplier
