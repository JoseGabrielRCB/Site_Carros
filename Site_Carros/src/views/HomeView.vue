<template>
  <div class="pagina">

    <!-- ── Hero ── -->
    <div class="home-hero">
      <div class="home-hero-texto">
        <h1>Sistema de Revisoes de Veiculos</h1>
        <p>Gerencie proprietarios, veiculos e historico de revisoes em um so lugar.</p>
      </div>
    </div>

    <!-- ── Cards de totais ── -->
    <div class="grid-cards" style="margin-top: 32px;">
      <div class="card card-stat">
        <div class="card-stat-icone icone-azul">👤</div>
        <div class="card-stat-info">
          <span class="card-stat-numero">{{ carregando ? '...' : totais.usuarios }}</span>
          <span class="card-stat-label">Proprietarios</span>
        </div>
      </div>
      <div class="card card-stat">
        <div class="card-stat-icone icone-verde">🚗</div>
        <div class="card-stat-info">
          <span class="card-stat-numero">{{ carregando ? '...' : totais.veiculos }}</span>
          <span class="card-stat-label">Veiculos</span>
        </div>
      </div>
      <div class="card card-stat">
        <div class="card-stat-icone icone-laranja">🔧</div>
        <div class="card-stat-info">
          <span class="card-stat-numero">{{ carregando ? '...' : totais.revisoes }}</span>
          <span class="card-stat-label">Revisoes</span>
        </div>
      </div>
    </div>

    <!-- ════════════════════════════════════════════════════════════
         Acesso Rapido — um atalho por pagina existente no sistema.
         Descricoes removidas: exibe apenas icone + nome da pagina.
         Rotas: proprietarios, veiculos, revisoes, relatorios, funcionarios.
    ════════════════════════════════════════════════════════════ -->
    <h2 style="margin-top: 40px; margin-bottom: 16px;">Acesso rapido</h2>
    <div class="grid-cards">

      <div class="card card-atalho" @click="ir('proprietarios')">
        <div class="atalho-icone">👤</div>
        <h3>Proprietários</h3>
        <span class="atalho-seta">→</span>
      </div>

      <div class="card card-atalho" @click="ir('veiculos')">
        <div class="atalho-icone">🚗</div>
        <h3>Veículos</h3>
        <span class="atalho-seta">→</span>
      </div>

      <div class="card card-atalho" @click="ir('revisoes')">
        <div class="atalho-icone">🔧</div>
        <h3>Revisões</h3>
        <span class="atalho-seta">→</span>
      </div>

      <div class="card card-atalho" @click="ir('relatorios')">
        <div class="atalho-icone">📊</div>
        <h3>Relatórios</h3>
        <span class="atalho-seta">→</span>
      </div>

    </div>

    <!-- ── Proximas revisoes ── -->
    <h2 style="margin-top: 40px; margin-bottom: 16px;">Proximas revisoes previstas</h2>

    <p v-if="carregando" class="estado-loading">Carregando...</p>
    <p v-if="erroProximas" class="alerta alerta-erro">{{ erroProximas }}</p>

    <div class="tabela-wrapper" v-if="!carregando && proximas.length > 0">
      <table>
        <thead>
          <tr>
            <th>Proprietario</th>
            <th>Ultima revisao</th>
            <th>Media proxima revisao (dias)</th>
            <th>Proxima previsao</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in proximasPaginadas" :key="p.nome">
            <td>{{ p.nome }}</td>
            <td>{{ formatarData(p.ultima_revisao) }}</td>
            <td>{{ p.media_dias }} dias</td>
            <td>{{ formatarData(p.proxima_revisao) }}</td>
            <td>
              <span :class="badgeStatus(p.proxima_revisao)">
                {{ textoStatus(p.proxima_revisao) }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="paginacao" v-if="totalPaginas > 1">
        <button class="btn-paginacao" :disabled="paginaAtual === 1" @click="irParaPagina(paginaAtual - 1)">
          ← Anterior
        </button>
        <span class="paginacao-info">Pagina {{ paginaAtual }} de {{ totalPaginas }}</span>
        <button class="btn-paginacao" :disabled="paginaAtual === totalPaginas" @click="irParaPagina(paginaAtual + 1)">
          Proximo →
        </button>
      </div>
    </div>

    <p v-if="!carregando && proximas.length === 0" class="estado-vazio">
      Nenhuma previsao disponivel ainda.
    </p>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter }                from 'vue-router'
import api                          from '@/services/api'

const router       = useRouter()
const carregando   = ref(true)
const erroProximas = ref(null)
const proximas     = ref([])
const totais       = ref({ usuarios: 0, veiculos: 0, revisoes: 0 })

const ITENS_POR_PAGINA = 10
const paginaAtual      = ref(1)

const totalPaginas = computed(() =>
  Math.ceil(proximas.value.length / ITENS_POR_PAGINA)
)

const proximasPaginadas = computed(() => {
  const inicio = (paginaAtual.value - 1) * ITENS_POR_PAGINA
  return proximas.value.slice(inicio, inicio + ITENS_POR_PAGINA)
})

const irParaPagina = (n) => {
  if (n >= 1 && n <= totalPaginas.value) paginaAtual.value = n
}

onMounted(async () => {
  try {
    const [resUsuarios, resVeiculos, resRevisoes, resProximas] = await Promise.all([
      api.get('users/'),
      api.get('veiculos/'),
      api.get('revisoes/'),
      api.get('revisoes/relatorio/proximas/'),
    ])
    totais.value.usuarios = resUsuarios.data.length
    totais.value.veiculos = resVeiculos.data.length
    totais.value.revisoes = resRevisoes.data.length
    proximas.value        = resProximas.data
    paginaAtual.value     = 1
  } catch (e) {
    erroProximas.value = 'Nao foi possivel carregar alguns dados.'
  } finally {
    carregando.value = false
  }
})

const ir = (nome) => router.push({ name: nome })

const formatarData = (data) => {
  if (!data) return '—'
  const [ano, mes, dia] = data.split('-')
  return `${dia}/${mes}/${ano}`
}

const badgeStatus = (dataProxima) => {
  if (!dataProxima) return 'badge badge-masculino'
  const diff = (new Date(dataProxima) - new Date()) / 86400000
  if (diff < 0)   return 'badge badge-feminino'
  if (diff <= 15) return 'badge badge-moto'
  return 'badge badge-carro'
}

const textoStatus = (dataProxima) => {
  if (!dataProxima) return '—'
  const diff = (new Date(dataProxima) - new Date()) / 86400000
  if (diff < 0)   return 'Atrasada'
  if (diff <= 15) return 'Proxima'
  return 'Em dia'
}
</script>