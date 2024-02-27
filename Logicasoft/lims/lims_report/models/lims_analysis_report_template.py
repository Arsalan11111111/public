from odoo import fields, models, api


class LimsAnalysisReportTemplate(models.Model):
    _name = 'lims.analysis.report.template'
    _description = 'Lims report model'
    _order = 'sequence, id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def get_default_option_ids(self):
        return self.get_all_options_for_lims_report()

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True, tracking=True)
    laboratory_id = fields.Many2one('lims.laboratory', tracking=True,
                                    help='If filled, only this laboratory will be able to select this template.')
    report_id = fields.Many2one('ir.actions.report', domain=[('model', '=', 'lims.analysis.report')], tracking=True,
                                required=True)
    option_ids = fields.Many2many('ir.model.fields', domain=[('model_id', '=', 'lims.analysis.report'),
                                                             ('ttype', '=', 'boolean'),
                                                             ('name', '=like', 'option_%')],
                                  default=get_default_option_ids,
                                  help="Select the printing options to already checked for the report that will be "
                                       "created.")

    def get_all_options_for_lims_report(self):
        """
        Get all field named with this structure =begin with 'option_' and his format is boolean

        :return:
        """
        return self.env['ir.model.fields'].search([('model_id', '=', 'lims.analysis.report'),
                                                             ('ttype', '=', 'boolean'),
                                                             ('name', '=like', 'option_%')])

    def get_dict_for_selected_options(self, selected_options=False, dictionary_options=None):
        """
        Convert selected options, into a dictionary
        with option selected : True, option unselected : False,
        To bypass the default arg in model.

        :param selected_options:
        :param dictionary_options:
        :return:
        """
        if dictionary_options is None:
            dictionary_options = {}
        if not selected_options:
            return dictionary_options
        possible_options = self.get_all_options_for_lims_report()
        for option in possible_options:
            if option in selected_options:
                dictionary_options.update({option.name: True})
            else:
                dictionary_options.update({option.name: False})
        return dictionary_options
