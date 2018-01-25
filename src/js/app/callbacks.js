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
        var rc_id = $$('div.page[data-page=rc_buttons]').attr('data-rc-id');
        var rc_name = $$('div.page[data-page=rc_buttons]').attr('data-rc-name');
        myApp.hidePreloader();

        mainView.router.load({
            url: 'static/rc_button_save.html',
            context: {
                signal: response.signal,
                rc_id: rc_id,
                rc_name: rc_name,
                rc_button_type: 'ir'
            }
        });
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
    }
};
