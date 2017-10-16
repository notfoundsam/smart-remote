// Initialize app
var myApp = new Framework7({
    //Tell Framework7 to compile templates on app init
    template7Pages: true,
    material: true,
    // domCache: false,
    // cache: false
});
 
// If we need to use custom DOM library, let's save it to $$ variable:
var $$ = Dom7;

var socket_remotes = null;
var socket_commands = null;
 
// Add view
var mainView = myApp.addView('.view-main', {
  // Because we want to use dynamic navbar, we need to enable it for this view:
  // dynamicNavbar: true
});

$$.ajax({
    url: '/api/v1.0/login',
    type: 'POST',
    success: function (data) {
        var d_obj = JSON.parse(data);
        console.log(d_obj.status_code);
        if (d_obj.status_code == 100 || d_obj.status_code == 20) {
            var devices = d_obj.devices ? d_obj.devices : [];

            mainView.router.load({
                url: 'static/status.html',
                reload: true,
                context: {
                    title: 'Choice device',
                    devices: devices
                }
            });

            activateConnection();
        } else {
            myApp.addNotification({
                message: 'Programm error',
                hold: 3000
            });
        }
        // getTemperature();
    },
    statusCode: {
        401: function (xhr) {
            myApp.loginScreen();
        }
    }
});
