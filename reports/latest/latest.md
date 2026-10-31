# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `7736c2d89e167ba321da17841ca890f49a3b6506` · **Modo:** fast

> ⚠️ **Relatório incompleto.** A análise de **finance** não produziu resultado neste run. O que segue abaixo cobre só 2 das 3 seções esperadas — ausência de finding numa área não avaliada não significa ausência de problema.

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Segurança | low |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-011 | 🟠 high | architecture | 112 | useModal (roteamento de todo modal financeiro do app) e useToast (todo feedback ao usuário) continuam sem nenhum teste direto — open()/close()/reset de payload e o auto-dismiss via setTimeout só são exercitados incidentalmente através de mocks em testes de componentes individuais. Nenhuma mudança desde a última auditoria. |
| ARCH-009 | 🟡 medium | architecture | 56 | O componente-base compartilhado por todos os modais do app (Escape para fechar, focus trap e restauração de foco ao gatilho) continua sem nenhuma cobertura de teste, direta ou indireta. Nenhuma mudança desde a última auditoria. |
| ARCH-005 | 🟡 medium | architecture | 36 | Duas das quatro páginas centrais do Wealth OS foram corrigidas desde a última auditoria (dashboard, orçamento). Contas e Portadores continuam sem teste de página, e a nova rota dinâmica contas/[id].vue foi adicionada ao projeto sem nenhum teste de página. |
| ARCH-004 | 🟡 medium | architecture | 33.33 | Um dos quatro componentes apontados na última auditoria (ModalNovaConta) já tem teste de montagem. ModalNovoMembro, ModalEditarReembolso e ModalMount — este último o componente que decide qual modal financeiro renderizar via activeModal — continuam sem nenhuma cobertura direta ou indireta. |
| ARCH-013 | 🟡 medium | architecture | 22.5 | A lógica de sinal buy/sell (documentada no próprio arquivo como causa do bug real FIN-002 quando duplicada) tem uma terceira reimplementação não coberta pelo teste de paridade existente entre signed_cost e signed_cost_sql, então uma mudança na regra de sinal pode divergir silenciosamente na validação de venda sem que o teste de paridade acuse. Nenhuma mudança desde a última auditoria. |
| SEC-003 | 🟢 low | security | 18 | Nuxt (dependência direta de ambos os frontends) e um pequeno grupo de dependências de build seguem desatualizados com avisos moderate/low conhecidos (patch disponível: nuxt 4.6.3); o gate de CI aceita corretamente essa faixa por desenho, mas a dívida de atualização persiste, e o lado Ruby (Gemfile.lock) continua sem poder ser auditado neste ambiente por falta de bundler instalado. |
| ARCH-008 | 🟡 medium | architecture | 9.6 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm, mas o template de apresentação e o CSS scoped inteiro continuam duplicados quase byte a byte entre os dois arquivos. Nenhuma mudança desde a última auditoria. |
| ARCH-014 | 🟡 medium | architecture | 9 | O padrão visual de campo com select (label, wrapper, seta customizada) continua reimplementado em CSS scoped duplicado em pelo menos três modais de entidade diferentes dos de lançamento, então qualquer ajuste visual (ex: acessibilidade do caret, espaçamento) precisa ser replicado manualmente em cada arquivo e tende a divergir. Nenhuma mudança desde a última auditoria. |
| ARCH-016 | 🟢 low | architecture | 8 | A regra que decide o status de AuditLog de uma importação (sucesso parcial conta como sucesso) está duplicada verbatim entre as actions create e confirm de ImportsController em vez de viver num método privado único. |
| ARCH-015 | 🟢 low | architecture | 6 | A regra 'occurred_on não pode ser futuro' continua duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado, apesar de o diretório de concerns já existir no projeto para esse propósito. Nenhuma mudança desde a última auditoria. |
| ARCH-017 | 🟢 low | architecture | 6 | O identificador 'editar-categoria' sugere um editor completo da categoria (nome, tipo, etc.), mas na prática abre um modal que só edita o vínculo de reembolso (ModalEditarReembolso) — um nome que esconde a intenção real do fluxo e pode levar quem lê o código a procurar uma funcionalidade de edição de categoria que não existe nesse modal. |
| SEC-005 | 🟢 low | security | 6 | PATCH /api/v1/password_resets/:token (redenção do token de reset de senha) continua sem qualquer rate limiting, ao contrário de todas as outras rotas de autenticação não-autenticadas (sign_in, sign_up e o pedido de reset em POST /password_resets, essas três cobertas por rack_attack.rb:3-5). |
