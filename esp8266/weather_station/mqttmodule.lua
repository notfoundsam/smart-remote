do
  local M = {}

  M.connected = false
  M.server_ip = "192.168.100.50"
  M.server_port = 1883
  M.server_channel = "/weather"
  M.device_id = "station_outside"

  local client = mqtt.Client(M.device_id, 60)
  client:lwt('/offline', M.device_id)

  client:on("offline", function(con)
    M.connected = false
    print("disconnected")
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

  function M.publishBattery(message)
    client:publish("/battery", '['..message..',{"id":"'..M.device_id..'"}]', 0, 0)
  end

  return M
end
