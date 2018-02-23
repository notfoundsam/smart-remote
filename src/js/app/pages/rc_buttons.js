myApp.onPageInit('rc_buttons', function (page) {
    var rc_id = $$('div.page[data-page=rc_buttons]').attr('data-rc-id');
    var request = {};

    request.action = 'rc_buttons_refresh';
    request.content = {}
    request.content.rc_id = rc_id;

    sendRequest(request, socket_remotes);
    myApp.showIndicator();

    $$('#rc_buttons_action_btn').on('click', function () {

        var buttons = [
            {
                text: 'Catch IR signal',
                onClick: function () {
                    var request = {};
                    request.action = 'catch_signal';
                    myApp.showPreloader('Waiting for signal');
                    sendRequest(request, socket_remotes);
                }
            },
            {
                text: 'Sort Buttons',
                onClick: function () {
                    myApp.alert('Button2 clicked');
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
                onClick: function () {
                    myApp.alert('Cancel clicked');
                }
            },
        ];
        myApp.actions(buttons);
    });
});
