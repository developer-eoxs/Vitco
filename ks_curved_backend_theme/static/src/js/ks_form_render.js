odoo.define("ks_curved_backend_theme.ks_form_renderer", function (require) {
  "use strict";

  var FormRenderer = require("web.FormRenderer");

  var Ks_FormRenderer = FormRenderer.include({
    // FixMe: Remove before in case of no events
    events: _.extend({}, FormRenderer.prototype.events, {}),
    /**
     * @override
     * To bind this with ks_form_resize
     */
    init: function () {
      this._super.apply(this, arguments);
      this.ks_from_resize = _.debounce(this.ks_from_resize.bind(this), 200);
    },
    /**
     * @override
     */
    start() {
      window.addEventListener("resize", this.ks_from_resize);
      return this._super(...arguments);
    },
    /**
     * @override
     */
    destroy() {
      window.removeEventListener("resize", this.ks_from_resize);
      return this._super(...arguments);
    },
    /**
     * @override
     */
    _applyFormSizeClass: function () {
      this.ks_from_resize();
      return this._super(...arguments);
    },
    /**
     * ## Already Handled in ENTERPRISE
     * To add and remove classes for chatter position
     */
    ks_from_resize() {
      if (
        window.matchMedia("(min-width: 1400px)").matches &&
        this?.$el[0].classList.contains("o_form_view")
      )
        this?.$el[0].classList.add("ks_large_screen");
      else if (this?.$el[0].classList.contains("ks_large_screen"))
        this?.$el[0].classList.remove("ks_large_screen");
    },
  });
  return Ks_FormRenderer;
});
