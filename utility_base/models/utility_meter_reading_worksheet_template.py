# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class UtilityMeterReadingWorksheetTemplate(models.Model):
    _name = "utility.meter_reading_worksheet_template"
    _description = "Meter Reading Worksheet Template"

    name = fields.Char(
        string="Template Name",
        required=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    note = fields.Text(
        string="Note",
    )
    meter_ids = fields.Many2many(
        string="Meter(s)",
        comodel_name="utility.meter",
        relation="rel_meter_reading_worksheet_temp_2_meter",
        column1="template_id",
        column2="meter_id",
    )
    worksheet_sequence_id = fields.Many2one(
        string="Worksheet Sequence",
        comodel_name="ir.sequence",
    )
    default_user_id = fields.Many2one(
        string="Default User",
        comodel_name="res.users",
    )
    estimate_work_hour = fields.Integer(
        string="Estimate Work Hours",
        default=0,
    )
    estimate_work_minute = fields.Integer(
        string="Estimate Work Minutes",
        default=0,
    )
    cron_id = fields.Many2one(
        string="Cron",
        comodel_name="ir.cron",
        readonly=True,
    )
    worksheet_confirm_grp_ids = fields.Many2many(
        string="Allow To Confirm Worksheet",
        comodel_name="res.groups",
        relation="rel_sheet_template_confirm_worksheet",
        column1="type_id",
        column2="group_id",
    )
    worksheet_approve_grp_ids = fields.Many2many(
        string="Allow To Approve Worksheet",
        comodel_name="res.groups",
        relation="rel_sheet_template_approve_worksheet",
        column1="type_id",
        column2="group_id",
    )
    worksheet_start_grp_ids = fields.Many2many(
        string="Allow To Confirm Worksheet",
        comodel_name="res.groups",
        relation="rel_sheet_template_start_worksheet",
        column1="type_id",
        column2="group_id",
    )
    worksheet_done_grp_ids = fields.Many2many(
        string="Allow To Finish Worksheet",
        comodel_name="res.groups",
        relation="rel_sheet_template_done_worksheet",
        column1="type_id",
        column2="group_id",
    )
    worksheet_cancel_grp_ids = fields.Many2many(
        string="Allow To Cancel Worksheet",
        comodel_name="res.groups",
        relation="rel_sheet_template_cancel_worksheet",
        column1="type_id",
        column2="group_id",
    )
    worksheet_restart_grp_ids = fields.Many2many(
        string="Allow To Restart Worksheet",
        comodel_name="res.groups",
        relation="rel_sheet_template_restart_worksheet",
        column1="type_id",
        column2="group_id",
    )

    @api.multi
    def action_generate_worksheet(self):
        for document in self:
            document._generate_worksheet()

    @api.model
    def cron_generate_worksheet(self, template_id):
        template = self.browse([template_id])[0]
        template._generate_worksheet()

    @api.multi
    def _generate_worksheet(self):
        self.ensure_one()
        obj_sheet = self.env["utility.meter_reading_worksheet"]
        data = {
            "template_id": self.id,
            "scheduled_date_start": fields.Datetime.now(),
        }
        temp_record = obj_sheet.new(data)
        temp_record.onchange_user_id()
        temp_record.onchange_schedule_date_end()
        values = temp_record._convert_to_write(temp_record._cache)
        obj_sheet.create(values)

    @api.multi
    def action_generate_cron(self):
        for document in self:
            document._generate_cron()

    @api.multi
    def _generate_cron(self):
        self.ensure_one()
        data = self._prepare_cron_data()
        obj_cron = self.env["ir.cron"]
        cron = obj_cron.create(data)
        self.write({"cron_id": cron.id})

    @api.multi
    def _prepare_cron_data(self):
        self.ensure_one()
        cron_name = "Generate Meter Utility Reading Worksheet: %s" % (
            self.name)
        return {
            "name": cron_name,
            "user_id": self.env.user.id,
            "active": False,
            "interval_number": 30,
            "interval_unit": "days",
            "numberofcall": -1,
            "doall": True,
            "model": "utility.meter_reading_worksheet_template",
            "function": "cron_generate_worksheet",
            "args": "(%s,)" % (self.id),
        }
