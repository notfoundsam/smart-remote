local dht_pin = 4

local w = require('wifimodule')
local m = require('mqttmodule')

tmr.create():alarm(10000, tmr.ALARM_AUTO, function(t)
  if w.isConnected() and m.connected then
    dht22()
  else
    print('offline...\n')
    m.connect()
  end
end)

function dht22()
  status, temp, humi, temp_dec, humi_dec = dht.read(dht_pin)

  if status == dht.OK then
    m.publish('{"tempValue":'..temp..',"humiValue":'..humi..'}')
  elseif status == dht.ERROR_CHECKSUM then
    print( "DHT Checksum error." )
  elseif status == dht.ERROR_TIMEOUT then
    print( "DHT timed out." )
  end
end
