odoo.define('your_module.loading_script', function (require) {
  "use strict";
  
  $(document).ready(function() {
    $('#loading').show();

    setTimeout(function() {
      window.location.href = window.location.href.replace("timbrado", "timbrar");
    }, 5000);

    setTimeout(function() {
      alert("Archivo descargado y enviado por correo");
      window.location.href = window.location.href.replace("timbrado/", "");
    }, 60000);
  });

});
