# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class UtilityMeter(models.Model):
    _name = "utility.meter"
    _description = "Utility Meter"

    @api.multi
    @api.depends(
        ("type_id")
    )
    def _compute_allowed_uom_ids(self):
        for document in self:
            document.allowed_uom_ids = document.type_id.allowed_uom_ids

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

    @api.onchange(
        "type_id",
    )
    def onchange_uom_id(self):
        self.uom_id = False
