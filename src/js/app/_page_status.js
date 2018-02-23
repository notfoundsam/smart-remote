myApp.onPageInit('status', function (page) {
    console.log('OoooPage');
    var request = {};

    request.action = 'radios_refresh';
    sendRequest(request, socket_radios);
    
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
                text: 'Add Radio',
                onClick: function () {
                    mainView.router.load({
                        url: 'static/radio_create.html'
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

    $$('#lirc_update_btn').on('click', function () {
        var request = {};

        request.action = 'lirc_update';
        sendRequest(request, socket_remotes);
    });
});
