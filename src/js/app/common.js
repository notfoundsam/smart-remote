function activateConnection() {
    if (socket_remotes == null) {
        
        socket_remotes = io.connect('http://' + document.domain + ':' + location.port + '/remotes');
        socket_remotes.on('connect', function() {
            console.log('connected to remotes');
            var request = {};

            request.action = 'rc_refresh';
            sendRequest(request, socket_remotes);
        });
        // socket_remotes.on('message', function(msg) {
        //     console.log(msg);
        // });
        socket_remotes.on('json', function(data) {
            console.log(data);
            if (data.response) {
                parseResponse(data.response);
            }
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
        console.log(request);
        socket.emit('json', request);
    } else {
        myApp.addNotification({
            message: 'No socket connection',
            hold: 3000
        });
    }
}

function parseResponse(response) {
    if (response.result == 'success') {
        runCallback(response.callback, response);
    }
    else if (response.result == 'error') {
        myApp.addNotification({
            message: response.message,
            hold: 3000
        });
    } else {
        myApp.addNotification({
            message: 'No socket connection',
            hold: 3000
        });
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
