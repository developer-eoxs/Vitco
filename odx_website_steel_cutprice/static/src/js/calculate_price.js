odoo.define('odx_website_steel_cut_price.calculate_price', function (require) {
"use strict";
var ajax = require('web.ajax');
var core = require('web.core');
var session = require('web.session');
var utils = require('web.utils');


$(function() {
    $('.calculate_price').click(function(e) {
		e.preventDefault();
		var width = $('#custom_width').val();
		var length = $('#custom_length').val();
		var thickness = $('#custom_thickness').val();
//		var thickness2 = $('#custom_thickness2').val();
		var qty = $('#custom_qty').val();
		var pro_variant = $('#product_template_id').val();

        ajax.jsonRpc('/custom/cut_price','call',{'width':width,'length':length,'thickness':thickness,'qty':qty,'pro_variant':pro_variant})
        .then(function(data){
         console.log(data)
         var total_price = data["total_price"];
         $('#display_size').hide();
         $('#computed_price').text(total_price);
//         document.getElementById("computed_price") = total_price;
         });
         });
});
});