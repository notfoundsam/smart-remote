var app_routes = [
  {
    path: '/radios/',
    templateUrl: './static/radios.html',
    on: {
      pageInit: function (e, page) {
        var request = {};

        request.action = 'radios_refresh';
        sendRequest(request, socket_radios);

        page.$el.find('#radios_action_btn').on('click', function () {
          radios_action_sheet.open();
        });

        page.$el.find('#lirc_update_btn').on('click', function () {
          var request = {};

          request.action = 'lirc_update';
          sendRequest(request, socket_remotes);
        });
      },
    }
  },
  {
    name: 'rc_create',
    path: '/rc_create/',
    templateUrl: './static/rc_create.html',
    on: {
      pageInit: function (e, page) {
        page.$el.find('#rc_save_btn').on('click', function () {
          app.input.validateInputs('#rc_create_form');
          var content = app.form.convertToData('#rc_create_form');

          if (content.rc_name && content.rc_icon) {
            var request = {};
            request.action = 'rc_save';
            request.content = content;
            sendRequest(request, socket_remotes);
            mainView.router.navigate('/radios/');
          }
        });
      },
    }
  },
  {
    name: 'radio_create',
    path: '/radio_create/',
    templateUrl: './static/radio_create.html',
    on: {
      pageInit: function (e, page) {
        page.$el.find('#radio_save_btn').on('click', function () {
          app.input.validateInputs('#radio_create_form');
          var content = app.form.convertToData('#radio_create_form');

          if (content.radio_name && content.radio_pipe && content.radio_order) {
            var request = {};
            request.action = 'radio_save';
            request.content = content;
            sendRequest(request, socket_radios);
            mainView.router.navigate('/radios/');
          }
        });
      },
    },
  },
  {
    name: 'rc',
    path: '/rc/:rc_id',
    templateUrl: './static/rc.html',
    on: {
      pageInit: function (e, page) {
        var rc_id = page.$el.attr('data-rc-id');
        var request = {};

        request.action = 'get_rc_buttons';
        request.content = {}
        request.content.rc_id = rc_id;

        sendRequest(request, socket_remotes);
        app.preloader.show();
        
        $$('#rc_action_sheet').on('click', function () {
          rc_action_sheet.open();
        });
      },
      pageAfterIn: function (e, page) {
      },
    },
  },
  {
    name: 'button',
    path: '/button/',
    templateUrl: './static/button.html',
    on: {
      pageInit: function (e, page) {
        page.$el.find('#catch_ir_signal_btn').on('click', function () {
          var request = {};
          request.action = 'catch_ir_signal';
          app.dialog.preloader('Waiting for signal');
          sendRequest(request, socket_remotes);
        });

        page.$el.find('#button_save_btn').on('click', function () {
          app.input.validateInputs('#button_form');
          var content = app.form.convertToData('#button_form');
          
          if (content.button_name && content.button_order_ver && content.button_order_hor) {
            var request = {};
            request.action = 'button_save';
            request.content = content;
            sendRequest(request, socket_remotes);
            app.preloader.show();
          }
        });

        page.$el.find('#test_signal_btn').on('click', function () {
          var form = page.$el.find('#button_form');
          var button_type = form.find('input[name=button_type]:checked').val();

          var request = {};
          request.action = 'test_signal';
          request.content = {}
          
          if (button_type == 'ir') {
            var ir_signal = form.find('#ir_signal').text();

            if (ir_signal) {
              request.content.signal = ir_signal;
            } else {
              app.dialog.alert('No IR signal', 'Invalid input');
              return;
            }
          } else {
            var command = form.find('input[name=button_command]').val();

            if (command) {
              request.content.signal = command;
            } else {
              app.dialog.alert('No command', 'Invalid input');
              return;
            }
          }

          request.content.button_type = button_type;
          request.content.radio_id = page.$el.find('input[name=test_radio_id]:checked').val();
          sendRequest(request, socket_remotes);
        });
      },
      pageAfterIn: function (e, page) {
      },
    },
  },
  {
    name: 'button_list',
    path: '/button_list/',
    templateUrl: './static/button_list.html',
    on: {
      pageInit: function (e, page) {
        $$('#button_remove_btn').on('click', function () {
          var request = {};
          var buttons = [];
          var content = app.form.convertToData('#button_list_form');

          request.action = 'rc_button_remove';
          request.content = content;

          sendRequest(request, socket_remotes);
          app.preloader.show();
        });

        $$('#button_edit_btn').on('click', function () {
          var button = page.$el.find('input[name=button]:checked').val();

          if (!button)
            return;

          var request = {};
          request.action = 'button_edit';
          request.content = {}
          request.content.rc_id = page.$el.find('input[name=rc_id]').val();
          request.content.button = button;

          sendRequest(request, socket_remotes);
          app.preloader.show();
        });
      },
      pageAfterIn: function (e, page) {
      },
    },
  },
];
