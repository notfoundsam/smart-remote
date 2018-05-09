var rc_action_sheet = app.actions.create({
  buttons: [
    {
      text: 'Catch IR signal',
      onClick: function () {
        var request = {};
        request.action = 'catch_signal';
        app.dialog.preloader('Waiting for signal');
        sendRequest(request, socket_remotes);
      }
    },
    {
      text: 'Sort Buttons',
      onClick: function () {
        app.alert('Button2 clicked');
      }
    },
    {
      text: 'Edit Button',
      onClick: function () {
        var rc_name = $$('div.page[data-page=rc_buttons]').attr('data-rc-name');
        var rc_id = $$('div.page[data-page=rc_buttons]').attr('data-rc-id');
        var buttons = [];

        $$('#buttons_area a.button').each(function() {
          var btn = {};

          btn.id = $$(this).attr('data-btn-id');
          btn.name = $$(this).text();

          buttons.push(btn);
        });

        mainView.router.load({
          url: 'static/rc_button_list.html',
          context: {
            remove: false,
            buttons: buttons,
            rc_id: rc_id,
            rc_name: rc_name
          }
        });
      }
    },
    {
      text: 'Remove Buttons',
      onClick: function () {
        var rc_name = $$('div.page[data-page=rc_buttons]').attr('data-rc-name');
        var rc_id = $$('div.page[data-page=rc_buttons]').attr('data-rc-id');
        var buttons = [];

        $$('#buttons_area a.button').each(function() {
          var btn = {};

          btn.id = $$(this).attr('data-btn-id');
          btn.name = $$(this).text();

          buttons.push(btn);
        });

        mainView.router.load({
          url: 'static/rc_button_list.html',
          context: {
            remove: true,
            buttons: buttons,
            rc_id: rc_id,
            rc_name: rc_name
          }
        });
      }
    },
    {
      text: 'Cancel',
      color: 'red',
    },
  ]
});
