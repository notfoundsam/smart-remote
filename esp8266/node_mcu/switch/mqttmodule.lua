do
  local M = {}
  local pin = 2
  gpio.mode(pin, gpio.INPUT)
  -- gpio.write(pin, gpio.LOW)

  M.connected = false
  M.server_ip = "192.168.100.10"
  M.server_port = 1883
  M.server_channel = "/air_dryer"
  M.device_id = "air_dryer"

  local client = mqtt.Client(M.device_id, 60)
  client:lwt('/offline', M.device_id)

  client:on("offline", function(con)
    M.connected = false
    print("disconnected")
  end)

  client:on("message", function(cli, topic, msg)
    if topic == '/air_dryer' then
      if msg == 'gpio1_on' then
        print('gpio1_on')
        gpio.mode(pin, gpio.OUTPUT)
        gpio.write(pin, gpio.HIGH)
        gpio.write(pin, gpio.LOW)
      elseif msg == 'gpio1_off' then
        print('gpio1_off')
        gpio.mode(pin, gpio.INPUT)
        -- gpio.write(pin, gpio.LOW)
      elseif msg == 'gpio1_pulse' then
        print('gpio1_pulse')
        gpio.mode(pin, gpio.OUTPUT)
        gpio.write(pin, gpio.HIGH)
        gpio.write(pin, gpio.LOW)
      end
    end
  end)

  function M.connect()
    client:connect(M.server_ip, M.server_port, 0, function(cli)
      print("connected")

      cli:subscribe(M.server_channel, 0, function(cli)
        print("subscribe success")
      end)
      M.connected = true
    end,
    function(cli, reason)
      print("failed reason: " .. reason)
    end)
  end

  function M.publish(message)
    client:publish(M.server_channel, '['..message..',{"id":"'..M.device_id..'"}]', 0, 0)
  end

  return M
end
