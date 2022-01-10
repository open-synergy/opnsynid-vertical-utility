# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class UtilityMeterReadingMultiplier(models.Model):
    _name = "utility.meter_reading_multiplier"
    _description = "Utility Meter Reading Multiplier"
    _order = "sequence, id"

    meter_reading_id = fields.Many2one(
        string="# Meter Reading",
        comodel_name="utility.meter_reading",
        required=True,
        ondelete="cascade",
    )
    item_id = fields.Many2one(
        string="Multiplier Item",
        comodel_name="utility.meter_reading_multiplier_item",
        required=True,
    )
    sequence = fields.Integer(
        string="Sequence",
        required=True,
        readonly=True,
    )
    multiplier = fields.Float(
        string="Multiplier",
        required=True,
        readonly=True,
    )
