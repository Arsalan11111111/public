/** @odoo-module */

import {registry} from "@web/core/registry";
import {View} from "@web/views/view";
import {Dialog} from "@web/core/dialog/dialog";
import {useService} from "@web/core/utils/hooks";
import {_t, qweb} from 'web.core';
import {usePopover} from "@web/core/popover/popover_hook";
import {AlertDialog} from "@web/core/confirmation_dialog/confirmation_dialog";

jQuery.expr[':'].contains = function (a, i, m) {
    return jQuery(a).text().toUpperCase().indexOf(m[3].toUpperCase()) >= 0;
};

const {Component, useState, useRef, onMounted} = owl;

/**
 * Getting Parameter Helper Dialog by its ID
 * @returns jQueryElement
 */
function getParamHelperDialog() {
    return $('div#param_helper_main');
}

/**
 * This class is used to handle the Lims Parameter Helper modal
 */
class LimsParameterHelperDialog extends Component {
    async setup() {
        super.setup();
        this.popover = usePopover();
        this.helperData = this.props.data;
        this.helperFromId = this.props.helperFromId;
        this.helperFromModel = this.props.helperFromModel;
        this.model = this.props.searchModel.resModel;
        this.modelId = this.props.data.id;
        this.analysisId = this.props.analysisId;
        this.parameterPacks = this.props.parameterPacks;
        this.searchInputPlaceholder = _t('What are you looking for ?')
        this.searchInputParamPlaceholder = _t('What parameter are you looking for ?'),
        this.searchInputPackPlaceholder = _t('What pack are you looking for ?'),
        this.parameterPacks.current_results = _.groupBy(this.parameterPacks.current_results, function (res) {
            return res.method;
        });
        this.state = useState({});
        this.rpc = useService('rpc');
        onMounted(() => {
            this._initDialog();
        });
    }

    // ------------------------------------------------------------
    // Private
    // ------------------------------------------------------------

    _initDialog() {
        var $dialog = getParamHelperDialog();
        this.$dialog = $dialog;
        _.each(this.parameterPacks.current_results, function (result) {
            _.each(result, function (res) {
                var $input = $dialog.find('input[data-param-id="%i"]'
                    .replace('%i', res.id));
                $input.attr('disabled', true).attr('checked', true);
                $input.closest('li').toggleClass('text-secondary');
            })
        });
        _.each(this.parameterPacks.owned_packs, function (ownedPack) {
            var $input = $dialog.find('input.o_checkbox_pack[data-pack-id="%i"]'
                .replace('%i', ownedPack.id));
            var $children = $dialog.find('div[id="accordion_%i"]'
                .replace('%i', ownedPack.id));
            $input.attr('disabled', true).attr('checked', true)
                .addClass('o_current_result');
            $input.siblings('span').addClass('font-italic text-secondary');
            $children.find('input.o_checkbox_param')
                .attr('disabled', true).attr('checked', true)
                .addClass('o_current_result')
                .siblings('span').addClass('font-italic');
        });
    }

    _refreshSummary() {
        var self = this;
        var checkedPacks = this.$dialog.find('.o_checkbox_pack:checked:not(.o_current_result)');
        var checkedParams = this.$dialog.find('.o_checkbox_param:checked:not(.o_current_result,:disabled)');
        var paramIds = [];
        var $selectionPacks = this.$dialog.find('.o_selection_packs');
        var $selectionParams = this.$dialog.find('.o_selection_params');
        var $selectedPacks = this.$dialog.find('.o_selected_packs');
        var $selectedParams = this.$dialog.find('.o_selected_params');
        $selectedPacks.empty();
        $selectedParams.empty();
        _.each(checkedPacks, function (pack) {
            var $pack = $(pack);
            self.$dialog.find('.o_selected_packs').append(
                $(qweb.render('lims_base.parameters_helper.modal_content.badge', {
                    name: $pack.data('displayName'),
                    id: $pack.data('packId'),
                    class: 'text-bg-primary o_badge',
                    type: 'pack',
                })).on('click', function (ev) {
                    self._onBadgeClick(ev);
                })
            );
        });
        _.each(checkedParams, function (param) {
            var $param = $(param);
            if (!paramIds.includes($param.data('paramId'))) {
                self.$dialog.find('.o_selected_params').append(
                    $(qweb.render('lims_base.parameters_helper.modal_content.badge', {
                        name: $param.data('name'),
                        id: $param.data('paramId'),
                        class: 'text-bg-secondary o_badge',
                        type: 'param',
                    })).on('click', function (ev) {
                        self._onBadgeClick(ev);
                    })
                );
            }
            paramIds.push($param.data('paramId'));
        });
        this.$dialog.find('.o_empty_selection')
            .toggleClass('d-none', (checkedPacks.length + checkedParams.length) > 0);
        $selectionPacks.toggleClass('d-none', !checkedPacks.length);
        $selectionParams.toggleClass('d-none', !checkedParams.length);
    }

    _toggleAccordionCollapse(ev) {
        var $currentTarget = $(ev.currentTarget);
        var $accordion = $currentTarget.closest('div.accordion-item');
        $accordion.find('.accordion-collapse').toggleClass('show');
    }

    _adaptCardTotals() {
        var $cards = this.$dialog.find('span.o_total_calculated').closest('div.accordion-item');
        var main = 'input.o_search_input';
        var anyValueLength = this.$dialog.find(main + '[data-filter="all"]').val().length ||
            this.$dialog.find(main + '[data-filter="pack"]').val().length ||
            this.$dialog.find(main + '[data-filter="param"]').val().length;
        this.$dialog.find('div.o_total_calculated').toggleClass(
            'd-none', !anyValueLength);
        _.each($cards, function (card) {
            var $card = $(card);
            $card.find('span.o_total_calculated').text(
                $card.find('li.list-group-item:not(.d-none)').length);
        });
    }

    // ------------------------------------------------------------
    // Handlers
    // ------------------------------------------------------------

    _onFocusSummaryParam(ev) {
        $(ev.target).popover();
    }

    _onCheckboxPackClick(ev) {
        var $currentTarget = $(ev.currentTarget);
        var $accordion = $currentTarget.closest('div.accordion-item');
        $accordion.find('.o_checkbox_param:not(.o_current_result)')
            .prop('checked', $currentTarget.is(':checked'))
            .prop('disabled', $currentTarget.is(':checked'));
        this._refreshSummary();
    }

    _onCheckboxParamClick() {
        this._refreshSummary();
    }

    _onPackNameClick (ev) {
        this._toggleAccordionCollapse(ev);
    }

    _onBadgeParamsClick (ev) {
        this._toggleAccordionCollapse(ev);
    }

    _onBadgeClick (ev) {
        var $currentTarget = $(ev.currentTarget);
        var id = $currentTarget.data('id');
        var type = $currentTarget.data('type');
        var selector;
        if (type === 'pack') {
            selector = '.o_checkbox_pack[data-pack-id="%i"],.o_checkbox_param[data-pack-id="%i"]';
        } else if (type === 'param') {
            selector = '.o_checkbox_param[data-param-id="%i"]';
        }
        this.$dialog.find(selector.replace('%i', id).replace('%i', id))
            .prop('checked', false).prop('disabled', false);
        this._refreshSummary();
    }

    _onSearchInputKeyup (ev) {
        var $currentTarget = $(ev.currentTarget);
        var value = $currentTarget.val();
        var filter = $currentTarget.data('filter');
        var $uselessParams = this.$dialog.find(
            'span.o_param_name:not(:contains("%i"))'.replace('%i', value));

        /* PACKS+PARAMS LOGIC */
        // Init state
        this.$dialog.find('div.accordion').find('div.card-body').removeClass('d-none');
        this.$dialog.find('span.o_param_name').closest('li').removeClass('d-none');
        this.$dialog.find('div.o_empty_advanced_results').removeClass('d-block');
        // Processing
        if (filter === 'param' || filter === 'all') {
            _.each($uselessParams, function (uselessParam) {
                var $uselessParam = $(uselessParam);
                $uselessParam.closest('li').addClass('d-none');
            });
        }
        _.each(this.$dialog.find('span.o_pack_name'), function (pack) {
            var $pack = $(pack);
            var $card = $pack.closest('div.accordion-item');
            var $cardBody = $card.find('div.accordion-collapse');
            var shownItems = $cardBody.find('li:not(.d-none)').length;
            if (filter === 'all') {
                $cardBody.toggleClass('d-none', !shownItems);
                $card.toggleClass('d-none',
                    !shownItems && !$pack.is(':contains("%i")'.replace('%i', value)));
            }
            if (filter === 'pack') {
                $card.toggleClass('d-none', !$pack.is(':contains("%i")'.replace('%i', value)));
            }
            if (filter === 'param') {
                $card.find('div.o_empty_advanced_results').toggleClass('d-block', !shownItems);
            }
        });
        if (filter === 'param' || filter === 'all') {
            // Force to show all params contained in a pack
            var $packsFound = this.$dialog.find('span.o_pack_name:contains("%i")'.replace('%i', value));
            _.each($packsFound, function (pack) {
                var $packCardBody = $(pack).closest('div.accordion-item').find('div.accordion-collapse');
                $packCardBody.removeClass('d-none');
                $packCardBody.find('li').removeClass('d-none');
            });
        }

        /* ORPHAN PARAMS LOGIC */
        // Init state
        if (filter === 'param' || filter === 'all') {
            this.$dialog.find('tr.o_param_without_pack').removeClass('d-none');
            // Adapting params without packs
            var $paramsWithoutPacks = this.$dialog.find('tr.o_param_without_pack');
            _.each($paramsWithoutPacks, function (tr) {
                var $tr = $(tr);
                var isFound = $tr.find('span.o_param_name:contains("%i")'.replace('%i', value)).length;
                $tr.toggleClass('d-none', !isFound);
            });
        }
        // Adapting inputs according input context
        if (filter === 'pack') {
            this.$dialog.find('input.o_search_input[data-filter="param"]').val('').trigger('keyup');
        }
        this._adaptCardTotals();
    }

    _onSelectAllClick(ev) {
        var $currentTarget = $(ev.currentTarget);
        var type = $currentTarget.data('type');
        var isSelectAll = $currentTarget.is(':checked');
        var selector;
        var base;
        switch (type) {
            case 'packs':
                this.$dialog.find('input.o_checkbox_pack').click();
                base = 'div.card:not(.d-none)';
                if (isSelectAll) {
                    selector = 'input.o_checkbox_pack:not(:checked)';
                } else {
                    selector = 'input.o_checkbox_pack:checked';
                }
                this.$dialog.find(base).find(
                    'input.o_checkbox_param:not(.o_param_without_pack):not(:disabled)')
                    .prop('checked', isSelectAll);
                break;
            case 'params':
                this.$dialog.find('input.o_param_without_pack:not(:disabled)').click();
                base = 'tr.o_param_without_pack:not(.d-none)';
                if (isSelectAll) {
                    selector = 'input.o_param_without_pack:not(:checked):not(:disabled)';
                } else {
                    selector = 'input.o_param_without_pack:checked:not(:disabled)';
                }
                break;
        }
        this.$dialog.find(base).find(selector).prop('checked', isSelectAll);
        this._refreshSummary();
    }

    _onSearchSwitchClick(ev) {
        var $simple = this.$dialog.find('div.input-group[data-search="simple"]');
        var $advanced = this.$dialog.find('div.input-group[data-search="advanced"]');
        var inputSelector = 'input.o_search_input';
        if (!$simple.hasClass('d-none')) {
            $($advanced[0]).find(inputSelector).val($simple.find(inputSelector).val()).trigger('keyup');
            $($advanced[1]).find(inputSelector).val('').trigger('keyup');
        } else {
            $simple.find(inputSelector).val($($advanced[0]).find(inputSelector).val()).trigger('keyup');
        }
        $simple.toggleClass('d-none');
        $advanced.toggleClass('d-none');
    }

    _onCreateDialogBtnClick() {
        var self = this;
        var limsDatas = {};
        _.each(this.$dialog.find('.o_lims_data:checked:not(:disabled)'), function (limsData) {
            var limsData = $(limsData)
            if (!limsDatas[limsData.data('limsType')]) {
                limsDatas[limsData.data('limsType')] = [];
            }
            limsDatas[limsData.data('limsType')].push(limsData.data('limsId'));
        });
        var results = {
            // Get data from the active model and active id.
            model: this.model,
            model_id: this.helperData.id,
            // Get the specific id and model where button is placed.
            helperFromModel: this.helperFromModel,
            helperFromId: this.helperFromId,
            // Get the linked analysis if exists.
            analysis_id: this.$dialog.find('.o_analysis').data('id'),
            regulation_id: this.$dialog.find('.o_regulation').data('id'),
            // Get all element marked by 't-att-data-lims-type=STR' and 't-att-data-lims-id=INT'
            lims_datas: limsDatas,
        };
        this.rpc(
            '/web/parameters_helper/create_results',
            {
                results: results,
            },
        ).then(function () {
            window.location.reload();
        });
    }

    _onCloseDialogBtnClick() {
        this.props.close();
    }
}

LimsParameterHelperDialog.components = {Dialog};
LimsParameterHelperDialog.template = 'lims_base.LimsParameterHelperDialog';

/**
 * This class is used to handle the Widget button
 */
class LimsParameterHelper extends Component {
    setup() {
        super.setup();
        this.dialog = useService('dialog');
        this.data = this.env.model.root.data;
        this.model = this.env.model.root.resModel;
        this.modelId = this.data.id;
        this.helperFromModel = this.props.helperFromModel;
        this.helperFromId = this.props.helperFromId;
        this.analysisId = this.props.analysisId;
        this.searchModel = this.env.model.env.searchModel;

        this.orm = this.env.model.orm;
        this.rpc = useService('rpc');
    }

    // ------------------------------------------------------------
    // Private
    // ------------------------------------------------------------

    async _onButtonClick() {
        if ((this.data.matrix_id || this.props.record.data.matrix_id || this.props.record.data.rel_matrix_id) && (this.modelId || this.helperFromModel)) {
            this.parameterPacks = await this._getParameterPacks();
            if(this.model==this.props.record.resModel){
               this.analysisId = this.modelId;
            }else if(this.props.record.data.analysis_id){
               this.analysisId = this.props.record.data.analysis_id[0]
            }
            this.dialog.add(LimsParameterHelperDialog, {
                searchModel: this.searchModel,
                data: this.data,
                model : this.model,
                modelId : this.modelId,
                helperFromId: this.props.record.data.id,
                helperFromModel: this.props.record.resModel,
                analysisId: this.analysisId,
                orm: this.orm,
                parameterPacks: this.parameterPacks,
            });
        } else {
            this.dialog.add(AlertDialog, {
                title: _t("Configuration error"),
                body: _t("Try to save element before launch the wizard\nCheck that all mandatory datas are set"),
                confirmLabel: _t('Ok'),
            });
        }
    }

    async _getParameterPacks() {
        var res = {}
        var matrixId;
        var model = this.model;
        var modelId = this.modelId;
        var helperFromId = this.props.record.data.id;
        var helperFromModel = this.props.record.resModel;
        var analysisId = null;
        if (helperFromModel == model){
            analysisId = this.modelId;
        } else if (this.props.record.data.analysis_id){
            analysisId = this.props.record.data.analysis_id[0];
        }
        if (this.props.record.data.rel_matrix_id){
            matrixId = this.props.record.data.rel_matrix_id[0];
        } else if (this.props.record.data.matrix_id){
            matrixId = this.props.record.data.matrix_id[0];
        } else if (this.data.matrix_id){
            matrixId = this.data.matrix_id[0];
        } else {
            this.dialog.add(AlertDialog, {
                title: _t("Configuration error"),
                body: _t("Try to save element before launch the wizard\nCheck that all mandatory datas are set"),
                confirmLabel: _t('Ok'),
            });
        }
        res = await this.rpc(
            '/web/parameters_helper/get_parameter_packs',
            {
                model: model,
                model_id: modelId,
                helper_from_model: helperFromModel,
                helper_from_id: helperFromId,
                matrix_id: matrixId,
                analysis_id: analysisId,
            },
        );
        return res;
    }
}

LimsParameterHelper.template = 'lims_base.LimsParameterHelper';
LimsParameterHelper.components = {View};

registry.category('view_widgets').add('lims_parameter_helper', LimsParameterHelper);

return {
    LimsParameterHelper: LimsParameterHelper,
    LimsParameterHelperDialog: LimsParameterHelperDialog,
};
