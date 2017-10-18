$$('#login').on('click', function() {
    var username = $$('input[name=username]').val();
    var password = $$('input[name=password]').val();

    if (!username || !password) {
        myApp.alert('Enter both username and password', 'Input error');
        return;
    }

    $$.ajax({
        url: '/api/v1.0/login',
        type: 'POST',
        data: {
            username: username,
            password: password
        },
        success: function (data) {
            var d_obj = JSON.parse(data);
            switch (d_obj.status_code) {
                case 10: 
                    // $$('#username').text(d_obj.result.current_user);
                    // current_bidder = d_obj.result.current_bidder;
                    mainView.router.load({
                        url: 'static/status.html'
                    });
                    myApp.closeModal('.login-screen');
                    break;
                case 20: 
                    myApp.closeModal('.login-screen');
                    break;
                case 30:
                    myApp.alert('Login or password incorect', 'Login error');
                    break;
            }
        }
    });
});

$$('#logout').on('click', function() {
    $$.ajax({
        url: '/api/v1.0/login',
        type: 'POST',
        data: {
            username: username,
            password: password
        },
        success: function (data) {
            var d_obj = JSON.parse(data);
            switch (d_obj.status_code) {
                case 40: 
                    myApp.loginScreen();
                    break;
                default:
                    myApp.alert('Refresh the page', 'Logout error');
                    break;
            }
        }
    });
});
