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
      <!-- Error banner -->
      <div v-if="error" role="alert" style="background:var(--ald);border:1px solid var(--alert);border-radius:8px;padding:10px 14px;font-size:12px;color:var(--alert);margin-bottom:16px">
        {{ error }}
      </div>

      <!-- Skeleton while loading -->
      <template v-if="isLoading">
        <UiSkeletonCard v-for="n in 5" :key="n" style="margin-bottom:8px" />
      </template>

      <template v-else>
        <template v-if="titulares.length">
          <div style="font-size:10px;font-weight:600;color:var(--t3);text-transform:uppercase;letter-spacing:.1em;font-family:'Space Grotesk',monospace;margin-bottom:10px">Titulares</div>
          <UiMemberCard
            v-for="member in titulares"
            :key="member.id"
            :name="member.name"
            relationship="titular"
            :spent-label="formatBRL(spendByMember.get(member.id) ?? 0)"
          />
        </template>

        <template v-if="dependentes.length">
          <div style="font-size:10px;font-weight:600;color:var(--t3);text-transform:uppercase;letter-spacing:.1em;font-family:'Space Grotesk',monospace;margin:20px 0 10px">Dependentes</div>
          <UiMemberCard
            v-for="member in dependentes"
            :key="member.id"
            :name="member.name"
            relationship="dependente"
            :spent-label="formatBRL(spendByMember.get(member.id) ?? 0)"
          />
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
const { members, isLoading, error, fetchMembers } = useMembers()
const { formatBRL } = useFormatters()

const memberSpends = ref<MemberSpend[]>([])

onMounted(async () => {
  await fetchMembers()
  const now = new Date()
  memberSpends.value = await fetchMemberSpends(
    members.value.map((m) => m.id), now.getFullYear(), now.getMonth() + 1,
  )
})

const titulares = computed(() => members.value.filter((m) => m.relationship === 'titular'))
const dependentes = computed(() => members.value.filter((m) => m.relationship === 'dependente'))
const spendByMember = computed(() => new Map(memberSpends.value.map((s) => [s.memberId, s.totalDebits])))
</script>
