/** @odoo-module alias=lims_web_tour.lims_web_tour */

import publicWidget from 'web.public.widget';
import Dialog from 'web.Dialog';
import core from 'web.core';
import { _t } from 'web.core';

publicWidget.registry.limsWebTour = publicWidget.Widget.extend({
    selector: 'table.o_results_table',
    events: {
        'click .o_result_rework': '_onResultReworkClick',
    },

    //----------------------------------------------------------------------
    // Handlers
    //----------------------------------------------------------------------
    /**
     * @private
     * @param {Event} ev
     */
    _onResultReworkClick: function (ev) {
        var self = this;
        var $currentTarget = $(ev.currentTarget);
        new Dialog(this, {
            title: _t('Rework'),
            $content: '<div><input type="text" class="form-control o_input_reason" placeholder="Reason"/></div>',
            buttons: [
                {
                    text: _t('Send'),
                    classes: 'btn-primary',
                    close: false,
                    click: function () {
                        var reason = this.$el.find('input.o_input_reason').val();
                        if (reason) {
                            this.close();
                            self._rpc({
                                route: '/my/analysis/rework_result',
                                params: {
                                    'analysis_id': $currentTarget.data('analysisId'),
                                    'method_param_charac_id': $currentTarget.data('methodParamCharacId'),
                                    'reason': reason.toString(),
                                    'model': $currentTarget.data('model'),
                                },
                            }).then(function () {
                                window.location.reload();
                            });
                        }
                    },
                },
                {
                    text: _t('Cancel'),
                    close: true,
                },
            ],
        }).open();
    },
});