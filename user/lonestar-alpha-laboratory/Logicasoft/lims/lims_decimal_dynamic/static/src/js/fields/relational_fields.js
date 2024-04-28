odoo.define('lims_decimal_dynamic.relational_fields', function (require) {
"use strict";

var core = require('web.core');
var _lt = core._lt;
var AbstractField = require('web.AbstractField');
var FieldUtils = require('web.field_utils');

var FieldFloatDynamic = AbstractField.extend({
    description: _lt('Float Dynamic'),
    tag_template: 'FieldFloatDynamic',
    className: 'o_field_float_dynamic',
    supportedFieldTypes: ['float_dynamic'],
    events: _.extend({}, AbstractField.prototype.events, {
        'click': '_onClick',
        'change': '_onChange',
    }),
    limit: 1000,

    /**
     * @constructor
     */
    init: function () {
        this._super.apply(this, arguments);
        if (this.nodeOptions.dynamic_digits_field.includes('.')) {
            // This is probably a Many2one and it will be processed later
            this.digits = undefined;
        } else {
            this.digits = this.recordData[this.nodeOptions.dynamic_digits_field];
        }
        this.value = this.recordData[this.name];
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @override
     * @returns {jQuery}
     */
    getFocusableElement: function () {
        return this.mode === 'edit' && this.$input || this.$el;
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _finalRender: function (digits) {
        var options = {};
        if (!_.isUndefined(digits) && !_.isUndefined(this.value) && Math.sign(digits) !== -1) {
            options.digits = [0, digits];
        }
        this.$el.text(FieldUtils.format.float(this.value, {}, options));
    },
    /**
     * @private
     */
    _renderFloatDynamic: function () {
        var self = this;
        if (_.isUndefined(this.digits)) {
            var fieldOptions = self.recordData[this.nodeOptions.dynamic_digits_field.split('.')[0]];
            if (fieldOptions) {
                this._rpc({
                    model: fieldOptions.model,
                    method: 'read',
                    args: [fieldOptions.data.id],
                }).then(function (res) {
                    fieldOptions = _.extend(fieldOptions, res[0]);
                    self._finalRender(fieldOptions[self.nodeOptions.dynamic_digits_field.split('.')[1]]);
                });
            }
        } else {
            this._finalRender(this.digits);
        }
    },
    /**
     * @override
     */
    _renderReadonly: function () {
        this._renderFloatDynamic();
    },
    /**
     * @override
     */
    _prepareInput: function () {
        this.$input = $('<input/>', {
            class: 'o_field_widget o_field_number o_field_float_dynamic o_input',
            type: 'text',
        });
        this.$input.val(this.value);
        return this.$input;
    },
    /**
     * @override
     */
    _renderEdit: function () {
        this._prepareInput().appendTo(this.$el);
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onClick: function (ev) {
        if (this.mode === 'edit') {
            ev.preventDefault();
            ev.stopPropagation();
            this.$el.find('input').select();
        }
    },
    /**
     * @private
     */
    _onChange: function () {
        var newValue = this.$input.val();
        if (this.mode === 'edit') {
            this.removeInvalidClass();
            this._setValue(newValue);
            this._renderFloatDynamic();
        } else {
            this.setInvalidClass();
        }
    },
});

return {
    FieldFloatDynamic: FieldFloatDynamic,
};

});
