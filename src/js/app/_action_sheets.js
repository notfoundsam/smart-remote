var rc_action_sheet = app.actions.create({
  buttons: [
    {
      text: 'Add button',
      onClick: function () {

        mainView.router.navigate('/button/', {
          context: {
            button: {
              rc_id: $$('div.page[data-name=rc]').attr('data-rc-id'),
              btn_type: 'ir'
            }
          }
        });
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
