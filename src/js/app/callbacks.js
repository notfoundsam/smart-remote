/**
 * Custom callbacks
 */
var callbacks = {
    rc_buttons_refresh: function(response) {
        var buttons = response.buttons;
        var page = $$('div.page[data-name=rc]');

        if (page.length && buttons.length) {
            var button_area = $$('#buttons_area');

            var row = 0;

            var content_block = $$('<div class="block"></div>');
            var buttons_row = null;

            buttons.forEach(function(element) {
                if (element.order_ver != row) {
                    row = element.order_ver;

                    if (buttons_row)
                        content_block.append(buttons_row);

                    buttons_row = $$('<p class="row"></p>');
                }

                var button = $$('<button class="col button button-raised button-fill"></button>');
                button.addClass(element.color);
                button.attr('data-btn-id', element.identificator);
                button.text(element.name);
                button.on('click', function (e) {
                    var data = $$(this).dataset();
                    var request = {};

                    request.action = 'rc_button_pushed';
                    request.content = {}
                    request.content.btn_id = data.btnId;
                    sendRequest(request, socket_remotes);
                });

                buttons_row.append(button);
            });

            content_block.append(buttons_row);
            button_area.append(content_block);
        }

        if (response.rc_name) {
            page.find('.navbar .title').text(response.rc_name);
        }

        app.preloader.hide();
    },
    rc_refresh: function(response) {
        var remotes = response.remotes;
        var menu = $$('#remotes ul');
        menu.empty();

        remotes.forEach(function(element) {
            var li = $$('<li>');
            var anchor = $$('<a href="#" class="item-link item-content panel-close" data-ignore-cache="true"></a>');
            var icon = $$('<div class="item-media"><i class="' + element.icon + ' size-25" aria-hidden="true"></i></div>');
            var inner = $$('<div class="item-inner"></div>');
            var title = $$('<div class="item-title"></div>').text(element.name);

            anchor.on('click', function (e) {
                mainView.router.navigate('/rc/' + element.identificator, {
                    reloadCurrent : (mainView.router.currentRoute.name == 'rc'),
                    // ignoreCache: true,
                    // context: {
                    //     title: data.title,
                    //     rc_id: data.id
                    // }
                });
            });

            inner.append(title);
            anchor.append(icon);
            anchor.append(inner);
            li.append(anchor);
            menu.append(li);
        });
    },
    // set_radio_options: function(response) {
    //     var radios = response.radios;
    //     var page = $$('div.page[data-name=button]');
    //     var radio_options = $$('select[name=btn_radio_id]');
    //     var test_radio_list = $$('#test_radio_list ul');
        
    //     if (page.length && radios.length) {
    //         radios.forEach(function(element) {
    //             var option = $$('<option value="' + element.radio_id + '">' + element.name + '</option>');
    //             radio_options.append(option);

    //             var li = $$('<li></li>');
    //             var label = $$('<label class="item-radio item-content"></label>');
    //             var input = $$('<input type="radio" name="test_radio_id" value="' + element.radio_id + '">');
    //             var icon = $$('<i class="icon icon-radio"></i>');
    //             var item_inner = $$('<div class="item-inner"></div>').append($$('<div class="item-title">' + element.name + '</div>'));
                
    //             label.append(input);
    //             label.append(icon);
    //             label.append(item_inner);
    //             li.append(label);
    //             test_radio_list.append(li);
    //         });
    //     }
    // },
    ir_signal: function(response) {
        var page = $$('div.page[data-name=button]');

        if (page.length) {
            app.dialog.close();

            if (response.signal) {
                page.find('input[name=button_signal]').val(response.signal);
                page.find('#ir_signal').text(response.signal);
            } else {
                var notif = app.notification.create({
                    icon: '<i class="fa fa-bell-o" aria-hidden="true"></i>',
                    title: 'Application',
                    titleRightText: 'now',
                    subtitle: 'IR Cacher',
                    text: 'A signal was not recieved',
                    closeTimeout: 3000,
                    closeButton: true,
                });
                notif.open();
            }
        }
    },
    button_edit: function(response) {
        if (response.button) {
            response.radios.forEach(function(el) {
                if (response.button.btn_radio_id == el.radio_id)
                    el.btn_selected = true;
            });
        }

        mainView.router.navigate('/button/', {
            context: {
                button: response.button,
                radios: response.radios
            }
        });

        app.preloader.hide();
    },
    back_to_rc: function(response) {
        app.preloader.hide();
        mainView.router.navigate('/rc/' + response.rc_id);
    },
    radios_refresh: function(response) {
        var radios = response.radios;
        var page = $$('div.page[data-name=radios]');
        var radios_area = $$('#radios_area');
        radios_area.empty();
        
        if (page.length && radios.length) {
            radios.forEach(function(element) {
                var card = $$('<div class="card" id="rid_' + element.id + '"></div>');
                var card_header = $$('<div class="card-header"></div>');
                var card_content = $$('<div class="card-content card-content-padding"></div>');
                var card_content_inner = $$('<div class="row"></div>');
                var card_footer = $$('<div class="card-footer"><a href="#" class="radio-edit-btn" data-id="' + element.id + '"><i class="fa fa-pencil-square-o" aria-hidden="true"></i> Edit</a><a href="#" class="radio-remove-btn" data-id="' + element.id + '"><i class="fa fa-trash-o" aria-hidden="true"></i> Remove</a></div>');
                
                card_header.append($$('<div></div>').text(element.name + ' (radio number: ' + element.pipe + ')'));

                if (element.battery) {
                    card_header.append($$('<div class="sensor-bat"><i class="fa fa-battery-full" aria-hidden="true"></i></div>'));
                }
                if (element.dht) {
                    card_content_inner.append($$('<div class="col-50"><i class="fa fa-thermometer-half" aria-hidden="true"></i> Temperature: <span class="sensor-temp">--</span>&#8451;</div>'));
                    card_content_inner.append($$('<div class="col-50"><i class="fa fa-tint" aria-hidden="true"></i> Humidity: <span class="sensor-hum">--</span>%</div>'));
                }

                card_content.append(card_content_inner);
                card.append(card_header);
                card.append(card_content);
                card.append(card_footer);
                radios_area.append(card);
            });

            $$('.radio-edit-btn').on('click', function () {
                var request = {};

                request.action = 'radio_edit';
                request.content = {}
                request.content.id = $$(this).attr('data-id');
                sendRequest(request, socket_radios);
            });

            $$('.radio-remove-btn').on('click', function () {
                var request = {};

                request.action = 'radio_remove';
                request.content = {}
                request.content.radio = $$(this).attr('data-id');
                sendRequest(request, socket_radios);
            });
        }
    },
    radio_edit: function(response) {
        var radios = response.radios;
        var page = $$('div.page[data-page=status]');

        mainView.router.load({
            url: 'static/radio_create.html',
            context: {
                radio: response.radio
            }
        });
    },
    radio_sensor_refresh: function(response) {
        var rid = response.rid;
        // var sensors = response.sensors;
        var page = $$('div.page[data-name=index]');

        if (page.length) {
            var radio = $$('#rid_' + rid);

            if (response.sensors.temp) {
                radio.find('.sensor-temp').html(response.sensors.temp)
            }
            if (response.sensors.hum) {
                radio.find('.sensor-hum').html(response.sensors.hum)
            }
            if (response.sensors.bat) {
                radio.find('.sensor-bat').html('v' + response.sensors.bat + ' <i class="fa fa-battery-full" aria-hidden="true"></i>')
            }
        }
    },
};
