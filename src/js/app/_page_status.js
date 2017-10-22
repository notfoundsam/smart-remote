myApp.onPageInit('status', function (page) {
    $$('#rc_menu_btn').on('click', function () {
        var buttons = [
            {
                text: 'Add Remote',
                onClick: function () {
                    mainView.router.load({
                        url: 'static/add_remote.html'
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
});
