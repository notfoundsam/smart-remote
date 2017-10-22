myApp.onPageInit('ir_remote', function (page) {
    var rc_id = $$('div.page[data-page=ir_remote]').attr('data-rc-id');
    console.log(rc_id);

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
                    myApp.alert('Button2 clicked');
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
