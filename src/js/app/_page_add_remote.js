myApp.onPageInit('add_remote', function (page) {
    $$('#add_remote_btn').on('click', function () {
        var request = {};
        var page = $$(this).closest('.page-content');

        request.action = 'add_remote';
        request.content = {}
        request.content.rc_type = page.find('select[name=rc_type]').val();
        request.content.rc_id = page.find('input[name=rc_id]').val();
        request.content.rc_name = page.find('input[name=rc_name]').val();
        sendRequest(request, socket_remotes);
    });
});
