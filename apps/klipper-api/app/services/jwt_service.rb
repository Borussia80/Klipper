class JwtService
  SECRET = Rails.application.secret_key_base
  ALGORITHM = "HS256"
  ACCESS_EXPIRY = 15.minutes
  REFRESH_EXPIRY = 30.days

  def self.encode(payload = {}, expires_in: ACCESS_EXPIRY, token_type: "access", **claims)
    payload = payload.merge(claims).merge(token_type: token_type, exp: expires_in.from_now.to_i)
    JWT.encode(payload, SECRET, ALGORITHM)
  end

  def self.encode_refresh(payload)
    encode(payload, expires_in: REFRESH_EXPIRY, token_type: "refresh")
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
