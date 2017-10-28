myApp.onPageInit('add_ir_button', function (page) {
    $$('#add_remote_button_btn').on('click', function () {
        var request = {};
        var page = $$(this).closest('.page-content');

        request.action = 'remote_ir_btn_add';
        request.content = {}
        request.content.rc_id = page.find('input[name=rc_id]').val();
        request.content.rc_name = page.find('input[name=rc_name]').val();
        request.content.btn_name = page.find('input[name=btn_name]').val();
        request.content.btn_order_ver = page.find('input[name=btn_order_ver]').val();
        request.content.btn_order_hor = page.find('input[name=btn_order_hor]').val();
        request.content.btn_color = page.find('select[name=btn_color]').val();
        request.content.signal = page.find('#recived_signal').text();

        sendRequest(request, socket_remotes);
        myApp.showIndicator();
    });

    $$('#ir_test_signal_btn').on('click', function () {
        var request = {};
        var page = $$(this).closest('.page-content');

        request.action = 'ir_test_signal';
        request.content = {}
        request.content.signal = page.find('#recived_signal').text();

        console.log(request);

        sendRequest(request, socket_remotes);
        // myApp.showIndicator();
    });
});
