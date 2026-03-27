<template>
  <div class="pagina">

    <div class="pagina-header">
      <h1>Revisões</h1>
      <button class="btn btn-sucesso" @click="abrirModalCriar">+ Nova revisão</button>
    </div>

    <p v-if="mensagem" :class="['alerta', mensagem.tipo === 'sucesso' ? 'alerta-sucesso' : 'alerta-erro']">
      {{ mensagem.texto }}
    </p>

    <div class="filtro-ativo-tag" v-if="filtroVeiculoPlaca">
      <span class="filtro-ativo-icone">🚗</span>
      <span class="filtro-ativo-texto">Exibindo revisões do veículo: <strong>{{ filtroVeiculoPlaca }}</strong></span>
      <button class="filtro-ativo-limpar" @click="limparFiltroVeiculo">✕ Limpar filtro</button>
    </div>

    <div class="filtros">
      <input v-model="filtroTexto"  class="filtro-input" type="text" placeholder="Buscar por placa, marca ou responsável..." />
      <input v-model="filtroInicio" class="filtro-input" type="date" title="Data inicial" />
      <input v-model="filtroFim"    class="filtro-input" type="date" title="Data final" />
      <button class="btn btn-neutro" v-if="filtroTexto || filtroInicio || filtroFim" @click="limparFiltrosLocais">
        Limpar filtros
      </button>
    </div>

    <p class="contador-resultados" v-if="!carregando">
      {{ revisoesFiltradas.length }} revisão(ões) encontrada(s)
    </p>

    <p v-if="carregando" class="estado-loading">Carregando...</p>

    <div class="tabela-revisoes-wrapper" v-if="!carregando">
      <table class="tabela-revisoes">
        <colgroup>
          <col class="col-data">
          <col class="col-veiculo">
          <col class="col-flex">
          <col class="col-km">
          <col class="col-responsavel">
          <col class="col-custo">
          <col class="col-acoes">
        </colgroup>
        <thead>
          <tr>
            <th>Data</th>
            <th>Veículo</th>
            <th>Proprietário</th>
            <th>KM</th>
            <th>Responsável</th>
            <th>Custo</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="revisoesFiltradas.length === 0">
            <td colspan="7" class="estado-vazio">
              <span v-if="filtroVeiculoPlaca">Nenhuma revisão encontrada para o veículo <strong>{{ filtroVeiculoPlaca }}</strong>.</span>
              <span v-else>Nenhuma revisão encontrada.</span>
            </td>
          </tr>
          <tr v-for="r in revisoesPaginadas" :key="r.id">
            <td>{{ formatarData(r.data_revisao) }}</td>
            <td>
              <div class="veiculo-cell">
                <strong class="placa-texto">{{ r.veiculo_placa }}</strong>
                <span class="veiculo-sub">{{ r.veiculo_marca }} {{ r.veiculo_modelo }}</span>
              </div>
            </td>
            <td>{{ r.proprietario_nome }}</td>
            <td class="td-km">{{ formatarKm(r.quilometragem) }}</td>
            <td>{{ r.responsavel }}</td>
            <td class="td-custo"><span class="custo-valor">{{ formatarMoeda(r.custo) }}</span></td>
            <td>
              <div class="acoes-cell">
                <button class="btn btn-info btn-sm"     @click="abrirModalDetalhes(r)">🔍 Detalhes</button>
                <button class="btn btn-primario btn-sm" @click="abrirModalEditar(r)">Editar</button>
                <button class="btn btn-perigo btn-sm"   @click="confirmarDeletar(r)">Excluir</button>
              </div>
            </td>
          </tr>
        </tbody>
        <tfoot v-if="revisoesFiltradas.length > 0">
          <tr>
            <td colspan="5" class="tfoot-label">Total das Revisões (filtro atual)</td>
            <td class="tfoot-total">{{ formatarMoeda(totalCustos) }}</td>
            <td></td>
          </tr>
        </tfoot>
      </table>

      <div class="paginacao" v-if="totalPaginas > 1">
        <button class="btn-paginacao" :disabled="paginaAtual === 1" @click="irParaPagina(1)">«</button>
        <button class="btn-paginacao" :disabled="paginaAtual === 1" @click="irParaPagina(paginaAtual - 1)">← Anterior</button>
        <button v-for="n in paginasVisiveis" :key="n"
          class="btn-paginacao" :class="{ 'btn-paginacao-ativo': n === paginaAtual }"
          @click="irParaPagina(n)">{{ n }}</button>
        <button class="btn-paginacao" :disabled="paginaAtual === totalPaginas" @click="irParaPagina(paginaAtual + 1)">Próximo →</button>
        <button class="btn-paginacao" :disabled="paginaAtual === totalPaginas" @click="irParaPagina(totalPaginas)">»</button>
        <span class="paginacao-info">Página {{ paginaAtual }} de {{ totalPaginas }}</span>
      </div>
    </div>

    <!-- Modal de detalhes (permanece como modal centralizado — só leitura) -->
    <div class="modal-overlay" v-if="modalDetalhes" @click.self="modalDetalhes = false">
      <div class="modal-card modal-card-lg">
        <div class="modal-header detalhe-header">
          <div>
            <h2 class="detalhe-nome">Revisão — {{ revisaoDetalhes?.veiculo_placa }}</h2>
            <p class="detalhe-meta-revisao">{{ formatarData(revisaoDetalhes?.data_revisao) }}</p>
          </div>
          <button class="modal-fechar" @click="modalDetalhes = false">✕</button>
        </div>
        <div class="modal-body detalhes-grid" v-if="revisaoDetalhes">
          <div class="detalhe-item">
            <span class="detalhe-label">🚗 Veículo</span>
            <span class="detalhe-valor">{{ revisaoDetalhes.veiculo_placa }} — {{ revisaoDetalhes.veiculo_marca }} {{ revisaoDetalhes.veiculo_modelo }}</span>
          </div>
          <div class="detalhe-item">
            <span class="detalhe-label">👤 Proprietário</span>
            <span class="detalhe-valor">{{ revisaoDetalhes.proprietario_nome }}</span>
          </div>
          <div class="detalhe-item">
            <span class="detalhe-label">📅 Data</span>
            <span class="detalhe-valor">{{ formatarData(revisaoDetalhes.data_revisao) }}</span>
          </div>
          <div class="detalhe-item">
            <span class="detalhe-label">🛣️ Quilometragem</span>
            <span class="detalhe-valor">{{ formatarKm(revisaoDetalhes.quilometragem) }}</span>
          </div>
          <div class="detalhe-item">
            <span class="detalhe-label">🔧 Responsável</span>
            <span class="detalhe-valor">{{ revisaoDetalhes.responsavel }}</span>
          </div>
          <div class="detalhe-item">
            <span class="detalhe-label">💰 Custo</span>
            <span class="detalhe-valor detalhe-custo">{{ formatarMoeda(revisaoDetalhes.custo) }}</span>
          </div>
          <div class="detalhe-item detalhe-item-full">
            <span class="detalhe-label">📋 Descrição dos serviços</span>
            <span class="detalhe-valor detalhe-descricao">{{ revisaoDetalhes.descricao }}</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-neutro" @click="modalDetalhes = false">Fechar</button>
          <button class="btn btn-primario" @click="() => { modalDetalhes = false; abrirModalEditar(revisaoDetalhes) }">
            Editar revisão
          </button>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════════
         REQ 1 — OFFCANVAS LATERAL (cadastro/edição de revisão)
    ═══════════════════════════════════════════════════════════════ -->
    <div class="offcanvas-overlay" :class="{ ativo: panelAberto }" @click.self="fecharModal">
      <aside class="offcanvas-panel" :class="{ aberto: panelAberto }">

        <div class="offcanvas-header">
          <h2>{{ modoEdicao ? 'Editar revisão' : 'Nova revisão' }}</h2>
          <button class="offcanvas-fechar" @click="fecharModal">✕</button>
        </div>

        <div class="offcanvas-body">
          <form @submit.prevent="salvar" novalidate>

            <!-- Veículo (busca por placa) -->
            <div class="form-grupo" style="position: relative;">
              <label>Veículo * (busque pela placa)</label>
              <input
                v-model="termoBuscaVeiculo" type="text"
                placeholder="Digite a placa para buscar..."
                class="input-busca-proprietario"
                @input="onInputVeiculo" @focus="mostrarDropdownVeiculo = true"
                autocomplete="off"
              />
              <ul v-if="mostrarDropdownVeiculo && veiculosFiltradosForm.length > 0" class="dropdown-proprietario">
                <li v-for="v in veiculosFiltradosForm" :key="v.id"
                  @mousedown.prevent="selecionarVeiculo(v)" class="dropdown-proprietario-item">
                  <span class="dp-nome">{{ v.placa }}</span>
                  <span class="dp-cpf">{{ v.marca }} {{ v.modelo }}</span>
                </li>
              </ul>
              <div v-if="mostrarDropdownVeiculo && termoBuscaVeiculo && veiculosFiltradosForm.length === 0"
                class="dropdown-proprietario dropdown-vazio">Nenhum veículo encontrado.</div>
              <span class="campo-erro" v-if="erroVeiculo">{{ erroVeiculo }}</span>
            </div>

            <!-- Data + KM -->
            <div class="form-row">
              <div class="form-grupo">
                <label>Data da revisão *</label>
                <input v-model="form.data_revisao" type="date"
                  :max="dataHoje" :min="dataMinima" @change="validarData" required />
                <span class="campo-erro" v-if="erroData">{{ erroData }}</span>
              </div>
              <div class="form-grupo">
                <label>Quilometragem (km) *</label>
                <input v-model="form.quilometragem" type="number" placeholder="45000" min="0" step="0.01" required />
              </div>
            </div>

            <!-- Descrição -->
            <div class="form-grupo">
              <label>Descrição dos serviços *</label>
              <!--
                REQ 2 — maxlength="500" espelha o limite do banco.
                Textarea também suporta maxlength — bloqueia fisicamente
                a digitação além de 500 caracteres.
                O contador mostra quantos caracteres restam.
              -->
              <textarea
                v-model="form.descricao"
                rows="3"
                placeholder="Ex: Troca de óleo, filtro de ar..."
                maxlength="500"
                required
              ></textarea>
              <span class="campo-contador">{{ form.descricao.length }}/500</span>
            </div>

            <!-- Responsável + Custo -->
            <div class="form-row">
              <div class="form-grupo">
                <label>Responsável *</label>
                <!--
                  REQ 2 — maxlength="100" bloqueia fisicamente o campo.
                  @keydown bloqueia teclas especiais indesejadas (números
                  e símbolos) — só aceita letras, espaços e hífens.
                  Garante que nomes de oficina/mecânico sejam texto limpo.
                -->
                <input
                  v-model="form.responsavel"
                  type="text"
                  placeholder="Nome da oficina ou mecânico"
                  maxlength="100"
                  @keydown="bloquearResponsavelInvalido"
                  required
                />
                <span class="campo-contador">{{ form.responsavel.length }}/100</span>
                <span class="campo-info">Apenas letras, espaços e hífens</span>
              </div>
              <div class="form-grupo">
                <label>Custo (R$) *</label>
                <input v-model="custoExibicao" type="text" placeholder="R$ 0,00"
                  @input="onInputCusto" inputmode="numeric" required />
                <span class="campo-erro" v-if="erroCusto">{{ erroCusto }}</span>
              </div>
            </div>

            <p v-if="erroForm" class="form-erro">{{ erroForm }}</p>

            <div class="offcanvas-footer">
              <button type="button" class="btn btn-neutro" @click="fecharModal">Cancelar</button>
              <button type="submit" class="btn btn-sucesso"
                :disabled="salvando || !!erroData || !!erroVeiculo">
                {{ salvando ? 'Salvando...' : modoEdicao ? 'Salvar alterações' : 'Criar revisão' }}
              </button>
            </div>

          </form>
        </div>
      </aside>
    </div>

    <!-- Modal de confirmação de exclusão -->
    <div class="modal-overlay" v-if="modalDeletar" @click.self="modalDeletar = false">
      <div class="modal-card modal-card-sm">
        <div class="modal-header">
          <h2>Confirmar exclusão</h2>
          <button class="modal-fechar" @click="modalDeletar = false">✕</button>
        </div>
        <p style="margin: 16px 0;">
          Deseja excluir a revisão do veículo <strong>{{ revisaoSelecionada?.veiculo_placa }}</strong>
          realizada em <strong>{{ formatarData(revisaoSelecionada?.data_revisao) }}</strong>?
        </p>
        <div class="modal-footer">
          <button class="btn btn-neutro" @click="modalDeletar = false">Cancelar</button>
          <button class="btn btn-perigo" @click="deletar" :disabled="salvando">
            {{ salvando ? 'Excluindo...' : 'Confirmar exclusão' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter }             from 'vue-router'
import api                                 from '@/services/api'

const route  = useRoute()
const router = useRouter()

const revisoes           = ref([])
const veiculos           = ref([])
const carregando         = ref(true)
const salvando           = ref(false)
const mensagem           = ref(null)
const erroForm           = ref(null)
const erroData           = ref(null)
const erroVeiculo        = ref(null)
const erroCusto          = ref(null)
// REQ 1 — offcanvas
const panelAberto        = ref(false)
const modalDeletar       = ref(false)
const modalDetalhes      = ref(false)
const modoEdicao         = ref(false)
const revisaoSelecionada = ref(null)
const revisaoDetalhes    = ref(null)
const filtroTexto        = ref('')
const filtroInicio       = ref('')
const filtroFim          = ref('')
const filtroVeiculoId    = ref(null)
const filtroVeiculoPlaca = ref('')
const termoBuscaVeiculo  = ref('')
const mostrarDropdownVeiculo = ref(false)
const custoExibicao      = ref('')
const dataHoje           = new Date().toISOString().split('T')[0]
const dataMinima         = '2020-12-01'
const ITENS_POR_PAGINA   = 10
const paginaAtual        = ref(1)
const formVazio = { veiculo: '', data_revisao: '', quilometragem: '', descricao: '', responsavel: '', custo: '' }
const form = ref({ ...formVazio })

const veiculosFiltradosForm = computed(() => {
  const t = termoBuscaVeiculo.value.toUpperCase().trim()
  if (!t) return veiculos.value.slice(0, 8)
  return veiculos.value.filter(v => v.placa.includes(t)).slice(0, 8)
})

const revisoesFiltradas = computed(() =>
  revisoes.value
    .filter(r => {
      if (filtroVeiculoId.value && r.veiculo !== Number(filtroVeiculoId.value)) return false
      const txt = filtroTexto.value.toLowerCase()
      const bateTexto = !txt ||
        r.veiculo_placa?.toLowerCase().includes(txt)  ||
        r.veiculo_marca?.toLowerCase().includes(txt)  ||
        r.veiculo_modelo?.toLowerCase().includes(txt) ||
        r.responsavel?.toLowerCase().includes(txt)
      return bateTexto &&
        (!filtroInicio.value || r.data_revisao >= filtroInicio.value) &&
        (!filtroFim.value    || r.data_revisao <= filtroFim.value)
    })
    .sort((a, b) => new Date(b.data_revisao) - new Date(a.data_revisao))
)

const totalPaginas = computed(() => Math.ceil(revisoesFiltradas.value.length / ITENS_POR_PAGINA))
const revisoesPaginadas = computed(() => {
  const i = (paginaAtual.value - 1) * ITENS_POR_PAGINA
  return revisoesFiltradas.value.slice(i, i + ITENS_POR_PAGINA)
})
const paginasVisiveis = computed(() => {
  const total = totalPaginas.value, atual = paginaAtual.value
  let ini = Math.max(1, atual - 2), fim = Math.min(total, ini + 4)
  if (fim - ini < 4) ini = Math.max(1, fim - 4)
  const p = []; for (let i = ini; i <= fim; i++) p.push(i); return p
})
const totalCustos = computed(() =>
  revisoesFiltradas.value.reduce((a, r) => a + parseFloat(r.custo || 0), 0).toFixed(2)
)

watch([filtroTexto, filtroInicio, filtroFim, filtroVeiculoId], () => { paginaAtual.value = 1 })
const irParaPagina = (n) => { if (n >= 1 && n <= totalPaginas.value) paginaAtual.value = n }

onMounted(async () => {
  if (route.query.veiculo_id) {
    filtroVeiculoId.value    = route.query.veiculo_id
    filtroVeiculoPlaca.value = route.query.veiculo_placa || ''
  }
  try {
    const [resR, resV] = await Promise.all([api.get('revisoes/'), api.get('veiculos/')])
    revisoes.value = resR.data; veiculos.value = resV.data
  } catch { exibirMensagem('Erro ao carregar dados.', 'erro') }
  finally  { carregando.value = false }
})

const limparFiltroVeiculo  = () => { filtroVeiculoId.value = null; filtroVeiculoPlaca.value = ''; router.replace({ name: 'revisoes' }) }
const limparFiltrosLocais  = () => { filtroTexto.value = ''; filtroInicio.value = ''; filtroFim.value = '' }
const abrirModalDetalhes   = (r) => { revisaoDetalhes.value = r; modalDetalhes.value = true }

const onInputVeiculo    = () => { form.value.veiculo = ''; erroVeiculo.value = null }
const selecionarVeiculo = (v) => {
  form.value.veiculo = v.id
  termoBuscaVeiculo.value = `${v.placa} — ${v.marca} ${v.modelo}`
  mostrarDropdownVeiculo.value = false; erroVeiculo.value = null
}
const validarVeiculoExiste = () => {
  mostrarDropdownVeiculo.value = false
  if (!form.value.veiculo) { erroVeiculo.value = 'Selecione um veículo válido.'; return false }
  erroVeiculo.value = null; return true
}
const validarData = () => {
  const d = form.value.data_revisao; if (!d) return true
  if (d > dataHoje)   { erroData.value = 'Não é permitido selecionar datas futuras.'; return false }
  if (d < dataMinima) { erroData.value = 'Não são aceitas revisões anteriores a dezembro de 2020.'; return false }
  erroData.value = null; return true
}
const onInputCusto = () => {
  const digits = custoExibicao.value.replace(/\D/g, '')
  if (!digits) { custoExibicao.value = ''; form.value.custo = ''; return }
  const num = parseInt(digits, 10) / 100
  form.value.custo    = num.toFixed(2)
  custoExibicao.value = num.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
  erroCusto.value = null
}

// ── REQ 2 — Bloqueio físico no campo Responsável ─────────────
// O campo responsável deve receber apenas letras (incluindo
// acentuadas), espaços, hífens e apóstrofes (para nomes como
// "D'Angelo"). Dígitos e símbolos são bloqueados antes de chegar
// ao input, garantindo que dados sujos não cheguem à API.
const bloquearResponsavelInvalido = (e) => {
  const permitidas = ['Backspace','Delete','Tab','ArrowLeft','ArrowRight','Home','End',' ']
  if (e.ctrlKey || e.metaKey) return
  if (permitidas.includes(e.key)) return
  // Aceita letras (incluindo acentuadas via regex unicode) e hífen/apóstrofe
  if (!/^[\p{L}'\-]$/u.test(e.key)) e.preventDefault()
}

// REQ 1 — offcanvas
const abrirModalCriar = () => {
  modoEdicao.value = false; form.value = { ...formVazio }
  erroForm.value = erroData.value = erroVeiculo.value = erroCusto.value = null
  custoExibicao.value = ''; termoBuscaVeiculo.value = ''
  mostrarDropdownVeiculo.value = false; panelAberto.value = true
}
const abrirModalEditar = (r) => {
  modoEdicao.value = true; revisaoSelecionada.value = r
  form.value = { veiculo: r.veiculo, data_revisao: r.data_revisao, quilometragem: r.quilometragem,
    descricao: r.descricao, responsavel: r.responsavel, custo: r.custo }
  const v = veiculos.value.find(x => x.id === r.veiculo)
  termoBuscaVeiculo.value = v ? `${v.placa} — ${v.marca} ${v.modelo}` : r.veiculo_placa || ''
  custoExibicao.value = parseFloat(r.custo || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
  erroForm.value = erroData.value = erroVeiculo.value = erroCusto.value = null
  mostrarDropdownVeiculo.value = false; panelAberto.value = true
}
const fecharModal = () => {
  panelAberto.value = false
  erroForm.value = erroData.value = erroVeiculo.value = erroCusto.value = null
  mostrarDropdownVeiculo.value = false
}

const salvar = async () => {
  if (!validarVeiculoExiste() || !validarData()) return
  salvando.value = true; erroForm.value = null
  try {
    if (modoEdicao.value) {
      const { data } = await api.put(`revisoes/${revisaoSelecionada.value.id}/update/`, form.value)
      const idx = revisoes.value.findIndex(r => r.id === revisaoSelecionada.value.id)
      if (idx !== -1) revisoes.value[idx] = { ...revisoes.value[idx], ...data }
      exibirMensagem('Revisão atualizada com sucesso.', 'sucesso')
    } else {
      const { data } = await api.post('revisoes/creat/', form.value)
      const veic = veiculos.value.find(v => v.id === form.value.veiculo)
      revisoes.value.unshift({ ...data,
        veiculo_placa: veic?.placa || '', veiculo_marca: veic?.marca || '',
        veiculo_modelo: veic?.modelo || '', proprietario_nome: veic?.proprietario_nome || '' })
      exibirMensagem('Revisão criada com sucesso.', 'sucesso')
    }
    fecharModal()
  } catch (e) {
    const erros = e.response?.data
    erroForm.value = erros ? Object.values(erros).flat().join(' ') : 'Erro ao salvar.'
  } finally { salvando.value = false }
}

const confirmarDeletar = (r) => { revisaoSelecionada.value = r; modalDeletar.value = true }
const deletar = async () => {
  salvando.value = true
  try {
    await api.delete(`revisoes/${revisaoSelecionada.value.id}/delete/`)
    revisoes.value = revisoes.value.filter(r => r.id !== revisaoSelecionada.value.id)
    modalDeletar.value = false; exibirMensagem('Revisão excluída com sucesso.', 'sucesso')
  } catch { exibirMensagem('Erro ao excluir revisão.', 'erro') }
  finally  { salvando.value = false }
}

const formatarData   = (d) => { if (!d) return '—'; const [a,m,dia] = d.split('-'); return `${dia}/${m}/${a}` }
const formatarMoeda  = (v) => Number(v).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
const formatarKm     = (k) => Number(k).toLocaleString('pt-BR') + ' km'
const exibirMensagem = (texto, tipo) => {
  mensagem.value = { texto, tipo }; setTimeout(() => { mensagem.value = null }, 4000)
}
</script>

<style scoped>
/* Tabela */
.tabela-revisoes-wrapper { width: 100%; overflow-x: auto; }
.tabela-revisoes { width: 100%; min-width: 1000px; table-layout: fixed; border-collapse: collapse; }
.col-data { width: 100px; } .col-veiculo { width: 160px; } .col-km { width: 110px; }
.col-responsavel { width: 150px; } .col-custo { width: 130px; } .col-acoes { width: 300px; }
.tabela-revisoes tbody tr td {
  vertical-align: middle; overflow: hidden; text-overflow: ellipsis;
  white-space: nowrap; padding: 8px 12px;
}
.tabela-revisoes tbody tr td:nth-child(3),
.tabela-revisoes tbody tr td:nth-child(5) { white-space: normal; word-break: break-word; }
.veiculo-cell { display: flex; flex-direction: column; align-items: flex-start; gap: 2px; }
.placa-texto { white-space: nowrap; letter-spacing: 0.5px; font-size: 0.88rem; }
.veiculo-sub { font-size: 0.75rem; color: #6b7280; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; }
.td-km, .td-custo { text-align: right; }
.acoes-cell { display: flex; align-items: center; justify-content: flex-end; gap: 8px; }

/* REQ 1 — Offcanvas */
.offcanvas-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.45);
  z-index: 200; opacity: 0; pointer-events: none; transition: opacity 0.3s ease;
}
.offcanvas-overlay.ativo { opacity: 1; pointer-events: all; }
.offcanvas-panel {
  position: fixed; top: 0; right: 0; bottom: 0;
  width: 100%; max-width: 500px; background: #fff;
  display: flex; flex-direction: column;
  transform: translateX(100%);
  transition: transform 0.3s cubic-bezier(0.4,0,0.2,1);
  box-shadow: -4px 0 24px rgba(0,0,0,0.12); z-index: 201;
}
.offcanvas-panel.aberto { transform: translateX(0); }
.offcanvas-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 20px 24px; border-bottom: 1px solid #e5e7eb;
  background: #1a1a2e; color: #fff; flex-shrink: 0;
}
.offcanvas-header h2 { font-size: 1.05rem; font-weight: 700; margin: 0; }
.offcanvas-fechar {
  background: none; border: none; color: rgba(255,255,255,0.75);
  font-size: 1.1rem; cursor: pointer; padding: 4px 8px; border-radius: 4px;
}
.offcanvas-fechar:hover { color: #fff; }
.offcanvas-body { flex: 1; overflow-y: auto; padding: 24px; }
.offcanvas-footer {
  display: flex; justify-content: flex-end; gap: 10px;
  padding: 16px 24px; border-top: 1px solid #e5e7eb;
  background: #f9fafb; flex-shrink: 0; margin-top: 20px;
}

/* REQ 2 — Contador e dica */
.campo-contador { display: block; text-align: right; font-size: 0.72rem; color: #9ca3af; margin-top: 2px; }
.campo-info     { display: block; font-size: 0.72rem; color: #9ca3af; margin-top: 2px; }
</style>