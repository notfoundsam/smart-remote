/**
 * Custom callbacks
 */
var callbacks = {
    rc_buttons_refresh: function(response) {
        var buttons = response.buttons;
        var page = $$('div.page[data-page=rc_buttons]');

        if (page.length && buttons.length) {
            var button_area = $$('#buttons_area');

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

                var anchor = $$('<a href="#" class="button button-raised button-fill"></a>');
                anchor.addClass(element.color);
                anchor.attr('data-btn-id', element.identificator);
                anchor.text(element.name);
                anchor.on('click', function (e) {
                    var data = $$(this).dataset();
                    var request = {};

                    request.action = 'rc_button_pushed';
                    request.content = {}
                    request.content.btn_id = data.btnId;
                    sendRequest(request, socket_remotes);
                });

                buttons_row.append(anchor);
            });

            content_block.append(buttons_row);
            button_area.append(content_block);
        }
        myApp.hideIndicator();
    },
    rc_refresh: function(response) {
        var remotes = response.remotes;
        var menu = $$('#remotes ul');
        menu.empty();

        remotes.forEach(function(element) {
            var li = $$('<li>');
            var anchor = $$('<a href="#" class="item-link item-content close-panel"></a>');
            var icon = $$('<div class="item-media"><i class="' + element.icon + ' size-25" aria-hidden="true"></i></div>');
            var inner = $$('<div class="item-inner"></div>');
            var title = $$('<div class="item-title"></div>').text(element.name);

            anchor.attr('data-id', element.identificator);
            anchor.attr('data-title', element.name);

            anchor.on('click', function (e) {
                var data = $$(this).dataset();
                mainView.router.load({
                    url: 'static/rc_buttons.html',
                    reload: (mainView.url == 'static/rc_buttons.html'),
                    ignoreCache: true,
                    context: {
                        title: data.title,
                        rc_id: data.id
                    }
                });
            });

            inner.append(title);
            anchor.append(icon);
            anchor.append(inner);
            li.append(anchor);
            menu.append(li);
        });
    },
    rc_button_save: function(response) {
        if (response.edit) {
            myApp.hideIndicator();

            response.radios.forEach(function(el) {
                if (response.button.btn_radio_id == el.id)
                    el.btn_selected = true;
            });

            mainView.router.load({
                url: 'static/rc_button_save.html',
                context: {
                    button: response.button,
                    radios: response.radios
                }
            });
        } else {
            myApp.hidePreloader();

            var rc_id = $$('div.page[data-page=rc_buttons]').attr('data-rc-id');
            var rc_name = $$('div.page[data-page=rc_buttons]').attr('data-rc-name');

            mainView.router.load({
                url: 'static/rc_button_save.html',
                context: {
                    button: {
                        rc_id: rc_id,
                        rc_name: rc_name,
                        btn_signal: response.signal,
                        btn_type: 'ir',
                        btn_radio: 999
                    },
                    radios: response.radios,
                    select: true
                }
            });
        }
    },
    back_to_remote: function(response) {
        mainView.router.load({
            url: 'static/rc_buttons.html',
            context: {
                title: response.rc_name,
                rc_id: response.rc_id
            }
        });
    },
    catch_failed: function(response) {
        myApp.hidePreloader();
        myApp.addNotification({
            message: 'Signal didn\'t recive',
            hold: 3000
        });
    },
    radios_refresh: function(response) {
        var radios = response.radios;
        var page = $$('div.page[data-page=status]');

        if (page.length && radios.length) {
            var radios_area = $$('#radios_area');
            radios_area.empty();

            radios.forEach(function(element) {
                var card = $$('<div class="card"></div>');
                var card_header = $$('<div class="card-header"></div>');
                var card_content = $$('<div class="card-content"></div>');
                var card_content_inner = $$('<div class="card-content-inner row"></div>');
                
                card_header.append($$('<div></div>').text(element.name));

                if (element.battery) {
                    card_header.append($$('<div><i class="fa fa-battery-full" aria-hidden="true"></i></div>'));
                }
                if (element.dht) {
                    card_content_inner.append($$('<div class="col-50"><i class="fa fa-thermometer-half" aria-hidden="true"></i> Temperature: --&#8451;</div>'));
                    card_content_inner.append($$('<div class="col-50"><i class="fa fa-tint" aria-hidden="true"></i> Humidity: --%</div>'));
                }

                card_content.append(card_content_inner);
                card.append(card_header);
                card.append(card_content);
                radios_area.append(card);
            });
        }
    },
};
