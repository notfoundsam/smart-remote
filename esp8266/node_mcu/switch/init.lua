local wifi_retries = 25
local mqtt_retries = 5
local push_retries = 10

local w = require('wifimodule')
local m = require('mqttmodule')

tmr.create():alarm(1000, tmr.ALARM_AUTO, function(t)
  if w.isConnected() then

    if not m.connected then
      m.connect()
    end

  else
    -- print('offline...\n')
    wifi_retries = wifi_retries - 1

    if wifi_retries == 0 then
      node.dsleep(1000000, 1)
    end
  end
end)
