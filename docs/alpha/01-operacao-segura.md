# Operação segura do alfa financeiro

O alfa D1–D3 aceita lançamentos inseridos manualmente. Importação de extrato,
cartões, financiamento e investimentos não fazem parte desta liberação.

## Pré-requisitos antes de convidar alguém

- Instância privada com HTTPS válido e `CORS_ORIGINS` limitado ao endereço do web.
- `DATABASE_URL`, `SECRET_KEY_BASE`, credenciais SMTP e chaves de terceiros
  definidos exclusivamente no provedor; nunca em `.env` versionado.
- Banco persistente, com disco e backup criptografados.
- Backup diário com retenção mínima de 30 dias e responsável definido.
- Restauração testada em banco isolado: criar conta, lançamento e transferência,
  restaurar o backup e conferir os mesmos saldos e pares de transferência.
- Monitoramento de disponibilidade e alertas de exceção ativados.

## Checagem de liberação

1. Migrar o banco e executar as suítes Rails, Nuxt e typecheck.
2. Criar duas contas, registrar receita, gasto e transferência; conferir saldo
   das duas contas e relatório mensal.
3. Excluir uma transferência, restaurá-la e conferir que as duas pontas voltam.
4. Repetir a jornada em 390 px e só por teclado.
5. Exportar os dados de uma conta de teste e validar que o arquivo contém
   lançamentos e contas esperados.

Não liberar dados pessoais se qualquer item acima falhar. Não há exclusão
permanente de lançamento nesta fase: a ação pode ser restaurada pelo usuário.
