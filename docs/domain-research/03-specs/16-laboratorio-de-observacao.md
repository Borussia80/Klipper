# Spec 16 — Laboratório de observação

**Status:** rascunho. **Origem:** pesquisa de comportamento para alimentar o backlog.
**Onde mora:** `docs/domain-research/06-registro-pi.md` (origem e observação) e o backlog (decisão de produto).

## Regras

1. **W-1.** O laboratório observa apps cuja licença não permite copiar código somente como **caixa-preta**: executa o
   app e registra comportamento; não abre nem procura o código-fonte.
2. **W-2.** A execução ocorre em container isolado, com Podman, sem internet ou somente com `localhost` quando isto
   for indispensável ao app observado.
3. **W-3.** A observação usa apenas dados fictícios. Dados reais nunca entram no app observado, em capturas, notas ou
   no repositório.
4. **W-4.** Cada achado é escrito como `entrada → saída observada`, em palavras próprias e sem reproduzir textos de
   terceiros.
5. **W-5.** Quem observa não implementa o comportamento observado. O documento de comportamento é a única ponte
   para quem implementa: princípio clean-room.
6. **W-6.** Todo comportamento aproveitado no backlog registra a origem e o método de observação no registro de PI.
7. **W-7.** Não entram no repositório código-fonte, testes, pseudocódigo, estrutura interna, telas copiadas, capturas
   que reproduzam tela, nem textos de terceiros.
8. **W-8.** Código sem licença explícita é tratado como “todos os direitos reservados”. Termos de uso de apps
   proprietários também podem proibir engenharia reversa; a observação só prossegue após verificá-los.
9. **W-9.** Isto não é aconselhamento jurídico. A política e cada uso devem ser revistos se o Klipper for
   comercializado.
10. **W-10.** Cashew (GPLv3), Firefly III, Sure e hledger são referências copyleft conhecidas. Ler para entender
    comportamento é diferente de copiar; nada deles é copiado para o Klipper, conforme a política de terceiros.
11. **W-11.** Uma observação não vira requisito automaticamente: o backlog precisa registrar a decisão e a fonte;
    ausência de evidência mantém o assunto como pergunta aberta.

## Ficha de observação

```text
Identificador e data:
App e versão, se exibida:
Licença/termos consultados:
Ambiente isolado e conectividade:
Dados fictícios usados:
Entrada:
Saída observada (palavras próprias):
Variação/caso-limite observado:
Origem no registro-pi:
Decisão para o backlog ou pergunta aberta:
```

## Critérios de pronto

- Container isolado, conectividade e uso de dados fictícios foram registrados.
- A ficha descreve ao menos uma relação entrada → saída em palavras próprias.
- A origem está no `registro-pi`; não há material de terceiros no repositório.
- A pessoa que implementará recebeu só a ficha de comportamento, não o app nem seu código.

## Perguntas abertas

- Quais termos de uso permitem a observação caixa-preta em cada app proprietário candidato?
- Qual revisão jurídica será necessária antes de qualquer comercialização do Klipper?
