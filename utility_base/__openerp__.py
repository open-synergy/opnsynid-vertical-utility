# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "Utility Management",
    "version": "8.0.1.2.0",
    "category": "Invoicing",
    "website": "https://simetri-sinergi.id",
    "author": "OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "base_sequence_configurator",
        "base_workflow_policy",
        "base_cancel_reason",
        "base_print_policy",
        "product",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/base_sequence_configurator_data.xml",
        "data/base_workflow_policy_data.xml",
        "data/base_cancel_reason_configurator_data.xml",
        "menu.xml",
        "wizards/utility_meter_reading_worksheet_start.xml",
        "wizards/utility_meter_reading_worksheet_end.xml",
        "views/utility_type_views.xml",
        "views/utility_meter_views.xml",
        "views/utility_meter_reading_views.xml",
        "views/utility_meter_reading_multiplier_item_views.xml",
        "views/utility_meter_reading_worksheet_template_views.xml",
        "views/utility_meter_reading_worksheet_views.xml",
    ],
}
