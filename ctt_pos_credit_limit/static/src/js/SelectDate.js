odoo.define('point_of_sale.SelectDate', function(require) {
  'use strict';
  const PosComponent = require('point_of_sale.PosComponent');
  const {useListener} = require('@web/core/utils/hooks');
  const Registries = require('point_of_sale.Registries');
  const pos_models = require('point_of_sale.models');
  class SelectDate extends PosComponent {
    setup() {
      super.setup();
      useListener('click', this.onClick);
    }
    async setDate(th) {
      var bucle = false
      var confirmado = false
      do {
        const {confirmed, payload: inputNote} =
            await th.showPopup('SelectDatePopup', {
              startingValue: '',
              title: th.env._t('Fecha de aplazo'),
            });
        var motivo = inputNote
        var confirmado = confirmed
        console.log('FECHA')
        if (confirmed && motivo[0] == '') {
          await th.showPopup('ErrorPopup', {
            title: th.env._t('Fecha Incorrecta'),
            body: th.env._t('Ingrese una fecha correcta para aplazar deuda.'),
          });
        }
        if (confirmed && motivo[0] != '') {
          if (new Date(motivo[0]) < new Date()) {
            await th.showPopup('ErrorPopup', {
              title: th.env._t('Fecha Incorrecta'),
              body: th.env._t('Ingrese una mayor a la de hoy.'),
            });
            bucle = false
          }
          else
          bucle = true
        }
        if (confirmed == false) {
          bucle = true
        }
      }
      while (!bucle)
        if (confirmado) {
          return motivo
        } else {
          motivo = false
          return motivo
        }
    }
  }
  Registries.Component.add(SelectDate);
  return SelectDate;
});