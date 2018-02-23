myApp.onPageInit('radio_create', function (page) {
    $$('#radio_save_btn').on('click', function () {
        var request = {};
        var page = $$(this).closest('.page-content');

        request.action = 'radio_save';
        request.content = {}
        request.content.radio_name = page.find('input[name=radio_name]').val();
        request.content.radio_battery = page.find('input[name=radio_battery]:checked') ? 1 : 0;
        request.content.radio_dht = page.find('input[name=radio_dht]:checked') ? 1 : 0;
        
        sendRequest(request, socket_radios);
        redirectTo('status');
    });
});
