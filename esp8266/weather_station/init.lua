local dht_pin = 4
local vin_ratio = 0.0995

adc.force_init_mode(adc.INIT_ADC)

local w = require('wifimodule')
local m = require('mqttmodule')

tmr.create():alarm(5000, tmr.ALARM_AUTO, function(t)
  if w.isConnected() and m.connected then
    dht22()
    battery()
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

function battery()
  input = adc.read(0)
  
  vin = ((input * 3.3) / 1023) / vin_ratio
  m.publishBattery('{"batValue":'..vin..'}')
end
