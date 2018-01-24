myApp.onPageInit('rc_buttons_remove', function (page) {
    $$('#rc_buttons_remove_btn').on('click', function () {
        var request = {};
        var buttons = [];
        var page = $$(this).closest('.page-content');

        request.action = 'rc_buttons_remove';
        request.content = {}
        request.content.rc_id = page.find('input[name=rc_id]').val();
        request.content.rc_name = page.find('input[name=rc_name]').val();
        
        page.find('input[name=ir_button]:checked').each(function() {
            buttons.push($$(this).val());
        });

        request.content.buttons = buttons;

        sendRequest(request, socket_remotes);
        myApp.showIndicator();
    });
});
