# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
from openerp.addons.base.res.res_partner import _tz_get


class UtilityMeter(models.Model):
    _name = "utility.meter"
    _description = "Utility Meter"

    @api.multi
    @api.depends(
        "type_id",
    )
    def _compute_allowed_uom_ids(self):
        for document in self:
            document.allowed_uom_ids = document.type_id.allowed_uom_ids

    @api.multi
    @api.depends(
        "type_id",
    )
    def _compute_allowed_multiplier_item_ids(self):
        for document in self:
            result = []
        if document.type_id:
            for multiplier in self.type_id.multiplier_ids:
                result.append(multiplier.item_id.id)
        document.allowed_multiplier_item_ids = result

    name = fields.Char(
        string="# Meter",
        required=True,
    )
    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
    )
    type_id = fields.Many2one(
        string="Type",
        comodel_name="utility.type",
        required=True,
    )
    tz = fields.Selection(
        string="Timezone",
        selection=_tz_get,
    )
    allowed_uom_ids = fields.Many2many(
        string="Allowed UoM(s)",
        comodel_name="product.uom",
        compute="_compute_allowed_uom_ids",
        store=False,
    )
    uom_id = fields.Many2one(
        string="UoM",
        comodel_name="product.uom",
        required=True,
    )
    meter_reading_sequence_id = fields.Many2one(
        string="Meter Reading Sequence",
        comodel_name="ir.sequence",
        domain=[
            ("code", "=", "meter.reading"),
        ],
    )
    allowed_multiplier_item_ids = fields.Many2many(
        string="Allowed Multipliers",
        comodel_name="utility.meter_reading_multiplier_item",
        compute="_compute_allowed_multiplier_item_ids",
        store=False,
    )
    multiplier_ids = fields.One2many(
        string="Multipliers",
        comodel_name="utility.meter_multiplier",
        inverse_name="meter_id",
    )

    @api.onchange(
        "type_id",
    )
    def onchange_uom_id(self):
        self.uom_id = False
