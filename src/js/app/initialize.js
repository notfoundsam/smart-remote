// Initialize app
var app = new Framework7({
  //Tell Framework7 to compile templates on app init
  root: '#app',
  panel: {
    swipe: 'right',
    leftBreakpoint: 768,
    rightBreakpoint: 1440,
  },
  routes: app_routes,
});

// If we need to use custom DOM library, let's save it to $$ variable:
var $$ = Dom7;

var socket_remotes = null;
var socket_radios = null;

// Add view
var mainView = app.views.create('.view-main', {
  // url: '/'
});

var loginScreen = app.loginScreen.create({
  el: '.login-screen',
  // animate: true
});

app.request({
  url: '/api/v1.0/login',
  method: 'POST',
  success: function (data) {
    var d_obj = JSON.parse(data);

    if (d_obj.status_code == 100 || d_obj.status_code == 20) {
      mainView.router.navigate('/radios/');

      activateConnection();
    } else {
      var notif = app.notification.create({
        icon: '<i class="fa fa-bell-o" aria-hidden="true"></i>',
        title: 'Application',
        titleRightText: 'now',
        subtitle: 'This is a subtitle',
        text: 'Programm error',
        closeTimeout: 3000,
        closeButton: true,
      });
      notif.open();
    }
  },
  statusCode: {
    401: function (xhr) {
      loginScreen.open();
    }
  }
});

