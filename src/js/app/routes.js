var app_routes = [
  {
    path: '/radios/',
    url: './static/radios.html',
    on: {
      pageInit: function (e, page) {
        var request = {};

        request.action = 'radios_refresh';
        sendRequest(request, socket_radios);
      },
    }
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
        // var request = {};
        // request.action = 'get_radio_options';
        // sendRequest(request, socket_radios);

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
          // var request = {};
          // var page = $$(this).closest('.page-content');

          // request.action = 'test_signal';
          // request.content = {}
          // request.content.radio_id = page.find('input[name=test_radio_id]:checked').val();
          // request.content.signal = page.find('#btn_signal').text();

          // sendRequest(request, socket_remotes);
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
        // $$('#rc_buttons_remove_btn').on('click', function () {
        //   var request = {};
        //   var buttons = [];
        //   var page = $$(this).closest('.page-content');

        //   request.action = 'rc_buttons_remove';
        //   request.content = {}
        //   request.content.rc_id = page.find('input[name=rc_id]').val();
        //   request.content.rc_name = page.find('input[name=rc_name]').val();
          
        //   page.find('input[name=button]:checked').each(function() {
        //       buttons.push($$(this).val());
        //   });

        //   request.content.buttons = buttons;

        //   sendRequest(request, socket_remotes);
        //   myApp.showIndicator();
        // });

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
