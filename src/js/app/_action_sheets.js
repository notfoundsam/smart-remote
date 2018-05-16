var radios_action_sheet = app.actions.create({
  buttons: [
    {
      text: 'Add remote control',
      onClick: function () {
        mainView.router.navigate('/rc_create/');
      }
    },
    {
      text: 'Add radio',
      onClick: function () {
        mainView.router.navigate('/radio_create/', {
          context: {
            radio: {},
            new: true
          },
        });
      }
    },
    {
      text: 'Cancel',
      color: 'red',
    },
  ]
});

var rc_action_sheet = app.actions.create({
  buttons: [
    {
      text: 'Add button',
      onClick: function () {

        var request = {};
        request.action = 'button_edit';
        request.content = {}
        request.content.rc_id = $$('div.page[data-name=rc]').attr('data-rc-id');

        sendRequest(request, socket_remotes);
        app.preloader.show();
      }
    },
    // {
    //   text: 'Sort Buttons',
    //   onClick: function () {
    //     app.alert('Button2 clicked');
    //   }
    // },
    {
      text: 'Edit Button',
      onClick: function () {
        var rc_id = $$('div.page[data-name=rc]').attr('data-rc-id');
        var buttons = [];

        $$('#buttons_area button.button').each(function() {
          var btn = {};

          btn.id = $$(this).attr('data-btn-id');
          btn.name = $$(this).text();

          buttons.push(btn);
        });

        mainView.router.navigate('/button_list/', {
          context: {
            remove: false,
            buttons: buttons,
            rc_id: rc_id,
          }
        });
      }
    },
    {
      text: 'Remove Buttons',
      onClick: function () {
        var rc_id = $$('div.page[data-name=rc]').attr('data-rc-id');
        var buttons = [];

        $$('#buttons_area button.button').each(function() {
          var btn = {};

          btn.id = $$(this).attr('data-btn-id');
          btn.name = $$(this).text();

          buttons.push(btn);
        });

        mainView.router.navigate('/button_list/', {
          context: {
            remove: true,
            buttons: buttons,
            rc_id: rc_id,
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
