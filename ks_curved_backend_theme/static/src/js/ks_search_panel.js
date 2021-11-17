odoo.define('ks_curved_backend_theme.KsSearchPanel', function (require) {
"use strict";

var SearchPanel = require('web.SearchPanel');
var core = require('web.core');
var QWeb = core.qweb;

var ksSearchPanel = SearchPanel.include({
     events:_.extend({}, SearchPanel.prototype.events, {
        'click .ks_close_catgy-modal': '_ksSearchPanelClose',
    }),

    init: function (parent, params) {
        this._super.apply(this, arguments);
        this.className = params.classes.concat(['ks_search_panel']).join(' ');
    },

    _render: function () {
        var self = this;
        this.$el.empty();

        // sort categories and filters according to their index
        var categories = Object.keys(this.categories).map(function (categoryId) {
            return self.categories[categoryId];
        });
        var filters = Object.keys(this.filters).map(function (filterId) {
            return self.filters[filterId];
        });
        var sections = categories.concat(filters).sort(function (s1, s2) {
            return s1.index - s2.index;
        });
        this.sections = sections
        self.$el.append(QWeb.render('ks_search_panel_back_botton', {}))
        sections.forEach(function (section) {
            if (Object.keys(section.values).length) {
                if (section.type === 'category') {
                    self.$el.append(self._renderCategory(section));
                } else {
                    self.$el.append(self._renderFilter(section));
                }
            }
        });
        if (self.$el.parents('.o_view_controller').find('.ks_search_control_panel').length){
            self.$el.parents('.o_view_controller').find('.ks_search_control_panel').replaceWith(QWeb.render('ks_control_search_panel', {filters: this.sections}));
        }
    },

    _ksSearchPanelClose(){
        $(".ks_search_panel").removeClass("show");
    },

});
});

