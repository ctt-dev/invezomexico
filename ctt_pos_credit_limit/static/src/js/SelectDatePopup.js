odoo.define('point_of_sale.SelectDatePopup', function(require) {
  'use strict';
  const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
  const Registries = require('point_of_sale.Registries');
  const {_lt} = require('@web/core/l10n/translation');
  const {onMounted, useRef, useState} = owl;
  class SelectDatePopup extends AbstractAwaitablePopup {
    setup() {
      super.setup();
      this.state = useState({inputValue: this.props.startingValue, inputValueMotivo: this.props.endingValue});
      this.inputRef = useRef('input');
      this.inputRefMotivo = useRef('inputMotivo');
      onMounted(this.onMounted);
    }
    onMounted() {
      this.inputRef.el.focus();
    }
    getPayload() {
      return [this.state.inputValue, this.state.inputValueMotivo];
    }
  }
  SelectDatePopup.template = 'SelectDatePopup';
  SelectDatePopup.defaultProps = {
    confirmText: _lt('Ok'),
    cancelText: _lt('Cancel'),
    title: '',
    body: '',
  };
  Registries.Component.add(SelectDatePopup);
  return SelectDatePopup;
});