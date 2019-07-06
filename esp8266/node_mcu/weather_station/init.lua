local dht_pin = 4
local bat_ratio = 10.37

local wifi_retries = 25
local mqtt_retries = 5
local push_retries = 10

adc.force_init_mode(adc.INIT_ADC)

local w = require('wifimodule')
local m = require('mqttmodule')

tmr.create():alarm(300, tmr.ALARM_AUTO, function(t)
  if w.isConnected() then
    tmr.unregister(t)
    m.connect()

    tmr.create():alarm(300, tmr.ALARM_AUTO, function(tw)
      if m.connected then
        tmr.unregister(tw)
        battery()
        dht22()

        tmr.create():alarm(300, tmr.ALARM_AUTO, function(off)
          if m.publish and m.publish_bat then
            node.dsleep(5000000, 1)
          end

          push_retries = push_retries - 1

          if push_retries == 0 then
            node.dsleep(1000000, 1)
          end
        end)
      else
        m.connect()

        mqtt_retries = mqtt_retries - 1

        if mqtt_retries == 0 then
          node.dsleep(1000000, 1)
        end
      end
    end)

  else
    -- print('offline...\n')
    wifi_retries = wifi_retries - 1

    if wifi_retries == 0 then
      node.dsleep(1000000, 1)
    end
  end
end)

function dht22()
  status, temp, humi, temp_dec, humi_dec = dht.read(dht_pin)

  if status == dht.OK then
    -- tmr.unregister(td)
    print( "t"..temp.."\n" )
    print( "h"..humi.."\n" )
    m.publish('{"tempValue":'..temp..',"humiValue":'..humi..'}')
  elseif status == dht.ERROR_CHECKSUM then
    print( "DHT Checksum error." )
  elseif status == dht.ERROR_TIMEOUT then
    print( "DHT timed out." )
  end
end

function battery()
  input = adc.read(0)
  
  bat = (input * 3.04 / 1024) * bat_ratio
  m.publishBattery('{"batValue":'..bat..'}')
end
