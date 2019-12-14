# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class UtilityMeterReading(models.Model):
    _name = "utility.meter_reading"
    _inherit = "utility.meter_reading"

    schedule_id = fields.Many2one(
        string="Invoice Schedule",
        comodel_name="utility.contract_invoice_schedule",
        ondelete="set null",
    )
