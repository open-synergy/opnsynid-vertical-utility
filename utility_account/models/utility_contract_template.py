# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class UtilityContractTemplate(models.Model):
    _name = "utility.contract_template"
    _description = "Utility Contract Template"

    name = fields.Char(
        string="Template",
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
    contract_sequence_id = fields.Many2one(
        string="Contract Sequence",
        comodel_name="ir.sequence",
        company_dependent=True,
    )
    contract_confirm_grp_ids = fields.Many2many(
        string="Allow To Confirm Contract",
        comodel_name="res.groups",
        relation="rel_contract_template_confirm_contract",
        column1="template_id",
        column2="group_id",
    )
    contract_approve_grp_ids = fields.Many2many(
        string="Allow To Approve Contract",
        comodel_name="res.groups",
        relation="rel_contract_template_approve_contract",
        column1="template_id",
        column2="group_id",
    )
    contract_start_grp_ids = fields.Many2many(
        string="Allow To Confirm Contract",
        comodel_name="res.groups",
        relation="rel_contract_template_start_contract",
        column1="template_id",
        column2="group_id",
    )
    contract_done_grp_ids = fields.Many2many(
        string="Allow To Finish Contract",
        comodel_name="res.groups",
        relation="rel_contract_template_done_contract",
        column1="template_id",
        column2="group_id",
    )
    contract_cancel_grp_ids = fields.Many2many(
        string="Allow To Cancel Contract",
        comodel_name="res.groups",
        relation="rel_contract_template_cancel_contract",
        column1="template_id",
        column2="group_id",
    )
    contract_terminate_grp_ids = fields.Many2many(
        string="Allow To Terminate Contract",
        comodel_name="res.groups",
        relation="rel_contract_template_terminate_contract",
        column1="template_id",
        column2="group_id",
    )
    contract_restart_grp_ids = fields.Many2many(
        string="Allow To Restart Contract",
        comodel_name="res.groups",
        relation="rel_contract_template_restart_contract",
        column1="template_id",
        column2="group_id",
    )
    note = fields.Text(
        string="Note",
    )
