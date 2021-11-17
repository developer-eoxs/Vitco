odoo.define('odx_website_steel_cutprice.VariantMixin', function (require) {
'use strict';

var VariantMixin = require('sale.VariantMixin');
var publicWidget = require('web.public.widget');
var ajax = require('web.ajax');
var core = require('web.core');
var QWeb = core.qweb;


/**
 * Addition to the variant_mixin.handleCustomValues
 *This is added to change the custom behaviour of input box and pop up a modal to show some features and then add to cart
 */


publicWidget.registry.WebsiteSale.include({
    /**
     * Adds the input modal to the regular handleCustomValues method
     * @override
     */
    handleCustomValues: function ($target) {
        var $variantContainer;
        var $customInput = false;
        if ($target.is('input[type=radio]') && $target.is(':checked')) {
            $variantContainer = $target.closest('ul').closest('li');
            $customInput = $target;
        } else if ($target.is('select')) {
            $variantContainer = $target.closest('li');
            $customInput = $target
                .find('option[value="' + $target.val() + '"]');
        }

        if ($variantContainer) {
            if ($customInput && $customInput.data('is_custom') === 'True') {
                var attributeValueId = $customInput.data('value_id');
                var attributeValueName = $customInput.data('value_name');

                if ($variantContainer.find('.variant_custom_value').length === 0
                        || $variantContainer
                              .find('.variant_custom_value')
                              .data('custom_product_template_attribute_value_id') !== parseInt(attributeValueId)) {
                    $variantContainer.find('.variant_custom_value').remove();
                     var $input = $('<button>',
                    {
                        type: 'button',
                        'data-custom_product_template_attribute_value_id': attributeValueId,
                        'data-attribute_value_name': attributeValueName,
                        class:'btn btn-secondary btn-lg mt16 variant_custom_value custom_attribute',
                        style:'width:120px;height:45px;font-size:17px;',
                        text:'Customize',
                        'data-toggle':'modal',
                        'data-target':'#modalaccept'
                    });

                    var isRadioInput = $target.is('input[type=radio]') &&
                        $target.closest('label.css_attribute_color').length === 0;

                    if (isRadioInput && $customInput.data('is_single_and_custom') !== 'True') {
                        $input.addClass('custom_value_radio');
                        $target.closest('div').after($input);
                    } else {
                        $input.attr('placeholder', attributeValueName);
                        $input.addClass('custom_value_own_line');
                        $variantContainer.append($input);
                    }
                }
            } else {
                $variantContainer.find('.variant_custom_value').remove();
            }
        }
    },

});

return VariantMixin;

});
