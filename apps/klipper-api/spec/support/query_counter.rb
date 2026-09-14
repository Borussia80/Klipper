# Conta as queries SQL disparadas dentro do bloco. Existe para que "este
# endpoint não faz N+1" seja uma asserção verificável, e não uma leitura de
# código: N+1 não quebra teste nenhum — só fica mais lento conforme o dado
# cresce, que é justamente quando ninguém está olhando.
#
# SCHEMA/TRANSACTION são ruído do próprio RSpec (SAVEPOINT por exemplo), não
# trabalho do endpoint, então ficam de fora da conta.
module QueryCounter
  IGNORED = /\A\s*(BEGIN|COMMIT|ROLLBACK|SAVEPOINT|RELEASE SAVEPOINT)/i

  def count_queries
    queries = []
    subscriber = ActiveSupport::Notifications.subscribe("sql.active_record") do |*, payload|
      next if payload[:name] == "SCHEMA" || payload[:cached]
      next if payload[:sql].match?(IGNORED)
      queries << payload[:sql]
    end
    yield
    queries
  ensure
    ActiveSupport::Notifications.unsubscribe(subscriber) if subscriber
  end
end

RSpec.configure do |config|
  config.include QueryCounter
end
