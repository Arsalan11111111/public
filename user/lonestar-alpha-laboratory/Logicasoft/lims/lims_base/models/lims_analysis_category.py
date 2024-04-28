# -*- coding: utf-8 -*-

##############################################################################
#
#    Odoo Proprietary License v1.0
#
#    Copyright (c) 2013 LogicaSoft SPRL (<http://www.logicasoft.eu>).
#
#    This software and associated files (the "Software") may only be used (executed,
#    modified, executed after modifications) if you have purchased a valid license
#    from the authors, typically via Odoo Apps, or if you have received a written
#    agreement from the authors of the Software.
#
#    You may develop Odoo modules that use the Software as a library (typically
#    by depending on it, importing it and using its resources), but without copying
#    any source code or material from the Software. You may distribute those
#    modules under the license of your choice, provided that this license is
#    compatible with the terms of the Odoo Proprietary License (For example:
#    LGPL, MIT, or proprietary licenses similar to this one).
#
#    It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#    or modified copies of the Software.
#
#    The above copyright notice and this permission notice must be included in all
#    copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
##############################################################################
from odoo import fields, models, api, _
import json
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from babel.dates import format_date


class LimsAnalysisCategory(models.Model):
    _name = 'lims.analysis.category'
    _description = 'Analysis Category'
    _order = 'sequence, id'

    name = fields.Char('Name', required=True, translate=True)
    description = fields.Text()
    active = fields.Boolean(default=True)
    sequence = fields.Integer(string="Sequence")

    kanban_dashboard = fields.Text(compute='compute_kanban_dashboard')
    kanban_dashboard_graph = fields.Text(compute='compute_kanban_dashboard_graph')

    def compute_kanban_dashboard(self):
        for record in self:
            record.kanban_dashboard = json.dumps(record.get_analysis_dashboard_datas())

    def compute_kanban_dashboard_graph(self):
        for record in self:
            record.kanban_dashboard_graph = json.dumps(record.get_bar_graph_datas())

    def get_analysis_dashboard_datas(self):
        analysis_obj = self.env['lims.analysis']
        nb_analysis_conform = analysis_obj.search_count([('state', '=', 'conform'), ('category_id', '=', self.id)])
        nb_analysis_notconform = analysis_obj.search_count(
            [('state', '=', 'not_conform'), ('category_id', '=', self.id)])
        sorted_analysis = {
            'nb_analysis_conform': nb_analysis_conform,
            'nb_analysis_not_conform': nb_analysis_notconform
        }
        stages = self.env['lims.analysis.stage'].get_analysis_stage_type()
        for stage, _ in stages:
            nb_analysis_by_stage = analysis_obj.search_count([('rel_type', '=', stage), ('category_id', '=', self.id)])
            sorted_analysis.update({'nb_analysis_' + stage: nb_analysis_by_stage})
        return sorted_analysis

    def get_bar_graph_datas(self):
        data = []
        today = fields.Date.context_today(self)
        data.append({'label': _('Past'), 'value': 0.0, 'type': 'past'})
        locale = self._context.get('lang', 'en_US') or 'en_US'
        day_of_week = int(format_date(today, 'e', locale=locale))
        first_day_of_week = today + timedelta(days=-day_of_week + 1)
        for i in range(-1, 4):
            if i == 0:
                label = _('This Week')
            elif i == 3:
                label = _('Future')
            else:
                start_week = first_day_of_week + timedelta(days=i * 7)
                end_week = start_week + timedelta(days=6)
                if start_week.month == end_week.month:
                    label = str(start_week.day) + '-' + str(end_week.day) + ' ' + \
                            format_date(end_week, 'MMM', locale=locale)
                else:
                    label = format_date(start_week, 'd MMM',
                                        locale=locale) + '-' + \
                            format_date(end_week, 'd MMM', locale=locale)
            data.append({'label': label, 'value': 0.0, 'type': 'past' if i < 0 else 'future'})

        # Build SQL query to find amount aggregated by week
        select_sql_clause = """SELECT count(id) as total, min(date_plan) as aggr_date from lims_analysis where
            category_id = %(category_id)s"""
        query = ''
        start_date = (first_day_of_week + timedelta(days=-7))
        for i in range(0, 6):
            if i == 0:
                query += "(" + select_sql_clause + " and date_plan < '" + \
                         start_date.strftime(DEFAULT_SERVER_DATE_FORMAT) + "')"
            elif i == 5:
                query += " UNION ALL (" + select_sql_clause + " and date_plan >= '" + \
                         start_date.strftime(DEFAULT_SERVER_DATE_FORMAT) + "')"
            else:
                next_date = start_date + timedelta(days=7)
                query += " UNION ALL (" + select_sql_clause + " and date_plan >= '" + start_date.strftime(
                    DEFAULT_SERVER_DATE_FORMAT) + "' and date_plan < '" + \
                         next_date.strftime(DEFAULT_SERVER_DATE_FORMAT) + "')"
                start_date = next_date

        self.env.cr.execute(query, {'category_id': self.id})
        query_results = self.env.cr.dictfetchall()
        for index in range(0, len(query_results)):
            if query_results[index].get('aggr_date'):
                data[index]['value'] = query_results[index].get('total')

        return [{'values': data}]

    def action_create_new(self):
        ctx = self.env.context.copy()
        ctx.update({
            'default_category_id': self.id,
        })
        return {
            'name': _('Create analysis'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'lims.analysis',
            'context': ctx,
        }

    def open_action(self):
        ctx = self.env.context.copy()
        ctx.update({
            'search_default_category_id': self.id,
        })
        return {
            'name': _('Analysis'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form,pivot,graph,calendar',
            'res_model': 'lims.analysis',
            'context': ctx,
        }
