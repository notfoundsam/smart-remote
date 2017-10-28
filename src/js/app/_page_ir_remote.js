myApp.onPageInit('ir_remote', function (page) {
    var rc_id = $$('div.page[data-page=ir_remote]').attr('data-rc-id');
    var request = {};

    request.action = 'remote_buttons_list';
    request.content = {}
    request.content.rc_id = rc_id;

    sendRequest(request, socket_remotes);
    myApp.showIndicator();

    $$('#ir_rc_menu_btn').on('click', function () {

        var buttons = [
            {
                text: 'Catch IR signal',
                onClick: function () {
                    var request = {};
                    request.action = 'catch_ir_signal';
                    sendRequest(request, socket_remotes);
                    myApp.showPreloader('Waiting for signal');
                }
            },
            {
                text: 'Sort Buttons',
                onClick: function () {
                    myApp.alert('Button2 clicked');
                }
            },
            {
                text: 'Remove Buttons',
                onClick: function () {
                    var rc_name = $$('div.page[data-page=ir_remote]').attr('data-rc-name');
                    var rc_id = $$('div.page[data-page=ir_remote]').attr('data-rc-id');
                    var buttons = [];

                    $$('#button_area a.button').each(function() {
                        var btn = {};

                        btn.id = $$(this).attr('data-btn-id');
                        btn.name = $$(this).text();
                        
                        buttons.push(btn);
                    });
                    
                    mainView.router.load({
                        url: 'static/remove_ir_buttons.html',
                        context: {
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
