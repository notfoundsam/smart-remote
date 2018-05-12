function activateConnection() {
  if (socket_remotes == null) {

    socket_remotes = io.connect('http://' + document.domain + ':' + location.port + '/remotes');
    socket_remotes.on('connect', function() {
      console.log('connected to remotes');
      var request = {};

      request.action = 'rc_refresh';
      sendRequest(request, socket_remotes);
    });
    socket_remotes.on('json', function(data) {
      console.log(data);
      if (data.response) {
        parseResponse(data.response);
      }
    });
  }

  if (socket_radios == null) {

    socket_radios = io.connect('http://' + document.domain + ':' + location.port + '/radios');
    socket_radios.on('connect', function() {
      console.log('connected to radios');
      var request = {};

      request.action = 'radios_refresh';
      sendRequest(request, socket_radios);
    });
    socket_radios.on('json', function(data) {
      console.log(data);
      if (data.response) {
        parseResponse(data.response);
      }
    });
  }
}

function sendRequest(request, socket) {
  if (socket != null) {
    console.log(request);
    socket.emit('json', request);
  } else {
    var notif = app.notification.create({
      icon: '<i class="fa fa-bell-o" aria-hidden="true"></i>',
      title: 'Socket',
      titleRightText: 'now',
      subtitle: 'This is a subtitle',
      text: 'No socket connection',
      closeTimeout: 3000,
      closeButton: true,
    });
    notif.open();
  }
}

function parseResponse(response) {
  if (response.result == 'success') {
    runCallback(response.callback, response);
  }
  else if (response.result == 'error') {
    var notif = app.notification.create({
      icon: '<i class="fa fa-bell-o" aria-hidden="true"></i>',
      title: 'Socket',
      titleRightText: 'now',
      subtitle: 'This is a subtitle',
      text: response.message,
      closeTimeout: 3000,
      closeButton: true,
    });
    notif.open();
  } else {
    var notif = app.notification.create({
      icon: '<i class="fa fa-bell-o" aria-hidden="true"></i>',
      title: 'Socket',
      titleRightText: 'now',
      subtitle: 'This is a subtitle',
      text: 'No socket connection',
      closeTimeout: 3000,
      closeButton: true,
    });
    notif.open();
  }
}

function redirectTo(page) {
  mainView.router.load({
    url: 'static/' + page + '.html'
  });
}

function runCallback(calback, args = '') {
  if (calback) {
    var func = callbacks[calback];

    if (typeof func === "function") { 
      func(args);
    }
  }
}
