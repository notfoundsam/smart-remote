function getTemperature() {
    var interval = 5000;
    var tid = setTimeout(setTimer, interval);
    
    function setTimer() {
        $$.ajax({
            url: '/api/v1.0/device/therm/status',
            type: 'GET',
            success: function (data) {
                var d_obj = JSON.parse(data);
                if (d_obj.status_code != 100) {
                    myApp.addNotification({
                        message: 'Could not get temperature',
                        hold: 3000
                    });
                    clearInterval(tid);
                    return;
                }

                console.log(d_obj.result);
                $$('div[data-page=devices] .temp').text(d_obj.result.temp + "*C");
                $$('div[data-page=devices] .hum').text(d_obj.result.hum + "%");
                tid = setTimeout(setTimer, interval);

            }
            // statusCode: {
            //  401: function (xhr) {
            //      myApp.loginScreen();
            //  }
            // }
        });
    }
    function abortTimer(tid) { // to be called when you want to stop the timer
      clearInterval(tid);
    }
}

function activateConnection() {
    if (socket_remotes == null) {
        
        socket_remotes = io.connect('http://' + document.domain + ':' + location.port + '/remotes');
        socket_remotes.on('connect', function() {
            console.log('connected to remotes');
            // socket_remotes.emit('my event', {data: 'I\'m connected!'});
        });
        socket_remotes.on('message', function(msg) {
            console.log(msg);
        });
        socket_remotes.on('json', function(msg) {
            console.log(msg);
        });
    }
    // console.log(socket_remotes);
    // if (socket_commands == null) {
        
    //     socket = io.connect('http://' + document.domain + ':' + location.port + '/commands');
    //     socket.on('connect', function() {
    //         console.log('connected to commands');
    //         // socket.emit('my event', {data: 'I\'m connected!'});
    //     });
    //     socket.on('message', function(msg) {
    //         console.log(msg);
    //     });
    // }
}

function sendRequest(request, socket) {
    if (socket != null) {
        socket.emit('json', request);

        return true;
    }
    myApp.addNotification({
        message: 'No socket connection',
        hold: 3000
    });
}
