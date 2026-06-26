class JwtService
  SECRET = Rails.application.secret_key_base
  ALGORITHM = "HS256"
  EXPIRY = 30.days

  def self.encode(payload)
    payload[:exp] = EXPIRY.from_now.to_i
    JWT.encode(payload, SECRET, ALGORITHM)
  end

  def self.decode(token)
    return nil if token.blank?
    body = JWT.decode(token, SECRET, true, algorithm: ALGORITHM).first
    HashWithIndifferentAccess.new(body)
  rescue JWT::ExpiredSignature
    nil
  rescue JWT::DecodeError
    nil
  end
end
