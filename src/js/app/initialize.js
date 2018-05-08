// Initialize app
var myApp = new Framework7({
  //Tell Framework7 to compile templates on app init
  // template7Pages: true,
  // material: true,
  root: '#app',
  // domCache: false,
  // cache: false
  panel: {
    swipe: 'right',
    leftBreakpoint: 768,
    rightBreakpoint: 1440,
  },
  routes: [
    {
      path: '/rc/:rc_id',
      templateUrl: './static/rc.html',
      on: {
        pageInit: function (e, page) {
          // console.log(e);
          // console.log(page.$el.attr('data-rc-id'));
          var rc_id = page.$el.attr('data-rc-id');
          var request = {};

          request.action = 'get_rc_buttons';
          request.content = {}
          request.content.rc_id = rc_id;

          sendRequest(request, socket_remotes);
          myApp.preloader.show();
        },
      },
      // options: {
      //   context: {
      //     title: 'Component Page',
      //   },
      // },
      // data: function () {
      //   return {
      //     title: 'Component Page',
      //     names: ['John', 'Vladimir', 'Timo'],
      //   }
      // },
    },
    {
      name: 'about',
      path: '/about/:rc_id',
      url: './static/about.html',
      on: {
        pageAfterIn: function (e, page) {
          // do something after page gets into the view
        },
        pageInit: function (e, page) {
          console.log('init');
        },
      }
    },
  ],
});

// If we need to use custom DOM library, let's save it to $$ variable:
var $$ = Dom7;

var socket_remotes = null;
var socket_radios = null;

// Add view
var mainView = myApp.views.create('.view-main', {
  // Because we want to use dynamic navbar, we need to enable it for this view:
  // dynamicNavbar: true
  // domCache: true
});

var loginScreen = myApp.loginScreen.create({
  el: '.login-screen',
  // animate: true
});

myApp.request({
  url: '/api/v1.0/login',
  method: 'POST',
  success: function (data) {
    var d_obj = JSON.parse(data);

    if (d_obj.status_code == 100 || d_obj.status_code == 20) {
      // mainView.router.load({
      //   url: 'static/status.html',
      // });

      activateConnection();
    } else {
      myApp.addNotification({
        message: 'Programm error',
        hold: 3000
      });
    }
  },
  statusCode: {
    401: function (xhr) {
      loginScreen.open();
    }
  }
});

