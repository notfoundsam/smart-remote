myApp.onPageInit('status', function (page) {
    $$('#rc_action_btn').on('click', function () {
        var buttons = [
            {
                text: 'Add Remote',
                onClick: function () {
                    mainView.router.load({
                        url: 'static/rc_create.html'
                    });
                }
            },
            {
                text: 'Sort Remote',
                onClick: function () {
                    myApp.alert('Button2 clicked');
                }
            },
            {
                text: 'Remove Remote',
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

    $$('#regenerate_lirc_btn').on('click', function () {
        var request = {};

        request.action = 'regenerate_lirc_commands';
        sendRequest(request, socket_remotes);
    });
});
