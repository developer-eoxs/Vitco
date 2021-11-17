odoo.define("ks_curved_backend_theme.ks_list_renderer", function (require) {
  "use strict";

  var ajax = require("web.ajax");
  var ListRenderer = require("web.ListRenderer");
  var DocumentViewer = require("mail.DocumentViewer");
  var core = require("web.core");
  var _t = core._t;

  var Ks_ListRenderer = ListRenderer.include({
    events: _.extend({}, ListRenderer.prototype.events, {
      "click .ks_attachment_id": "_onksViewAttachment",
      "click tbody .ks_attachment_data": "_onksAttachmentDivClicked",
      "change input": "_onksInputChange",
    }),

    // Showing preview of attachments
    _onksViewAttachment: function (ev) {
      var att_id = parseInt($(ev.currentTarget).data("id"));
      var att_mime = $(ev.currentTarget).data("mime");
      var att_name = $(ev.currentTarget).data("name");
      var rec_id = parseInt($(ev.currentTarget).data("ks-rec-id"));
      var att_data = this.ks_data;

      var match = att_mime.match("(image|video|application/pdf|text)");
      if (match) {
        var ks_attachment = [];
        att_data[rec_id].forEach((attachment) => {
          if (attachment.att_mime.match("(image|video|application/pdf|text)")) {
            ks_attachment.push({
              filename: attachment.att_name,
              id: attachment.att_id,
              is_main: false,
              mimetype: attachment.att_mime,
              name: attachment.att_name,
              type: attachment.att_mime,
              url: "/web/content/" + attachment.att_id + "?download=true",
            });
          }
        });
        var ks_activeAttachmentID = att_id;
        var ks_attachmentViewer = new DocumentViewer(
          self,
          ks_attachment,
          ks_activeAttachmentID
        );
        ks_attachmentViewer.appendTo($("body"));
      } else
        this.call("notification", "notify", {
          title: _t("File Type Not Supported"),
          message: _t("This file type can not be previewed"),
          sticky: false,
        });
    },

    willStart: async function () {
      const _super = this._super.bind(this);
      var self = this;
      // getting the attachments data
      await ajax
        .jsonRpc("/ks_list_renderer/attachments", "call", {
          res_ids: this.state.res_ids,
          model: this.state.model,
          domain: this.state.domain,
        })
        .then(function (data) {
          self.ks_data = data[0];
          self.ks_list_ = data[1];
        });
      return _super(...arguments);
    },

    _renderRow: function (record) {
      var self = this;
      var ks_attachment_limit = 5;
      var $tr = this._super.apply(this, arguments);
      if (self.ks_list_["ks_list_density"] == "Comfortable")
        $tr.addClass("ks_comfortable_list");
      else if (self.ks_list_["ks_list_density"] == "Attachment") {
        var att_data = this.ks_data;
        // adding div below the row having attachments
        if (att_data[record.data.id]) {
          var $outer_div = $("<div>", {
            class: "ks_attachment_data_outer",
          });
          var $inner_div = $("<div>", {
            class: "ks_attachment_data",
            id: record.id,
          });

          att_data[record.data.id].every((attachment, index, arr) => {
            if (index < ks_attachment_limit) {
              var $att_div = $("<div>", {
                class: "ks_attachment_id",
                "data-id": attachment.att_id,
                "data-name": attachment.att_name,
                "data-mime": attachment.att_mime,
                "data-ks-rec-id": record.data.id,
              });

              // attachment mimetype for image
              $att_div = $att_div.append(
                $("<div/>", {
                  "data-mimetype": attachment.att_mime,
                  class: "o_image",
                })
              );

              // attachment name div
              var $div_att_name = $("<div>", {
                class: "ks_attachment_name",
              }).append($("<span>").html(attachment.att_name));

              $att_div = $att_div.append($div_att_name);
              //appending both mimetype and name to the inner div
              $inner_div = $inner_div.append($att_div);
              return true;
            } else {
              var $att_div = $("<div>", {
                class: "ks_attach_counter ks_attachment_id",
                "data-id": attachment.att_id,
                "data-name": attachment.att_name,
                "data-mime": attachment.att_mime,
                "data-ks-rec-id": record.data.id,
              });
              // attachment counter div
              var $div_att_name = $("<div>", {
                class: "ks_attachment_name",
              }).append(
                $("<span>").html("+" + (arr.length - ks_attachment_limit))
              );
              $att_div = $att_div.append($div_att_name);
              //appending both mimetype and name to the inner div
              $inner_div = $inner_div.append($att_div);
              return false;
            }
          });
          var $div = $outer_div.append($inner_div);
          $tr = $tr.add($div);
        }
      }

      return $tr;
    },
    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onksAttachmentDivClicked: function (ev) {
      if (ev.target.className == "ks_attachment_data") {
        var id = $(ev.currentTarget.parentElement.previousElementSibling).data(
          "id"
        );
        if (id) {
          this.trigger_up("open_record", {
            id: id,
            target: ev.target,
          });
        }
      }
    },
    /**
     * To toggle class for adding bgcolor on selecetd rows
     * @private
     * @param {MouseEvent} ev
     */
    _onksInputChange: function (ev) {
      var self = this;
      var $ksrow = ev.currentTarget.closest("tr");
      var $ksparent = $ksrow.parentElement.localName;
      if ($ksparent == "thead") {
        var $ksrows = ev.delegateTarget.querySelector("tbody").children;
        _.each($ksrows, function (row) {
            if ($(row).find('td').length > 1){
                row.classList.toggle("ks_row_selected", ev.currentTarget.checked);
                self._ksApplyBgColorRow(row, ev.currentTarget.checked);
            }
        });
      } else if ($ksparent == "tbody"){
        $ksrow.classList.toggle("ks_row_selected", ev.currentTarget.checked);
        self._ksApplyBgColorRow($ksrow, ev.currentTarget.checked);
      }
    },

    _ksApplyBgColorRow(ksRow, status){
        var self = this;
        var ks_primary = document.body.style.getPropertyValue('--primary');
        ks_primary = self._ksHexToRGB(ks_primary);
        // Apply color.
        if (status){
            $(ksRow).css({'background-color': `rgba(${ks_primary.r},${ks_primary.g},${ks_primary.b}, 0.3)`});
            if ($(ksRow).attr('data-id')){
                $(".ks_attachment_data[id='"+$(ksRow).attr('data-id')+"']").css({'background-color': `rgba(${ks_primary.r},${ks_primary.g},${ks_primary.b}, 0.3)`});
            }
        }
        // Remove color.
        else{
            $(ksRow).css({'background-color': 'transparent'});
            if ($(ksRow).attr('data-id')){
                $(".ks_attachment_data[id='"+$(ksRow).attr('data-id')+"']").css({'background-color': 'transparent'});
            }
        }
    },

    _ksHexToRGB: function (hex) {
        var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result
          ? {
              r: parseInt(result[1], 16),
              g: parseInt(result[2], 16),
              b: parseInt(result[3], 16),
            }
          : null;
      },
  });
  return Ks_ListRenderer;
});
