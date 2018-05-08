myApp.on('pageInit', function (page) {
    if (page == 'rc_button_list') {
        $$('#rc_buttons_remove_btn').on('click', function () {
            var request = {};
            var buttons = [];
            var page = $$(this).closest('.page-content');

            request.action = 'rc_buttons_remove';
            request.content = {}
            request.content.rc_id = page.find('input[name=rc_id]').val();
            request.content.rc_name = page.find('input[name=rc_name]').val();
            
            page.find('input[name=button]:checked').each(function() {
                buttons.push($$(this).val());
            });

            request.content.buttons = buttons;

            sendRequest(request, socket_remotes);
            myApp.showIndicator();
        });

        $$('#rc_button_edit_btn').on('click', function () {
            var request = {};
            var page = $$(this).closest('.page-content');
            var button = page.find('input[name=button]:checked').val();

            if (!button)
                return;

            request.action = 'rc_button_edit';
            request.content = {}
            request.content.rc_id = page.find('input[name=rc_id]').val();
            request.content.rc_name = page.find('input[name=rc_name]').val();
            request.content.button = button;

            sendRequest(request, socket_remotes);
            myApp.showIndicator();
        });
    }
});
