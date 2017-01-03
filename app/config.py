# List of avalible devices
devices = [
    {
        'name': u'TV',
        'url': u'tv.html'
    },
    {
        'name': u'Light',
        'url': u'light.html'
    },
    {
        'name': u'Air Condition',
        'url': u'ac.html'
    }
]

device_commands = {
    'tv': ['power', 'hdmi', 'vup', 'mute', 'vdown'],
    'ac': ['heat', 'dry', 'cool']
}

# List of responce codes
status_code = {
    'login_success' : 10,
    'alredy_logedin': 20,
    'login_faild'   : 30,
    'logout'        : 40,
    'failed'        : 90,
    'success'       : 100,
}
