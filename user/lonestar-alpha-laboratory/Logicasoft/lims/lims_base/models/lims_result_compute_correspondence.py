
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
from odoo import models, fields


class LimsResultComputeCorrespondence(models.Model):
    _name = 'lims.result.compute.correspondence'
    _description = 'Correspondences of computed result'

    method_param_charac_id = fields.Many2one('lims.method.parameter.characteristic', 'Parameter Characteristic')
    correspondence = fields.Char()
    use_function = fields.Boolean()
    is_optional = fields.Boolean()
    compute_result_id = fields.Many2one('lims.analysis.compute.result', 'Compute result', ondelete='cascade')

    def get_correspondence_dictionary(self, dictionary=None):
        self.ensure_one()
        if dictionary is None:
            dictionary = {}
        dictionary.update({
            'method_param_charac_id': self.method_param_charac_id.id,
            'correspondence': self.correspondence,
            'use_function': self.use_function,
            'is_optional': self.is_optional,
        })
        return dictionary

