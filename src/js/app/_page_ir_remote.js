myApp.onPageInit('ir_remote', function (page) {
    $$('#ir_rc_menu_btn').on('click', function () {

        var buttons = [
            {
                text: 'Catch IR signal',
                onClick: function () {
                    var request = {};

                    request.action = 'catch_ir_signal';
                    // request.content = {}
                    // console.log(request);
                    sendRequest(request, socket_remotes);
                    myApp.showIndicator();

                    // mainView.router.load({
                    //     url: 'static/add_remote.html',
                    //     context: {
                    //         title: 'IR Remote',
                    //     }
                    // });
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
