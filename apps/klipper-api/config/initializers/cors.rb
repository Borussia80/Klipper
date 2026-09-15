Rails.application.config.middleware.insert_before 0, Rack::Cors do
  allow do
    origins ENV.fetch("CORS_ORIGINS", "http://localhost:3001").split(",")

    resource "*",
      credentials: true,
      headers: :any,
      methods: [ :get, :post, :put, :patch, :delete, :options, :head ],
      # Header de resposta fora desta lista é invisível ao JavaScript do
      # navegador: a API responderia certo e o cliente leria `null`.
      expose: [ "Authorization", "X-Per-Page", "X-Next-Cursor" ]
  end
end
