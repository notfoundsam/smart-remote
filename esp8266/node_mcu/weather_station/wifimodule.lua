do
  local M = {}

  local scfg = {}
  scfg.auto = true
  scfg.save = true
  scfg.ssid = 'your-ap-name'
  scfg.pwd = 'your-ap-password'

  wifi.setmode(wifi.STATION)
  wifi.sta.config(scfg)

  function M.isConnected()
    return wifi.sta.status() == wifi.STA_GOTIP
  end

  return M
end
