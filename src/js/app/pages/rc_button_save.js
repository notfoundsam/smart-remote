myApp.onPageInit('rc_button_save', function (page) {
    $$('#rc_button_save_btn').on('click', function () {
        var request = {};
        var page = $$(this).closest('.page-content');
        var radio_id = page.find('select[name=btn_radio_id]').val()

        request.action = 'rc_button_save';
        request.content = {}
        request.content.rc_id = page.find('input[name=rc_id]').val();
        request.content.rc_name = page.find('input[name=rc_name]').val();
        request.content.btn_id = page.find('input[name=btn_id]').val();
        request.content.btn_type = page.find('input[name=btn_type]:checked').val();
        request.content.btn_name = page.find('input[name=btn_name]').val();
        request.content.btn_order_ver = page.find('input[name=btn_order_ver]').val();
        request.content.btn_order_hor = page.find('input[name=btn_order_hor]').val();
        request.content.btn_color = page.find('select[name=btn_color]').val();
        request.content.btn_radio_id = radio_id ? radio_id : 0;
        request.content.btn_signal = page.find('#btn_signal').text();

        myApp.showIndicator();
        sendRequest(request, socket_remotes);
    });

    $$('#test_signal_btn').on('click', function () {
        var request = {};
        var page = $$(this).closest('.page-content');

        request.action = 'test_signal';
        request.content = {}
        request.content.btn_radio_id = page.find('input[name=test_radio_id]:checked').val();
        request.content.btn_signal = page.find('#btn_signal').text();

        sendRequest(request, socket_remotes);
    });
});
