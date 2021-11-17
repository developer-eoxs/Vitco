
odoo.define('odx_steel_production', function (require) {
"use strict";
    var ListRenderer = require('web.ListRenderer');

       ListRenderer.include({
            _renderBody: function () {
                var $rows = this._renderRows();
                    var list_new=['steel.production','job.order']
                    console.log(this);
                    if (list_new.includes(this.__parentedParent.model)){

                        }
                    else
                        while ($rows.length < 4) {
                        $rows.push(this._renderEmptyRow());
                        }
                return $('<tbody>').append($rows);
        },

})
})

//odoo.define('you_module_name.ListView', function (require) {
//       "use strict";
//
//       // First retrieve the veiw from view_registry
//       ListView = core.view_registry.get('list');
//
//       // now use include to override the render method
//       ListView.include({
//            render: function () {
//                // call super method first
//                this._super();
//                // then override what you need
//                // and best thing here is that you can dor this for
//                // your model only
//                if (this.model == 'odx_steel_production.pro.multi.lot.line'){
//                    this.pad_table_to(1);
//                }
//            }
//       });
//
//        }