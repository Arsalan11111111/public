/** @odoo-module **/

import { _t } from 'web.core';
import { Markup } from 'web.utils';
import tour from 'web_tour.tour';

tour.register('lims_sampling_tour', {
    url: "/web",
    rainbowManMessage: _t("Congrats !"),
    sequence: 10,
}, [tour.stepUtils.showAppsMenuItem(),
{
    trigger: '.o_app[data-menu-xmlid="lims_base.menu_root"]',
    content: Markup(_t('Ready to configure your sampling points? Let\'s have a look at your <b>Lims</b>.')),
    position: 'bottom',
    edition: 'enterprise',
}, {
    trigger: '.dropdown-toggle[data-menu-xmlid="lims_base.lims_master_data_submenu"]',
    content: Markup(_t('As Lims manager, you can access to a new menu part in <b>master data</b>.')),
    position: 'bottom',
    edition: 'enterprise',

}, {
    trigger: '.dropdown-item[data-menu-xmlid="lims_sampling.lims_sampling_point_menu"]',
    content: Markup(_t('This is the access to configure <b>new samplings points</b>.')),
    position: 'bottom',
    edition: 'enterprise',
    run: "click",

}, {
    trigger: ".o_list_button_add",
    content: Markup(_t('Create a new sampling point.')),
    position: "top",
    run: "click",
}, {
    trigger: ".o_field_char[name='name']",
    content: Markup(_t('Set the sampling\'s point name.')),
    position: "top",
    run: "text Sampling point form tour test",
}, {
    trigger: '.o_field_many2one[name="matrix_id"]',
    content: Markup(_t('Set the sampling point\'s matrix.')),
    position: "top",
    run: 'click',
}
]);
