myApp.onPageInit('rc_create', function (page) {
    $$('#rc_save_btn').on('click', function () {
        var request = {};
        var page = $$(this).closest('.page-content');

        request.action = 'rc_save';
        request.content = {}
        request.content.rc_icon = page.find('select[name=rc_icon]').val();
        request.content.rc_name = page.find('input[name=rc_name]').val();
        
        sendRequest(request, socket_remotes);
        redirectTo('status');
    });
});
