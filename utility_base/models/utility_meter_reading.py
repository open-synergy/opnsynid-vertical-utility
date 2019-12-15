# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
from pytz import timezone


class UtilityMeterReading(models.Model):
    _name = "utility.meter_reading"
    _description = "Utility Meter Reading"
    _order = "date_reading, id"
    _inherit = [
        "mail.thread",
        "base.sequence_document",
    ]

    @api.multi
    @api.depends(
        "date_reading",
        "state",
    )
    def _compute_previous_reading_id(self):
        for document in self:
            document.previous_reading_id = False
            if document.date_reading:
                prev_reading = document._get_previous_reading()
                document.previous_reading_id = prev_reading and \
                    prev_reading.id or False

    @api.multi
    @api.depends(
        "meter_id",
        "date_reading",
    )
    def _compute_date_reading_tz(self):
        for document in self:
            document.date_reading_tz = False
            if document.meter_id and document.date_reading:
                tz = document._get_tz()
                date_reading = datetime.strptime(
                    document.date_reading, "%Y-%m-%d %H:%M:%S")
                date_reading = timezone("UTC").localize(date_reading)
                date_reading = date_reading.astimezone(timezone(tz))
                # TODO: Not sure this is the right syntax
                date_reading = date_reading.replace(tzinfo=None)
                document.date_reading_tz = date_reading.strftime(
                    "%Y-%m-%d %H:%M:%S")

    @api.multi
    @api.depends(
        "previous_reading_id",
        "amount_reading",
        "state",
    )
    def _compute_amount_usage(self):
        for document in self:
            document.amount_usage = 0.0
            if document.previous_reading_id:
                prev_reading = document.previous_reading_id
                document.amount_usage = document.amount_reading - \
                    prev_reading.amount_reading

    @api.multi
    @api.depends(
        "meter_id",
    )
    def _compute_uom_id(self):
        for document in self:
            document.uom_id = False
            if document.meter_id:
                document.uom_id = document.meter_id.uom_id.id

    @api.multi
    @api.depends(
        "amount_reading",
        "multiplier_ids",
        "multiplier_ids.multiplier",
    )
    def _compute_amount_reading_multiplier(self):
        for document in self:
            amount_reading_multiplier = document.amount_reading
            for multiplier in document.multiplier_ids:
                amount_reading_multiplier *= multiplier.multiplier
            document.amount_reading_multiplier = amount_reading_multiplier

    @api.multi
    @api.depends(
        "amount_usage",
        "multiplier_ids",
        "multiplier_ids.multiplier",
    )
    def _compute_amount_usage_multiplier(self):
        for document in self:
            amount_usage_multiplier = document.amount_usage
            for multiplier in document.multiplier_ids:
                amount_usage_multiplier *= multiplier.multiplier
            document.amount_usage_multiplier = amount_usage_multiplier

    name = fields.Char(
        string="# Reading",
        required=True,
        default="/",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    previous_reading_id = fields.Many2one(
        string="# Previous Reading",
        comodel_name="utility.meter_reading",
        compute="_compute_previous_reading_id",
        store=True,
    )
    meter_id = fields.Many2one(
        string="# Meter",
        comodel_name="utility.meter",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    worksheet_id = fields.Many2one(
        string="# Worksheet",
        comodel_name="utility.meter_reading_worksheet",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    date_reading = fields.Datetime(
        string="Date",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    date_reading_tz = fields.Datetime(
        string="Date According Meter Timezone",
        compute="_compute_date_reading_tz",
        store=True,
    )
    amount_reading = fields.Float(
        string="Value",
        required=True,
        default=0.0,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    amount_usage = fields.Float(
        string="Usage",
        compute="_compute_amount_usage",
        store=True,
    )
    uom_id = fields.Many2one(
        string="UoM",
        comodel_name="product.uom",
        compute="_compute_uom_id",
        store=True,
    )
    multiplier_ids = fields.One2many(
        strng="Multiplier",
        comodel_name="utility.meter_reading_multiplier",
        inverse_name="meter_reading_id",
        readonly=True,
    )
    amount_reading_multiplier = fields.Float(
        string="Amount Reading After Multiply",
        compute="_compute_amount_reading_multiplier",
        store=True,
    )
    amount_usage_multiplier = fields.Float(
        string="Amount Usage After Multiply",
        compute="_compute_amount_usage_multiplier",
        store=True,
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("valid", "Valid"),
        ],
        default="draft",
        required=True,
        readonly=True,
    )

    @api.multi
    def action_valid(self):
        for document in self:
            document._compute_previous_reading_id()
            document.write(document._prepare_valid_data())
            document._generate_multipliers()

    @api.multi
    def action_draft(self):
        for document in self:
            document.write(document._prepare_draft_data())
            document.multiplier_ids.unlink()

    @api.multi
    def action_recompute(self):
        for document in self:
            document._compute_previous_reading_id()

    @api.multi
    def _prepare_valid_data(self):
        self.ensure_one()
        return {
            "state": "valid",
        }

    @api.multi
    def _prepare_draft_data(self):
        self.ensure_one()
        return {
            "state": "draft",
        }

    @api.multi
    def _get_previous_reading(self):
        self.ensure_one()
        result = False
        obj_reading = self.env["utility.meter_reading"]
        criteria = self._prepare_previous_reading_domain()
        results = obj_reading.search(criteria, order="date_reading desc")
        if len(results) > 0:
            result = results[0]
        return result

    @api.multi
    def _prepare_previous_reading_domain(self):
        self.ensure_one()
        return [
            ("meter_id", "=", self.meter_id.id),
            ("date_reading", "<", self.date_reading),
            ("state", "=", "valid"),
        ]

    @api.model
    def create(self, values):
        _super = super(UtilityMeterReading, self)
        result = _super.create(values)
        sequence = result._create_sequence()
        result.write({
            "name": sequence,
        })
        return result

    @api.constrains(
        "date_reading",
    )
    def _check_no_duplicate(self):
        obj_reading = self.env["utility.meter_reading"]
        for document in self:
            if document.date_reading:
                criteria = document._prepare_check_no_duplicate_domain()
                readings = obj_reading.search(criteria)
                if len(readings) > 0:
                    error_msg = _("No duplicate entry allowed")
                    raise UserError(error_msg)

    @api.multi
    def _prepare_check_no_duplicate_domain(self):
        self.ensure_one()
        return [
            ("date_reading", "=", self.date_reading),
            ("id", "=", self.id),
            ("meter_id", "!=", self.meter_id.id),
        ]

    @api.multi
    def _get_tz(self):
        self.ensure_one()
        if self.meter_id.tz:
            return self.meter_id.tz
        else:
            return self.env.user.company_id.partner_id.tz

    @api.multi
    def _generate_multipliers(self):
        self.ensure_one()
        result = []
        for multiplier in self.meter_id.multiplier_ids:
            result.append(multiplier._generate_multiplier())
        self.write({
            "multiplier_ids": result,
        })
