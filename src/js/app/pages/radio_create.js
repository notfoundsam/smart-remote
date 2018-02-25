myApp.onPageInit('radio_create', function (page) {
    $$('#radio_save_btn').on('click', function () {
        var request = {};
        var page = $$(this).closest('.page-content');

        request.action = 'radio_save';
        request.content = {}
        request.content.radio = page.find('input[name=radio]').val();
        request.content.radio_name = page.find('input[name=radio_name]').val();
        request.content.radio_id = page.find('input[name=radio_id]').val();
        request.content.radio_order = page.find('input[name=radio_order]').val();
        request.content.radio_battery = page.find('input[name=radio_battery]:checked').val() ? 1 : 0;
        request.content.radio_dht = page.find('input[name=radio_dht]:checked').val() ? 1 : 0;
        
        sendRequest(request, socket_radios);
        redirectTo('status');
    });
});
