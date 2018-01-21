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

            request.action = 'refresh_rc_list';
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
        });

        inner.append(title);
        anchor.append(icon);
        anchor.append(inner);
        li.append(anchor);
        menu.append(li);
    });
}

function refreshRemoteButtons(buttons, rc_name) {
    var page = $$('div.page[data-page=ir_remote]');

    if (page.length && buttons.length) {
        var button_area = $$('#button_area');

        var row = 0;

        var content_block = $$('<div class="content-block"></div>');
        var buttons_row = null;

        buttons.forEach(function(element) {
            if (element.order_ver != row) {
                row = element.order_ver;

                if (buttons_row)
                    content_block.append(buttons_row);

                buttons_row = $$('<p class="buttons-row"></p>');
            }

            var anchor = $$('<a href="#" class="button-control button button-raised button-fill"></a>');
            anchor.addClass(element.color);
            anchor.attr('data-btn-id', element.identificator);
            anchor.text(element.name);
            anchor.on('click', function (e) {
                var data = $$(this).dataset();
                data.rcId = $$(this).closest('.page').attr('data-rc-id');
                sendIrCommand(data);
            });

            buttons_row.append(anchor);
        });

        content_block.append(buttons_row);
        button_area.append(content_block);
        myApp.hideIndicator();
    }
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
        runCallback(response.callback, response);
        

        if (response.callback == 'refresh_remote_buttons') {
            refreshRemoteButtons(response.buttons, response.rc_name);
        } else if (response.callback == 'back_to_remote') {
            mainView.router.load({
                url: 'static/ir_remote.html',
                context: {
                    title: response.rc_name,
                    rc_id: response.rc_id
                }
            });
            // redirectTo('status');
            // refreshRemoteButtons(response.buttons);
        } else if (response.callback == 'ir_signal_recived') {
            var rc_id = $$('div.page[data-page=ir_remote]').attr('data-rc-id');
            var rc_name = $$('div.page[data-page=ir_remote]').attr('data-rc-name');
            myApp.hidePreloader();

            mainView.router.load({
                url: 'static/add_ir_button.html',
                context: {
                    signal: response.signal,
                    rc_id: rc_id,
                    rc_name: rc_name
                }
            });
        } else if (response.callback == 'ir_signal_failed') {
            myApp.hidePreloader();
            myApp.addNotification({
                message: 'Signal didn\'t recive',
                hold: 3000
            });
        }

        return;
    }
    else if (response.result == 'error') {
        myApp.addNotification({
            message: response.message,
            hold: 3000
        });
        
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

function loadRemoteControl(data) {
    if (data.type == 'ir_rc') {

        mainView.router.load({
            url: 'static/ir_remote.html',
            reload: (mainView.url == 'static/ir_remote.html'),
            ignoreCache: true,
            context: {
                title: data.title,
                rc_id: data.id
            }
        });
    }
}

function sendIrCommand(data) {
    console.log(data);
    var request = {};

    request.action = 'send_ir_command';
    request.content = {}
    request.content.rc_id = data.rcId;
    request.content.btn_id = data.btnId;
    sendRequest(request, socket_remotes);
}

function runCallback(calback, args = '') {
    if (calback) {
        var func = callbacks[calback];
    
        if (typeof func === "function") { 
            func(args);
        }
    }
}

/**
 * Custom callbacks
 */
var callbacks = {
    rc_saved: function() {
        var request = {};

        request.action = 'refresh_rc_list';
        sendRequest(request, socket_remotes);
        myApp.hideIndicator();
        redirectTo('status');
    },
    refresh_rc_list: function(response) {
        console.log(response);
        refreshRemoteMenu(response.remotes);
    }
};

