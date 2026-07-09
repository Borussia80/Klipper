<template>
  <div>
    <!-- Sticky header -->
    <div style="position:sticky;top:0;background:rgba(7,18,30,0.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--bd);padding:12px 20px;display:flex;align-items:center;gap:12px;z-index:10">
      <div>
        <div style="font-size:14px;font-weight:600;color:var(--t1);letter-spacing:-.015em">Portadores</div>
        <div style="font-size:11px;color:var(--t3)">{{ members.length }} portadores</div>
      </div>
      <div style="margin-left:auto;display:flex;align-items:center;gap:8px">
        <button class="btn btn-p" @click="open('novo-portador')">
          <svg width="11" height="11" viewBox="0 0 11 11" fill="none">
            <line x1="5.5" y1="1" x2="5.5" y2="10" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
            <line x1="1" y1="5.5" x2="10" y2="5.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
          </svg>
          Novo portador
        </button>
      </div>
    </div>

    <div style="padding:20px 20px 32px">
      <!-- Skeleton while loading -->
      <template v-if="isLoading">
        <UiSkeletonCard v-for="n in 5" :key="n" style="margin-bottom:8px" />
      </template>

      <template v-else>
        <template v-if="titulares.length">
          <div style="font-size:10px;font-weight:600;color:var(--t3);text-transform:uppercase;letter-spacing:.1em;font-family:'JetBrains Mono',monospace;margin-bottom:10px">Titulares</div>
          <div v-for="member in titulares" :key="member.id" class="ac">
            <div class="mem-avatar">{{ initials(member.name) }}</div>
            <div style="flex:1;min-width:0">
              <div style="font-size:13px;font-weight:600;color:var(--t1)">{{ member.name }}</div>
              <div style="font-size:11px;color:var(--t3)">Titular</div>
            </div>
          </div>
        </template>

        <template v-if="dependentes.length">
          <div style="font-size:10px;font-weight:600;color:var(--t3);text-transform:uppercase;letter-spacing:.1em;font-family:'JetBrains Mono',monospace;margin:20px 0 10px">Dependentes</div>
          <div v-for="member in dependentes" :key="member.id" class="ac">
            <div class="mem-avatar">{{ initials(member.name) }}</div>
            <div style="flex:1;min-width:0">
              <div style="font-size:13px;font-weight:600;color:var(--t1)">{{ member.name }}</div>
              <div style="font-size:11px;color:var(--t3)">Dependente</div>
            </div>
          </div>
        </template>

        <div v-if="!members.length" style="padding:48px 0;text-align:center;color:var(--t4);font-size:13px">
          Nenhum portador cadastrado.
          <br />
          <button class="btn btn-p" style="margin-top:12px" @click="open('novo-portador')">Adicionar portador</button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app' })
const { open } = useModal()
const { members, isLoading, fetchMembers } = useMembers()

onMounted(fetchMembers)

const titulares = computed(() => members.value.filter((m) => m.relationship === 'titular'))
const dependentes = computed(() => members.value.filter((m) => m.relationship === 'dependente'))

function initials(name: string) {
  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? '')
    .join('')
}
</script>

<style scoped>
.mem-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--bd);
  color: var(--t1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}
</style>
