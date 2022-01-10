# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class UtilityMeterReadingWorksheetStart(models.TransientModel):
    _name = "utility.meter_reading_worksheet_start"
    _description = "Start Meter Reading Worksheet"

    @api.model
    def _default_date_start(self):
        return fields.Datetime.now()

    date_start = fields.Datetime(
        string="Date Start",
        required=True,
        default=lambda self: self._default_date_start(),
    )

    @api.multi
    def action_start(self):
        self.ensure_one()
        worksheet_ids = self.env.context.get("active_ids", [])
        obj_worksheet = self.env["utility.meter_reading_worksheet"]
        for worksheet in obj_worksheet.browse(worksheet_ids):
            worksheet.action_start(self.date_start)
