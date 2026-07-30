class Rack::Attack
  # Throttle sign_in/sign_up attempts by IP: at most 20 requests per minute.
  throttle("auth/ip", limit: 20, period: 1.minute) do |req|
    req.ip if req.post? && %w[/api/v1/auth/sign_in /api/v1/auth/sign_up].include?(req.path)
  end

  # Throttle sign_in attempts by e-mail: at most 5 per minute, regardless of IP,
  # to stop credential stuffing against a single account from many addresses.
  #
  # The API only accepts JSON bodies, which plain Rack doesn't parse into
  # req.params, so the body is read and rewound here for the Rails app
  # further down the middleware stack to still read it in full.
  throttle("auth/sign_in/email", limit: 5, period: 1.minute) do |req|
    if req.post? && req.path == "/api/v1/auth/sign_in"
      begin
        body = req.body.read
        req.body.rewind
        JSON.parse(body)["email"].to_s.downcase.presence
      rescue JSON::ParserError
        nil
      end
    end
  end

  self.throttled_responder = lambda do |_request|
    [429, { "Content-Type" => "application/json" }, [ { error: "Muitas tentativas. Tente novamente em instantes." }.to_json ]]
  end
end

Rails.application.config.middleware.use(Rack::Attack)
