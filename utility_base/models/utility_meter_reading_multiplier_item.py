# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class UtilityMeterReadingMultiplierItem(models.Model):
    _name = "utility.meter_reading_multiplier_item"
    _description = "Utility Meter Reading Multiplier Item"

    name = fields.Char(
        string="Item",
        required=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
    )
    default_sequence = fields.Integer(
        string="Default Sequence",
        required=True,
        default=5,
    )
    multiplier = fields.Float(
        string="Multiplier",
        required=True,
        default=1.0,
    )
    allowed_utility_type_ids = fields.Many2many(
        string="Allowed Utility Types",
        comodel_name="utility.type",
        relation="rel_multiplier_item_2_utility_type",
        column1="item_id",
        column2="type_id",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    note = fields.Text(
        string="Note",
    )
