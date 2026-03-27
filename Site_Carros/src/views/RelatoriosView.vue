<template>
  <div class="pagina relatorios-pagina">

    <div class="pagina-header">
      <h1>Relatórios</h1>
      <span class="relatorio-subtitulo">Visão geral do sistema</span>
    </div>

    <div class="relatorio-loading" v-if="carregando">
      <span class="spinner"></span> Carregando dados...
    </div>

    <template v-if="!carregando">

      <!-- SEÇÃO 1 — VEÍCULOS -->
      <div class="secao-titulo">🚗 Veículos</div>

      <div class="relatorio-grid">

        <!-- Card: Total de Veículos -->
        <div class="card-relatorio card-destaque">
          <div class="card-rel-header">
            <span class="card-rel-titulo">Total de Veículos</span>
          </div>
          <div class="gauge-container">
            <span class="gauge-numero">{{ totalVeiculos }}</span>
            <span class="gauge-label">veículos cadastrados</span>
          </div>
          <div class="mini-barra-wrapper">
            <div class="mini-barra-item">
              <span class="mini-barra-label">Marcas</span>
              <div class="mini-barra-track">
                <div class="mini-barra-fill" style="width:100%; background:#60a5fa;"></div>
              </div>
              <span class="mini-barra-val">{{ dadosMarcas.length }}</span>
            </div>
          </div>
        </div>

        <!-- Card: Gênero vs. Frota (Donut) -->
        <div class="card-relatorio">
          <div class="card-rel-header">
            <span class="card-rel-titulo">Gênero vs. Frota</span>
            <span class="card-rel-sub">Quem possui mais veículos</span>
          </div>
          <div class="chart-box">
            <canvas ref="chartGeneroFrota"></canvas>
          </div>
        </div>

        <!-- Card: Ranking de Marcas (Barras verticais) -->
        <div class="card-relatorio card-wide">
          <div class="card-rel-header">
            <span class="card-rel-titulo">Ranking de Marcas</span>
            <span class="card-rel-sub">Volume de veículos por marca</span>
          </div>
          <div class="chart-box chart-box-tall">
            <canvas ref="chartMarcas"></canvas>
          </div>
        </div>

        <!-- Card: Marcas por Gênero (Stacked Bar) -->
        <div class="card-relatorio card-wide">
          <div class="card-rel-header">
            <span class="card-rel-titulo">Marcas por Gênero</span>
            <span class="card-rel-sub">Total por marca dividido entre Homens e Mulheres</span>
          </div>
          <div class="chart-box chart-box-tall">
            <canvas ref="chartMarcasGenero"></canvas>
          </div>
        </div>

      </div>

      <!-- SEÇÃO 2 — PESSOAS -->
      <div class="secao-titulo">👤 Pessoas</div>

      <div class="relatorio-grid">

        <!-- Card: Censo por Gênero (Pizza) -->
        <div class="card-relatorio">
          <div class="card-rel-header">
            <span class="card-rel-titulo">Censo por Gênero</span>
            <span class="card-rel-sub">Divisão de proprietários</span>
          </div>
          <div class="chart-box">
            <canvas ref="chartCenso"></canvas>
          </div>
        </div>

        <!-- Card: Idade Média por Gênero (Radial SVG) -->
        <div class="card-relatorio">
          <div class="card-rel-header">
            <span class="card-rel-titulo">Idade Média por Gênero</span>
            <span class="card-rel-sub">Média de idade dos proprietários</span>
          </div>
          <div class="radial-wrapper">
            <div v-for="g in idadeMedia" :key="g.genero" class="radial-item">
              <svg class="radial-svg" viewBox="0 0 80 80">
                <circle cx="40" cy="40" r="32" fill="none" stroke="#e5e7eb" stroke-width="8"/>
                <circle
                  cx="40" cy="40" r="32" fill="none"
                  :stroke="g.genero === 'Masculino' ? '#2563eb' : '#ec4899'"
                  stroke-width="8"
                  stroke-linecap="round"
                  :stroke-dasharray="`${(g.idade_media / 100) * 201} 201`"
                  transform="rotate(-90 40 40)"
                />
                <text x="40" y="44" text-anchor="middle" font-size="14" font-weight="700" fill="#1a1a2e">
                  {{ Math.round(g.idade_media) }}
                </text>
              </svg>
              <span class="radial-label">{{ g.genero }}</span>
            </div>
          </div>
          <p class="radial-nota">anos de média</p>
        </div>

      </div>

      <!-- SEÇÃO 3 — REVISÕES -->
      <div class="secao-titulo">🔧 Revisões</div>

      <div class="relatorio-grid">

        <!-- Card: Série Temporal (Linha) -->
        <div class="card-relatorio card-wide">
          <div class="card-rel-header">
            <span class="card-rel-titulo">Revisões por Mês</span>
            <span class="card-rel-sub">Total de revisões agrupadas por mês</span>
          </div>
          <div class="chart-box chart-box-tall">
            <canvas ref="chartSerieTemporal"></canvas>
          </div>
        </div>

        <!-- Card: Marcas com mais revisões -->
        <div class="card-relatorio">
          <div class="card-rel-header">
            <span class="card-rel-titulo">Marcas com Mais Revisões</span>
          </div>
          <div class="chart-box chart-box-tall">
            <canvas ref="chartMarcasRevisoes"></canvas>
          </div>
        </div>

        <!-- Card: Pessoas com mais revisões -->
        <div class="card-relatorio">
          <div class="card-rel-header">
            <span class="card-rel-titulo">Pessoas com Mais Revisões</span>
          </div>
          <div class="chart-box chart-box-tall">
            <canvas ref="chartPessoasRevisoes"></canvas>
          </div>
        </div>

        <!-- Card: Próximas Revisões Previstas -->
        <div class="card-relatorio card-wide">
          <div class="card-rel-header">
            <span class="card-rel-titulo">Próximas Revisões Previstas</span>
            <span class="card-rel-sub">Baseado na média histórica de cada proprietário</span>
          </div>
          <div class="proximas-wrapper">
            <p v-if="proximas.length === 0" class="estado-vazio">Nenhuma previsão disponível.</p>
            <table v-else class="tabela-proximas">
              <thead>
                <tr>
                  <th>Proprietário</th>
                  <th>Última revisão</th>
                  <th>Média (dias)</th>
                  <th>Próxima previsão</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in proximas" :key="p.nome">
                  <td>{{ p.nome }}</td>
                  <td>{{ formatarData(p.ultima_revisao) }}</td>
                  <td>{{ p.media_dias }} dias</td>
                  <td>{{ formatarData(p.proxima_revisao) }}</td>
                  <td>
                    <span :class="badgeProxima(p.proxima_revisao)">
                      {{ textoProxima(p.proxima_revisao) }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import api from '@/services/api'

let Chart = null

// ── Refs de canvas ────────────────────────────────────────────
const chartGeneroFrota     = ref(null)
const chartMarcas          = ref(null)
const chartMarcasGenero    = ref(null)
const chartCenso           = ref(null)
const chartSerieTemporal   = ref(null)
const chartMarcasRevisoes  = ref(null)
const chartPessoasRevisoes = ref(null)

const instancias = {}

// ── Dados ─────────────────────────────────────────────────────
const carregando        = ref(true)
const dadosGeneroFrota  = ref([])
const dadosMarcas       = ref([])
const dadosMarcasGenero = ref([])
const dadosCenso        = ref([])
const dadosRevisoes     = ref([])
const dadosMarcasRev    = ref([])
const dadosPessoasRev   = ref([])
const proximas          = ref([])

// ── Paleta ────────────────────────────────────────────────────
const CORES = {
  azul: '#2563eb', rosa: '#ec4899', verde: '#16a34a',
  laranja: '#f97316', vermelho: '#dc2626',
}
const PALETA = [
  '#2563eb','#ec4899','#16a34a','#f97316','#7c3aed',
  '#0891b2','#ca8a04','#dc2626','#0d9488','#9333ea',
  '#b45309','#1d4ed8','#be185d','#15803d','#c2410c',
]

// ── Computeds ─────────────────────────────────────────────────
const totalVeiculos = computed(() =>
  dadosMarcas.value.reduce((a, m) => a + m.total, 0)
)

const idadeMedia = computed(() =>
  dadosCenso.value.map(g => ({ genero: g.genero, idade_media: g.idade_media || 0 }))
)

const serieTemporal = computed(() => {
  const meses = {}
  dadosRevisoes.value.forEach(r => {
    const chave = r.data_revisao?.substring(0, 7)
    if (chave) meses[chave] = (meses[chave] || 0) + 1
  })
  const ord = Object.entries(meses).sort((a, b) => a[0].localeCompare(b[0]))
  return {
    labels: ord.map(([k]) => { const [a,m] = k.split('-'); return `${m}/${a}` }),
    valores: ord.map(([,v]) => v),
  }
})

// ── Helpers ───────────────────────────────────────────────────
const formatarData = (d) => {
  if (!d) return '—'
  const [a, m, dia] = d.split('-')
  return `${dia}/${m}/${a}`
}
const badgeProxima = (data) => {
  if (!data) return 'badge badge-masculino'
  const diff = (new Date(data) - new Date()) / 86400000
  if (diff < 0)   return 'badge badge-feminino'
  if (diff <= 15) return 'badge badge-moto'
  return 'badge badge-carro'
}
const textoProxima = (data) => {
  if (!data) return '—'
  const diff = (new Date(data) - new Date()) / 86400000
  if (diff < 0)   return 'Atrasada'
  if (diff <= 15) return 'Próxima'
  return 'Em dia'
}

// ── Plugin de datalabels inline ───────────────────────────────
const pluginDatalabels = {
  id: 'datalabels',
  afterDatasetsDraw(chart) {
    const { ctx } = chart
    chart.data.datasets.forEach((dataset, datasetIndex) => {
      const meta = chart.getDatasetMeta(datasetIndex)
      if (meta.hidden) return
      if (!['bar'].includes(meta.type)) return

      meta.data.forEach((element, index) => {
        const value = dataset.data[index]
        if (value === null || value === undefined || value === 0) return

        const { x, y } = element.tooltipPosition()
        const isHorizontal = chart.options.indexAxis === 'y'

        ctx.save()
        ctx.font        = 'bold 11px Segoe UI, sans-serif'
        ctx.fillStyle   = '#1a1a2e'
        ctx.textAlign   = 'center'
        ctx.textBaseline= isHorizontal ? 'middle' : 'bottom'

        if (isHorizontal) {
          ctx.textAlign    = 'left'
          ctx.textBaseline = 'middle'
          ctx.fillText(value, x + 5, y)
        } else {
          ctx.fillText(value, x, y - 4)
        }
        ctx.restore()
      })
    })
  },
}

// Plugin para exibir total no centro do donut
const pluginDonutTotal = {
  id: 'donutTotal',
  afterDraw(chart) {
    if (chart.config.type !== 'doughnut') return
    const { ctx, chartArea } = chart
    const total = chart.data.datasets[0].data.reduce((a, b) => a + b, 0)
    const cx = (chartArea.left + chartArea.right) / 2
    const cy = (chartArea.top  + chartArea.bottom) / 2
    ctx.save()
    ctx.font      = 'bold 22px Segoe UI, sans-serif'
    ctx.fillStyle = '#1a1a2e'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(total, cx, cy - 8)
    ctx.font      = '11px Segoe UI, sans-serif'
    ctx.fillStyle = '#6b7280'
    ctx.fillText('total', cx, cy + 12)
    ctx.restore()
  },
}

// ── Destroy helper ────────────────────────────────────────────
const destruir = (k) => {
  if (instancias[k]) { instancias[k].destroy(); delete instancias[k] }
}

// ── Opções base ───────────────────────────────────────────────
const optBase = (pos = 'bottom') => ({
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: {
      position: pos,
      labels: {
        font: { family: "'Segoe UI',sans-serif", size: 11 },
        padding: 12,
        boxWidth: 12,
      },
    },
    tooltip: {
      bodyFont:  { family: "'Segoe UI',sans-serif" },
      titleFont: { family: "'Segoe UI',sans-serif" },
    },
  },
})

// ── Gráficos ──────────────────────────────────────────────────

const criarGeneroFrota = () => {
  destruir('gf')
  if (!chartGeneroFrota.value || !dadosGeneroFrota.value.length) return
  instancias.gf = new Chart(chartGeneroFrota.value, {
    type: 'doughnut',
    plugins: [pluginDonutTotal],
    data: {
      labels: dadosGeneroFrota.value.map(d => `${d.genero} (${d.total})`),
      datasets: [{
        data: dadosGeneroFrota.value.map(d => d.total),
        backgroundColor: [CORES.azul, CORES.rosa],
        borderWidth: 2,
        borderColor: '#fff',
      }],
    },
    options: { ...optBase('right'), cutout: '62%' },
  })
}

const criarMarcas = () => {
  destruir('mr')
  if (!chartMarcas.value || !dadosMarcas.value.length) return
  const s = [...dadosMarcas.value].sort((a, b) => b.total - a.total)
  instancias.mr = new Chart(chartMarcas.value, {
    type: 'bar',
    plugins: [pluginDatalabels],
    data: {
      labels: s.map(d => d.marca),
      datasets: [{
        label: 'Veículos',
        data: s.map(d => d.total),
        backgroundColor: s.map((_, i) => PALETA[i % PALETA.length]),
        borderRadius: 6,
      }],
    },
    options: {
      ...optBase('top'),
      plugins: {
        ...optBase('top').plugins,
        legend: { display: false },
      },
      scales: {
        y: {
          beginAtZero: true,
          suggestedMax: Math.max(...s.map(d => d.total)) + 1,
          ticks: { stepSize: 1, font: { size: 11 } },
          grid: { color: '#f3f4f6' },
        },
        x: { ticks: { font: { size: 10 } }, grid: { display: false } },
      },
    },
  })
}

const criarMarcasGenero = () => {
  destruir('mg')
  if (!chartMarcasGenero.value || !dadosMarcasGenero.value.length) return
  const mapa = {}
  dadosMarcasGenero.value.forEach(({ marca, genero, total }) => {
    if (!mapa[marca]) mapa[marca] = { Masculino: 0, Feminino: 0 }
    mapa[marca][genero] = total
  })
  const marcas = Object.keys(mapa).sort()
  const totaisPorMarca = marcas.map(m => (mapa[m].Masculino || 0) + (mapa[m].Feminino || 0))

  instancias.mg = new Chart(chartMarcasGenero.value, {
    type: 'bar',
    plugins: [{
      id: 'stackedTotal',
      afterDatasetsDraw(chart) {
        const { ctx } = chart
        const lastDatasetMeta = chart.getDatasetMeta(chart.data.datasets.length - 1)
        lastDatasetMeta.data.forEach((element, index) => {
          const total = totaisPorMarca[index]
          if (!total) return
          const { x, y } = element.tooltipPosition()
          ctx.save()
          ctx.font         = 'bold 11px Segoe UI, sans-serif'
          ctx.fillStyle    = '#1a1a2e'
          ctx.textAlign    = 'center'
          ctx.textBaseline = 'bottom'
          const topY = chart.getDatasetMeta(0).data[index].tooltipPosition().y
          ctx.fillText(total, x, topY - 4)
          ctx.restore()
        })
      },
    }],
    data: {
      labels: marcas,
      datasets: [
        {
          label: 'Masculino',
          data: marcas.map(m => mapa[m].Masculino || 0),
          backgroundColor: CORES.azul,
          borderRadius: 4,
          stack: 'g',
        },
        {
          label: 'Feminino',
          data: marcas.map(m => mapa[m].Feminino || 0),
          backgroundColor: CORES.rosa,
          borderRadius: 4,
          stack: 'g',
        },
      ],
    },
    options: {
      ...optBase('top'),
      scales: {
        x: { stacked: true, ticks: { font: { size: 10 } }, grid: { display: false } },
        y: {
          stacked: true,
          beginAtZero: true,
          suggestedMax: Math.max(...totaisPorMarca) + 1,
          ticks: { stepSize: 1, font: { size: 11 } },
          grid: { color: '#f3f4f6' },
        },
      },
    },
  })
}

const criarCenso = () => {
  destruir('ce')
  if (!chartCenso.value || !dadosCenso.value.length) return
  instancias.ce = new Chart(chartCenso.value, {
    type: 'pie',
    data: {
      labels: dadosCenso.value.map(d => `${d.genero} (${d.total})`),
      datasets: [{
        data: dadosCenso.value.map(d => d.total),
        backgroundColor: [CORES.azul, CORES.rosa],
        borderWidth: 2,
        borderColor: '#fff',
      }],
    },
    options: { ...optBase('right') },
  })
}

const criarSerieTemporal = () => {
  destruir('st')
  if (!chartSerieTemporal.value) return
  const { labels, valores } = serieTemporal.value
  const maxVal = Math.max(...valores)

  instancias.st = new Chart(chartSerieTemporal.value, {
    type: 'line',
    plugins: [{
      id: 'lineLabels',
      afterDatasetsDraw(chart) {
        const { ctx } = chart
        const meta = chart.getDatasetMeta(0)
        meta.data.forEach((element, index) => {
          const value = chart.data.datasets[0].data[index]
          if (!value) return
          const { x, y } = element.tooltipPosition()
          ctx.save()
          ctx.font         = 'bold 11px Segoe UI, sans-serif'
          ctx.fillStyle    = '#2563eb'
          ctx.textAlign    = 'center'
          ctx.textBaseline = 'bottom'
          ctx.fillText(value, x, y - 6)
          ctx.restore()
        })
      },
    }],
    data: {
      labels,
      datasets: [{
        label: 'Revisões',
        data: valores,
        borderColor: CORES.azul,
        backgroundColor: 'rgba(37,99,235,0.10)',
        borderWidth: 2.5,
        pointRadius: 5,
        pointBackgroundColor: CORES.azul,
        fill: true,
        tension: 0.35,
      }],
    },
    options: {
      ...optBase('top'),
      plugins: { ...optBase('top').plugins, legend: { display: false } },
      scales: {
        y: {
          beginAtZero: true,
          suggestedMax: maxVal + 1,
          ticks: { stepSize: 1, font: { size: 11 } },
          grid: { color: '#f3f4f6' },
        },
        x: { ticks: { font: { size: 10 } }, grid: { display: false } },
      },
    },
  })
}

const criarMarcasRevisoes = () => {
  destruir('mrev')
  if (!chartMarcasRevisoes.value || !dadosMarcasRev.value.length) return
  const s = [...dadosMarcasRev.value].sort((a, b) => b.total - a.total).slice(0, 10)
  instancias.mrev = new Chart(chartMarcasRevisoes.value, {
    type: 'bar',
    plugins: [pluginDatalabels],
    data: {
      labels: s.map(d => d.marca),
      datasets: [{
        label: 'Revisões',
        data: s.map(d => d.total),
        backgroundColor: s.map((_, i) => PALETA[i % PALETA.length]),
        borderRadius: 6,
      }],
    },
    options: {
      ...optBase('top'),
      plugins: { ...optBase('top').plugins, legend: { display: false } },
      scales: {
        y: {
          beginAtZero: true,
          suggestedMax: Math.max(...s.map(d => d.total)) + 1,
          ticks: { stepSize: 1, font: { size: 11 } },
          grid: { color: '#f3f4f6' },
        },
        x: { ticks: { font: { size: 10 } }, grid: { display: false } },
      },
    },
  })
}

const criarPessoasRevisoes = () => {
  destruir('prev')
  if (!chartPessoasRevisoes.value || !dadosPessoasRev.value.length) return
  const s = [...dadosPessoasRev.value].sort((a, b) => b.total - a.total).slice(0, 10)
  instancias.prev = new Chart(chartPessoasRevisoes.value, {
    type: 'bar',
    plugins: [pluginDatalabels],
    data: {
      labels: s.map(d => d.nome),
      datasets: [{
        label: 'Revisões',
        data: s.map(d => d.total),
        backgroundColor: CORES.verde,
        borderRadius: 4,
      }],
    },
    options: {
      ...optBase('top'),
      indexAxis: 'y',
      plugins: { ...optBase('top').plugins, legend: { display: false } },
      scales: {
        x: {
          beginAtZero: true,
          suggestedMax: Math.max(...s.map(d => d.total)) + 1,
          ticks: { stepSize: 1, font: { size: 10 } },
          grid: { color: '#f3f4f6' },
        },
        y: { ticks: { font: { size: 10 } }, grid: { display: false } },
      },
    },
  })
}

// ── onMounted ─────────────────────────────────────────────────
onMounted(async () => {
  const mod = await import('https://cdn.jsdelivr.net/npm/chart.js@4.4.3/auto/+esm')
  Chart = mod.default ?? mod.Chart ?? mod

  const resultados = await Promise.allSettled([
    api.get('veiculos/relatorio/genero/'),
    api.get('veiculos/relatorio/marcas/'),
    api.get('veiculos/relatorio/marcas_genero/'),
    api.get('users/relatorio/genero/'),
    api.get('revisoes/'),
    api.get('revisoes/relatorio/marcas/'),
    api.get('revisoes/relatorio/pessoas/'),
    api.get('revisoes/relatorio/proximas/'),
  ])

  const ok = (r) => r.status === 'fulfilled' ? r.value.data : []

  dadosGeneroFrota.value   = ok(resultados[0])
  dadosMarcas.value        = ok(resultados[1])
  dadosMarcasGenero.value  = ok(resultados[2])
  dadosCenso.value         = ok(resultados[3])
  dadosRevisoes.value      = ok(resultados[4])
  dadosMarcasRev.value     = ok(resultados[5])
  dadosPessoasRev.value    = ok(resultados[6])
  proximas.value           = ok(resultados[7])

  resultados.forEach((r, i) => {
    if (r.status === 'rejected') console.warn(`Relatório #${i} falhou:`, r.reason?.message)
  })

  carregando.value = false
  await nextTick()

  criarGeneroFrota()
  criarMarcas()
  criarMarcasGenero()
  criarCenso()
  criarSerieTemporal()
  criarMarcasRevisoes()
  criarPessoasRevisoes()
})

onBeforeUnmount(() => {
  Object.values(instancias).forEach(c => c.destroy())
})
</script>

<style scoped>
.secao-titulo {
  font-size: 1rem;
  font-weight: 700;
  color: #1a1a2e;
  margin: 28px 0 14px;
  padding-left: 10px;
  border-left: 4px solid #2563eb;
}

.relatorio-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 18px;
  margin-bottom: 8px;
}

.card-relatorio {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 16px 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  transition: box-shadow 0.2s;
}
.card-relatorio:hover { box-shadow: 0 4px 16px rgba(37,99,235,0.10); }
.card-wide { grid-column: span 2; }

.card-destaque {
  background: linear-gradient(135deg, #1a1a2e 0%, #2563eb 100%);
  color: #fff;
  border: none;
}
.card-destaque .card-rel-titulo,
.card-destaque .card-rel-sub { color: rgba(255,255,255,0.9); }

.card-rel-header { display: flex; flex-direction: column; gap: 2px; }
.card-rel-titulo { font-size: 0.875rem; font-weight: 700; color: #1a1a2e; }
.card-rel-sub    { font-size: 0.75rem; color: #6b7280; }

.chart-box {
  position: relative;
  max-height: 240px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.chart-box canvas { max-height: 220px !important; width: 100% !important; }
.chart-box-tall { max-height: 260px; }
.chart-box-tall canvas { max-height: 240px !important; }

.gauge-container { display:flex; flex-direction:column; align-items:center; gap:4px; padding:8px 0; }
.gauge-numero { font-size:3rem; font-weight:800; color:#fff; line-height:1; }
.gauge-label  { font-size:.8rem; color:rgba(255,255,255,0.75); }
.mini-barra-wrapper { display:flex; flex-direction:column; gap:6px; margin-top:4px; }
.mini-barra-item { display:flex; align-items:center; gap:8px; font-size:.78rem; color:rgba(255,255,255,.85); }
.mini-barra-label { width:56px; flex-shrink:0; }
.mini-barra-track { flex:1; height:6px; background:rgba(255,255,255,.2); border-radius:3px; overflow:hidden; }
.mini-barra-fill  { height:100%; border-radius:3px; }
.mini-barra-val   { width:28px; text-align:right; }

.radial-wrapper { display:flex; justify-content:center; gap:28px; padding:8px 0; }
.radial-item    { display:flex; flex-direction:column; align-items:center; gap:6px; }
.radial-svg     { width:80px; height:80px; }
.radial-label   { font-size:.8rem; color:#374151; font-weight:600; }
.radial-nota    { text-align:center; font-size:.75rem; color:#9ca3af; margin-top:-4px; }

.proximas-wrapper { overflow-x:auto; max-height:280px; overflow-y:auto; }
.tabela-proximas { width:100%; border-collapse:collapse; font-size:.825rem; }
.tabela-proximas th { background:#f9fafb; padding:7px 10px; text-align:left; font-weight:600; color:#374151; border-bottom:1px solid #e5e7eb; white-space:nowrap; }
.tabela-proximas td { padding:7px 10px; border-bottom:1px solid #f3f4f6; color:#1f2937; white-space:nowrap; }
.tabela-proximas tr:last-child td { border-bottom:none; }
.tabela-proximas tr:hover td { background:#f8faff; }

.relatorio-loading { display:flex; align-items:center; gap:10px; padding:40px 0; justify-content:center; color:#6b7280; font-size:.9rem; }
.spinner { width:20px; height:20px; border:3px solid #e5e7eb; border-top-color:#2563eb; border-radius:50%; animation:spin .7s linear infinite; display:inline-block; }
@keyframes spin { to { transform:rotate(360deg); } }

.relatorio-subtitulo { font-size:.82rem; color:#6b7280; margin-left:8px; }

@media (max-width: 700px) {
  .card-wide { grid-column: span 1; }
  .relatorio-grid { grid-template-columns: 1fr; }
}
</style>