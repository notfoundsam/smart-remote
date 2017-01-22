# List of avalible devices
devices = [
    {
        # 'driver': 'tv',
        'name': u'TV',
        'url': u'tv.html'
    },
    {
        # 'driver': 'led',
        'name': u'Led',
        'url': u'led.html'
    }
    # {
    #     'driver': 'lidht',
    #     'name': u'Light',
    #     'url': u'light.html'
    # }
    # {
    #     'driver': 'ac',
    #     'name': u'Air Condition',
    #     'url': u'ac.html'
    # }
]

devices_drivers = ('tv', 'led', 'therm')

# devices_driver = {
#     'tv': ['power', 'hdmi', 'vup', 'mute', 'vdown'],
#     'ac': ['heat', 'dry', 'cool']
# }

# List of responce codes
status_code = {
    'login_success' : 10,
    'alredy_logedin': 20,
    'login_faild'   : 30,
    'logout'        : 40,
    'failed'        : 90,
    'success'       : 100,
}
