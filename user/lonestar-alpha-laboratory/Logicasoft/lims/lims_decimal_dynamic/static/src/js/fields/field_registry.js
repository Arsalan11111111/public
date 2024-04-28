odoo.define('lims_decimal_dynamic.field_registry', function (require) {
"use strict";

var registry = require('web.field_registry');
var relationalFields = require('lims_decimal_dynamic.relational_fields');

registry.add('float_dynamic', relationalFields.FieldFloatDynamic);

});
