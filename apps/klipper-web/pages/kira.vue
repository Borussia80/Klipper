<template>
  <div class="kira-shell">
    <!-- Header -->
    <div class="kira-header">
      <div style="display:flex;align-items:center;gap:10px">
        <div class="kira-avatar" aria-hidden="true">
          <svg width="16" height="16" viewBox="0 0 15 15" fill="none">
            <circle cx="7.5" cy="7.5" r="1.5" fill="currentColor"/>
            <path d="M7.5 2.5v1.5M7.5 11v1.5M2.5 7.5H4M11 7.5h1.5M4.2 4.2l1.1 1.1M9.7 9.7l1.1 1.1M9.7 4.2l-1.1 1.1M4.2 9.7l1.1 1.1" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
          </svg>
        </div>
        <div>
          <div style="font-size:14px;font-weight:600;color:var(--t1);letter-spacing:-.015em">Kira</div>
          <div style="font-size:11px;color:var(--t3)">Assistente financeiro pessoal</div>
        </div>
        <span style="margin-left:8px;font-size:9px;background:var(--bdm);color:var(--blue);border-radius:4px;padding:1px 5px;font-weight:600" aria-label="Versão beta">BETA</span>
      </div>
      <button class="btn btn-g" style="font-size:11px" @click="clearChat">Limpar</button>
    </div>

    <!-- Messages area -->
    <div ref="messagesRef" class="kira-messages" aria-live="polite" aria-label="Conversa com Kira">
      <!-- Empty state -->
      <div v-if="messages.length === 0" class="kira-empty">
        <div class="kira-avatar kira-avatar-lg" aria-hidden="true">
          <svg width="24" height="24" viewBox="0 0 15 15" fill="none">
            <circle cx="7.5" cy="7.5" r="1.5" fill="currentColor"/>
            <path d="M7.5 2.5v1.5M7.5 11v1.5M2.5 7.5H4M11 7.5h1.5M4.2 4.2l1.1 1.1M9.7 9.7l1.1 1.1M9.7 4.2l-1.1 1.1M4.2 9.7l1.1 1.1" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
          </svg>
        </div>
        <p style="font-size:14px;font-weight:500;color:var(--t1);margin-bottom:6px">Olá! Sou a Kira.</p>
        <p style="font-size:12px;color:var(--t3);text-align:center;max-width:280px;line-height:1.5">
          Posso ajudar com análises do seu patrimônio, dúvidas sobre orçamento e decisões financeiras.
        </p>
        <!-- Suggestion chips -->
        <div class="chip-grid">
          <button
            v-for="s in suggestions"
            :key="s"
            class="chip"
            @click="sendMessage(s)"
          >{{ s }}</button>
        </div>
      </div>

      <!-- Chat messages -->
      <template v-else>
        <div
          v-for="(msg, i) in messages"
          :key="i"
          class="msg-row"
          :class="msg.role"
        >
          <div v-if="msg.role === 'assistant'" class="kira-avatar kira-avatar-sm" aria-hidden="true">
            <svg width="12" height="12" viewBox="0 0 15 15" fill="none">
              <circle cx="7.5" cy="7.5" r="1.5" fill="currentColor"/>
              <path d="M7.5 2.5v1.5M7.5 11v1.5M2.5 7.5H4M11 7.5h1.5M4.2 4.2l1.1 1.1M9.7 9.7l1.1 1.1M9.7 4.2l-1.1 1.1M4.2 9.7l1.1 1.1" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="msg-bubble" :class="msg.role">{{ msg.content }}</div>
        </div>

        <!-- Typing indicator -->
        <div v-if="isLoading" class="msg-row assistant">
          <div class="kira-avatar kira-avatar-sm" aria-hidden="true">
            <svg width="12" height="12" viewBox="0 0 15 15" fill="none">
              <circle cx="7.5" cy="7.5" r="1.5" fill="currentColor"/>
              <path d="M7.5 2.5v1.5M7.5 11v1.5M2.5 7.5H4M11 7.5h1.5M4.2 4.2l1.1 1.1M9.7 9.7l1.1 1.1M9.7 4.2l-1.1 1.1M4.2 9.7l1.1 1.1" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="msg-bubble assistant typing" aria-label="Kira está digitando">
            <span class="dot" /><span class="dot" /><span class="dot" />
          </div>
        </div>
      </template>
    </div>

    <!-- Input area -->
    <div class="kira-input-area">
      <textarea
        ref="inputRef"
        v-model="draft"
        class="kira-input"
        placeholder="Pergunte sobre seu patrimônio, orçamento ou investimentos…"
        rows="1"
        aria-label="Mensagem para Kira"
        :disabled="isLoading"
        @keydown.enter.exact.prevent="handleSend"
        @input="autoResize"
      />
      <button
        class="send-btn"
        :disabled="!draft.trim() || isLoading"
        aria-label="Enviar mensagem"
        @click="handleSend"
      >
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
          <path d="M12 7L2 2l2.5 5L2 12l10-5z" fill="currentColor"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app' })

const { apiFetch } = useApi()
const { addToast } = useToast()

interface Message {
  role: 'user' | 'assistant'
  content: string
}

const messages = ref<Message[]>([])
const draft = ref('')
const isLoading = ref(false)
const messagesRef = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLTextAreaElement | null>(null)

const suggestions = [
  'Qual é meu saldo atual?',
  'Onde gastei mais este mês?',
  'Quanto tenho em investimentos?',
  'Estou dentro do orçamento?',
]

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

function autoResize(e: Event) {
  const el = e.target as HTMLTextAreaElement
  el.style.height = 'auto'
  el.style.height = `${Math.min(el.scrollHeight, 120)}px`
}

function clearChat() {
  messages.value = []
  draft.value = ''
}

async function sendMessage(text: string) {
  const content = text.trim()
  if (!content || isLoading.value) return

  messages.value.push({ role: 'user', content })
  draft.value = ''
  if (inputRef.value) {
    inputRef.value.style.height = 'auto'
  }
  isLoading.value = true
  scrollToBottom()

  try {
    const response = await apiFetch<{ reply: string }>('/api/v1/kira/chat', {
      method: 'POST',
      body: { message: content },
    })
    messages.value.push({ role: 'assistant', content: response.reply })
  } catch (err: unknown) {
    const isNotFound = err && typeof err === 'object' && 'status' in err && (err as { status: number }).status === 404
    const reply = isNotFound
      ? 'A integração com Kira ainda não foi ativada neste ambiente. Fique de olho nas próximas atualizações!'
      : 'Não consegui processar sua pergunta agora. Tente novamente em breve.'
    messages.value.push({ role: 'assistant', content: reply })
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

function handleSend() {
  sendMessage(draft.value)
}

watch(messages, scrollToBottom)
</script>

<style scoped>
.kira-shell {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.kira-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  border-bottom: 1px solid var(--bd);
  background: rgba(7,18,30,0.92);
  backdrop-filter: blur(8px);
  flex-shrink: 0;
}

.kira-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: color-mix(in srgb, var(--blue) 15%, var(--sf));
  border: 1px solid color-mix(in srgb, var(--blue) 30%, transparent);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--blue);
  flex-shrink: 0;
}

.kira-avatar-lg {
  width: 52px;
  height: 52px;
  margin-bottom: 12px;
}

.kira-avatar-sm {
  width: 24px;
  height: 24px;
  margin-top: 4px;
}

.kira-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.kira-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.chip-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-top: 20px;
}

.chip {
  font-size: 12px;
  padding: 6px 14px;
  border-radius: 20px;
  border: 1px solid var(--bd2);
  background: var(--sf);
  color: var(--t2);
  cursor: pointer;
  transition: background .12s, border-color .12s;
}

.chip:hover {
  border-color: var(--blue);
  background: color-mix(in srgb, var(--blue) 6%, var(--sf));
  color: var(--t1);
}

.msg-row {
  display: flex;
  gap: 8px;
  align-items: flex-start;
}

.msg-row.user {
  flex-direction: row-reverse;
}

.msg-bubble {
  max-width: 75%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.msg-bubble.user {
  background: var(--blue);
  color: #fff;
  border-bottom-right-radius: 4px;
}

.msg-bubble.assistant {
  background: var(--sf);
  border: 1px solid var(--bd2);
  color: var(--t1);
  border-bottom-left-radius: 4px;
}

.msg-bubble.typing {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 12px 16px;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--t3);
  animation: dot-bounce 1.2s ease infinite;
}

.dot:nth-child(2) { animation-delay: .2s; }
.dot:nth-child(3) { animation-delay: .4s; }

@keyframes dot-bounce {
  0%, 80%, 100% { transform: translateY(0); }
  40%            { transform: translateY(-5px); }
}

.kira-input-area {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  padding: 12px 20px;
  border-top: 1px solid var(--bd);
  background: var(--bg-frame);
  flex-shrink: 0;
}

.kira-input {
  flex: 1;
  background: var(--sf);
  border: 1px solid var(--bd2);
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 13px;
  color: var(--t1);
  font-family: inherit;
  outline: none;
  resize: none;
  line-height: 1.5;
  transition: border-color .12s;
  max-height: 120px;
}

.kira-input:focus {
  border-color: var(--blue);
}

.kira-input::placeholder {
  color: var(--t4);
}

.send-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--blue);
  color: #fff;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: opacity .12s;
}

.send-btn:disabled {
  opacity: 0.35;
  cursor: default;
}

.send-btn:not(:disabled):hover {
  opacity: 0.85;
}
</style>
