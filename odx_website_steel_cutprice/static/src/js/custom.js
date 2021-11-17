/**
 * Custom Scripts.
 * Note: use this file to add or override any other scripts.
 * DON'T EDIT TEMPLATE JS FILES DIRECTLY, JUST USE THIS FILE.
 */

(function($, window, document, undefined) {
    'use strict';

    $(document).ready(function() {
        $('body').addClass('active-pageloader corporate header-sticky header-menu-with-icons header-transparent header-menu-border-bottom menu-center footer-widgets footer-background dark-color widgets-6 submenu-show-arrow-right menu-is-capitalized submenu-is-capitalized logo-text-is-capitalized page-index'
        );

    $('#oe_main_menu_navbar').remove();
    $('body').removeClass('o_connected_user');
    $('.carousel-item').removeAttr("style");
    $('.o_portal_wrap').addClass('portalHeight');
    var $pageloader = $('.pageloader');
    var $variantContainer;
    var $customInput = false;
    console.log("hehehee");
    console.log($(this).find('input.js_variant_change:checked, select.js_variant_change'));

    var $customInput = ($(this).find('select.js_variant_change'));
    var $Input = ($(this).find('input[data-value_name="Custom"]'));
    console.log($Input);
//    $("input").remove(".custom_value_own_line");


    $Input.remove();
     if ($Input) {
            alert("hellooooo!!!!");
//            $Input.find('[class=""]').removeAttr('class');
//            $('.variant_custom_value form-control custom_value_own_line').removeAttr;
//            $(this).find('input.custom_value_own_line').attr('type','hidden');
//            $('.variant_attribute .variant_custom_value.custom_value_own_line').css({
//
//                'display': 'inline-none !important;'
//            });
//            $Input.addClass('d-none !important');
//            $('.custom_value_own_line').css('display','none');
//            $Input.remove();
//              $(this).find('input.custom_value_own_line').style.display = "none";
//            $(this).find('custom_value_own_line').remove()
//            $('.custom_button').show();



        }
      else{
        $('.custom_button').hide();

      }
//        if ($variantContainer) {
//            if ($customInput && $customInput.data('is_custom') === 'True') {
//
//
//            }
//        }


    if ($('body').hasClass('active-pageloader') && $pageloader.length) {
        setTimeout(function() {
            $pageloader.removeClass('is-active');
        },500);


    }




        /**
         * Start Add Your New Scripts Below.
         */


    });



})(jQuery, window, document);






