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
            var request = {};

            request.action = 'remote_list';
            sendRequest(request, socket_remotes);
            // socket_remotes.emit('my event', {data: 'I\'m connected!'});
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

function refreshRemoteMenu(remotes) {
    var menu = $$('#remotes ul');
    menu.empty();

    remotes.forEach(function(element) {
        var li = $$('<li>');
        var anchor = $$('<a href="#" class="item-link item-content close-panel"></a>');
        var icon = $$('<div class="item-media"><i class="' + element.icon + ' size-25" aria-hidden="true"></i></div>');
        var inner = $$('<div class="item-inner"></div>');
        var title = $$('<div class="item-title"></div>').text(element.name);

        anchor.attr('data-type', element.type);
        anchor.attr('data-id', element.identificator);
        anchor.attr('data-title', element.name);

        anchor.on('click', function (e) {
            var data = $$(this).dataset();
            loadRemoteControl(data);
            console.log(data);
        });

        inner.append(title);
        anchor.append(icon);
        anchor.append(inner);
        li.append(anchor);
        menu.append(li);
    });

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

function parseResponse(response) {
    if (response.result == 'success') {
        myApp.hideIndicator();

        if (response.callback == 'add_remote_to_menu') {
            var request = {};

            request.action = 'remote_list';
            sendRequest(request, socket_remotes);
            
            redirectTo('status');
        } else if (response.callback == 'refresh_remote_menu') {
            refreshRemoteMenu(response.remotes);
        } else if (response.callback == 'waiting_ir_signal') {
            myApp.showPreloader('Waiting for signal');
            // myApp.alert('Waiting for signal', 'Waiting', function () {
            //     myApp.alert('Button clicked!');
            // });
        } else if (response.callback == 'ir_signal_recived') {
            // refreshRemoteMenu(response.remotes);
            console.log('signal ok');
        } else if (response.callback == 'ir_signal_failed') {
            myApp.hidePreloader()
            // console.log('faild');
            myApp.addNotification({
                message: 'Signal didn\'t recive',
                hold: 3000
            });
        }

        return;
    }

    myApp.addNotification({
        message: 'No socket connection',
        hold: 3000
    });
}

function redirectTo(page) {
    mainView.router.load({
        url: 'static/' + page + '.html'
    });
}

function addRemoteToMenu() {
}

function loadRemoteControl(data) {
    if (data.type == 'ir_rc') {
        console.log(data.title)
        // if (mainView.url == 'ir_remote.html') {
        //     mainView.router.reloadContent(content)
        // }
        mainView.router.load({
            url: 'static/ir_remote.html',
            reload: (mainView.url == 'static/ir_remote.html'),
            ignoreCache: true,
            // animatePages: true,
            context: {
                title: data.title,
                id: data.id
            }
        });
    }
}


