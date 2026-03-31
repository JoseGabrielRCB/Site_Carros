<template>
  <transition name="slide-revisoes">
    <div v-if="panelRevisoes" class="revisoes-subpanel">

      <!-- Cabeçalho -->
      <div class="subpanel-header">
        <button class="btn-voltar" @click="$emit('fecharRevisoes')">← Voltar para Veículos</button>
        <div class="subpanel-titulo">
          <span class="subpanel-badge subpanel-badge--rev">📋</span>
          <h2>
            {{ veiculoRevisoes?.placa }}
            <span class="subpanel-sub">{{ veiculoRevisoes?.marca }} {{ veiculoRevisoes?.modelo }}</span>
          </h2>
        </div>
        <button class="btn btn-sucesso btn-sm" @click="$emit('abrirModalCriarRevisao')">+ Nova revisão</button>
      </div>

      <p v-if="mensagemRev" :class="['alerta', mensagemRev.tipo === 'sucesso' ? 'alerta-sucesso' : 'alerta-erro']">
        {{ mensagemRev.texto }}
      </p>

      <!-- Filtros -->
      <div class="filtros">
        <input
          :value="filtroTextoRev"
          @input="$emit('update:filtroTextoRev', $event.target.value)"
          class="filtro-input" type="text"
          placeholder="Buscar por responsável ou descrição..."
        />
        <input
          :value="filtroInicioRev"
          @input="$emit('update:filtroInicioRev', $event.target.value)"
          class="filtro-input" type="date" title="Data inicial"
        />
        <input
          :value="filtroFimRev"
          @input="$emit('update:filtroFimRev', $event.target.value)"
          class="filtro-input" type="date" title="Data final"
        />
        <button class="btn btn-neutro" v-if="filtroTextoRev || filtroInicioRev || filtroFimRev"
          @click="$emit('limparFiltrosRev')">
          Limpar filtros
        </button>
      </div>

      <p class="contador-resultados" v-if="!carregandoRev">
        {{ revisoesFiltradas.length }} revisão(ões) encontrada(s)
      </p>
      <p v-if="carregandoRev" class="estado-loading">Carregando revisões...</p>

      <!-- Tabela -->
      <div class="tabela-revisoes-wrapper" v-if="!carregandoRev">
        <table class="tabela-revisoes">
          <colgroup>
            <col class="rcol-data"> <col class="rcol-km"> <col class="rcol-flex">
            <col class="rcol-responsavel"> <col class="rcol-custo"> <col class="rcol-acoes">
          </colgroup>
          <thead>
            <tr>
              <th class="col-ordenavel" @click="alternarOrdenacao(ordenacaoRev, 'data_revisao')">
                Data <span class="sort-icon">{{ iconeOrdenacao(ordenacaoRev, 'data_revisao') }}</span>
              </th>
              <th class="col-ordenavel" @click="alternarOrdenacao(ordenacaoRev, 'quilometragem')">
                KM <span class="sort-icon">{{ iconeOrdenacao(ordenacaoRev, 'quilometragem') }}</span>
              </th>
              <th class="col-ordenavel" @click="alternarOrdenacao(ordenacaoRev, 'descricao')">
                Descrição <span class="sort-icon">{{ iconeOrdenacao(ordenacaoRev, 'descricao') }}</span>
              </th>
              <th class="col-ordenavel" @click="alternarOrdenacao(ordenacaoRev, 'responsavel')">
                Responsável <span class="sort-icon">{{ iconeOrdenacao(ordenacaoRev, 'responsavel') }}</span>
              </th>
              <th class="col-ordenavel" @click="alternarOrdenacao(ordenacaoRev, 'custo')">
                Custo <span class="sort-icon">{{ iconeOrdenacao(ordenacaoRev, 'custo') }}</span>
              </th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="revisoesPaginadasRev.length === 0">
              <td colspan="6" class="estado-vazio">Nenhuma revisão encontrada para este veículo.</td>
            </tr>
            <tr v-for="r in revisoesPaginadasRev" :key="r.id">
              <td>{{ formatarData(r.data_revisao) }}</td>
              <td class="td-km">{{ formatarKm(r.quilometragem) }}</td>
              <td class="td-descricao" :title="r.descricao">{{ r.descricao }}</td>
              <td>{{ r.responsavel }}</td>
              <td class="td-custo"><span class="custo-valor">{{ formatarMoeda(r.custo) }}</span></td>
              <td>
                <div class="acoes-cell">
                  <button class="btn btn-info btn-sm"     @click="$emit('abrirModalDetalhesRev', r)">🔍</button>
                  <button class="btn btn-primario btn-sm" @click="$emit('abrirModalEditarRev', r)">Editar</button>
                  <button class="btn btn-perigo btn-sm"   @click="$emit('confirmarDeletarRev', r)">Excluir</button>
                </div>
              </td>
            </tr>
          </tbody>
          <tfoot v-if="revisoesFiltradas.length > 0">
            <tr>
              <td colspan="4" class="tfoot-label">Total (filtro atual)</td>
              <td class="tfoot-total">{{ formatarMoeda(totalCustosRev) }}</td>
              <td></td>
            </tr>
          </tfoot>
        </table>

        <div class="paginacao" v-if="totalPaginasRev > 1">
          <button class="btn-paginacao" :disabled="paginaAtualRev === 1"
            @click="$emit('irParaPaginaRev', 1)">«</button>
          <button class="btn-paginacao" :disabled="paginaAtualRev === 1"
            @click="$emit('irParaPaginaRev', paginaAtualRev - 1)">← Anterior</button>
          <button v-for="n in paginasVisiveisRev" :key="n"
            class="btn-paginacao" :class="{ 'btn-paginacao-ativo': n === paginaAtualRev }"
            @click="$emit('irParaPaginaRev', n)">{{ n }}</button>
          <button class="btn-paginacao" :disabled="paginaAtualRev === totalPaginasRev"
            @click="$emit('irParaPaginaRev', paginaAtualRev + 1)">Próximo →</button>
          <button class="btn-paginacao" :disabled="paginaAtualRev === totalPaginasRev"
            @click="$emit('irParaPaginaRev', totalPaginasRev)">»</button>
          <span class="paginacao-info">Página {{ paginaAtualRev }} de {{ totalPaginasRev }}</span>
        </div>
      </div>

      <!-- Modal detalhes -->
      <div class="modal-overlay" v-if="modalDetalhesRev"
        @click.self="$emit('update:modalDetalhesRev', false)">
        <div class="modal-card modal-card-lg">
          <div class="modal-header detalhe-header">
            <div>
              <h2 class="detalhe-nome">Revisão — {{ veiculoRevisoes?.placa }}</h2>
              <p class="detalhe-meta-veiculo">{{ formatarData(revisaoDetalhes?.data_revisao) }}</p>
            </div>
            <button class="modal-fechar" @click="$emit('update:modalDetalhesRev', false)">✕</button>
          </div>
          <div class="modal-body detalhes-grid" v-if="revisaoDetalhes">
            <div class="detalhe-item">
              <span class="detalhe-label">🚗 Veículo</span>
              <span class="detalhe-valor">{{ veiculoRevisoes?.placa }} — {{ veiculoRevisoes?.marca }} {{ veiculoRevisoes?.modelo }}</span>
            </div>
            <div class="detalhe-item">
              <span class="detalhe-label">👤 Proprietário</span>
              <span class="detalhe-valor">{{ proprietarioVeiculos?.nome }}</span>
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
            <button class="btn btn-neutro" @click="$emit('update:modalDetalhesRev', false)">Fechar</button>
            <button class="btn btn-primario" @click="() => {
              $emit('update:modalDetalhesRev', false)
              $emit('abrirModalEditarRev', revisaoDetalhes)
            }">Editar revisão</button>
          </div>
        </div>
      </div>

      <!-- Modal exclusão -->
      <div class="modal-overlay" v-if="modalDeletarRev"
        @click.self="$emit('update:modalDeletarRev', false)">
        <div class="modal-card modal-card-sm">
          <div class="modal-header">
            <h2>Confirmar exclusão</h2>
            <button class="modal-fechar" @click="$emit('update:modalDeletarRev', false)">✕</button>
          </div>
          <p style="margin: 16px 24px;">
            Deseja excluir a revisão do veículo <strong>{{ veiculoRevisoes?.placa }}</strong>
            realizada em <strong>{{ formatarData(revisaoSelecionada?.data_revisao) }}</strong>?
          </p>
          <div class="modal-footer">
            <button class="btn btn-neutro" @click="$emit('update:modalDeletarRev', false)">Cancelar</button>
            <button class="btn btn-perigo" @click="$emit('deletarRev')" :disabled="salvandoRev">
              {{ salvandoRev ? 'Excluindo...' : 'Confirmar exclusão' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Offcanvas criar/editar revisão -->
      <div class="offcanvas-overlay" :class="{ ativo: panelRevisaoForm }"
        @click.self="$emit('fecharModalRev')">
        <aside class="offcanvas-panel" :class="{ aberto: panelRevisaoForm }">
          <div class="offcanvas-header">
            <h2>{{ modoEdicaoRev ? 'Editar revisão' : 'Nova revisão' }}</h2>
            <button class="offcanvas-fechar" @click="$emit('fecharModalRev')">✕</button>
          </div>
          <div class="offcanvas-body">
            <form @submit.prevent="$emit('salvarRev')" novalidate>

              <div class="form-row">
                <div class="form-grupo">
                  <label>Data da revisão *</label>
                  <input v-model="formRev.data_revisao" type="date"
                    :max="dataHoje" :min="dataMinima"
                    @blur="$emit('validarDataRev')"
                    @change="$emit('validarDataRev')"
                    required />
                  <span class="campo-erro" v-if="erroDataRev">{{ erroDataRev }}</span>
                </div>

                <!-- Quilometragem: máx 6 dígitos, apenas inteiros positivos -->
                <div class="form-grupo">
                  <label>Quilometragem (km) *</label>
                  <input
                    :value="formRev.quilometragem"
                    @input="onInputKm($event)"
                    @blur="validarKmLocal($event)"
                    type="text"
                    inputmode="numeric"
                    placeholder="Ex: 45000"
                    maxlength="6"
                    required
                  />
                  <span class="campo-erro" v-if="erroKmLocal">{{ erroKmLocal }}</span>
                  <span class="campo-info" v-else>Máximo: 999.999 km</span>
                </div>
              </div>

              <div class="form-grupo">
                <label>Descrição dos serviços *</label>
                <textarea v-model="formRev.descricao" rows="3"
                  placeholder="Ex: Troca de óleo, filtro de ar, revisão geral..."
                  maxlength="500" required></textarea>
                <span class="campo-contador">{{ formRev.descricao.length }}/500</span>
              </div>

              <div class="form-row">
                <div class="form-grupo">
                  <label>Responsável *</label>
                  <input v-model="formRev.responsavel" type="text"
                    placeholder="Ex: Oficina do João"
                    maxlength="100"
                    @keydown="$emit('bloquearResponsavelInvalido', $event)"
                    @blur="validarResponsavelLocal"
                    required />
                  <span class="campo-contador">{{ formRev.responsavel.length }}/100</span>
                  <span class="campo-erro" v-if="erroResponsavelLocal">{{ erroResponsavelLocal }}</span>
                  <span class="campo-info" v-else>Apenas letras, espaços e hífens</span>
                </div>

                <!-- Custo: preenchimento dinâmico, limite R$ 999.999,99 -->
                <div class="form-grupo">
                  <label>
                    Custo (R$) *
                    <span class="label-hint">máx. R$&nbsp;999.999,99</span>
                  </label>
                  <input
                    :value="custoExibicaoRev"
                    @input="onInputCustoLocal($event)"
                    @keydown="$emit('bloquearCustoExcedente', $event)"
                    @blur="validarCustoLocal"
                    type="text"
                    placeholder="Ex: R$ 350,00"
                    inputmode="numeric"
                    required
                  />
                  <span class="campo-erro" v-if="erroCustoRev">{{ erroCustoRev }}</span>
                  <span class="campo-info" v-else>Valor máximo: R$&nbsp;999.999,99</span>
                </div>
              </div>

              <p v-if="erroFormRev" class="form-erro">{{ erroFormRev }}</p>

              <div class="offcanvas-footer">
                <button type="button" class="btn btn-neutro" @click="$emit('fecharModalRev')">Cancelar</button>
                <button type="submit" class="btn btn-sucesso"
                  :disabled="salvandoRev || !!erroDataRev || !!erroCustoRev || !!erroKmLocal || !!erroResponsavelLocal">
                  {{ salvandoRev ? 'Salvando...' : modoEdicaoRev ? 'Salvar alterações' : 'Criar revisão' }}
                </button>
              </div>

            </form>
          </div>
        </aside>
      </div>

    </div>
  </transition>
</template>

<script setup>
import { ref } from 'vue'
import { alternarOrdenacao, iconeOrdenacao } from '@/composables/useOrdenacao'
import { formatarData, formatarMoeda, formatarKm } from '@/composables/useFormatters'

const props = defineProps({
  panelRevisoes:        { type: Boolean, required: true },
  veiculoRevisoes:      { type: Object,  default: null },
  proprietarioVeiculos: { type: Object,  default: null },
  carregandoRev:        { type: Boolean, required: true },
  salvandoRev:          { type: Boolean, required: true },
  mensagemRev:          { type: Object,  default: null },
  erroFormRev:          { type: String,  default: null },
  erroDataRev:          { type: String,  default: null },
  erroCustoRev:         { type: String,  default: null },
  formRev:              { type: Object,  required: true },
  custoExibicaoRev:     { type: String,  required: true },
  dataHoje:             { type: String,  required: true },
  dataMinima:           { type: String,  required: true },
  filtroTextoRev:       { type: String,  required: true },
  filtroInicioRev:      { type: String,  required: true },
  filtroFimRev:         { type: String,  required: true },
  paginaAtualRev:       { type: Number,  required: true },
  totalPaginasRev:      { type: Number,  required: true },
  paginasVisiveisRev:   { type: Array,   required: true },
  revisoesFiltradas:    { type: Array,   required: true },
  revisoesPaginadasRev: { type: Array,   required: true },
  totalCustosRev:       { type: [String, Number], required: true },
  panelRevisaoForm:     { type: Boolean, required: true },
  modalDetalhesRev:     { type: Boolean, required: true },
  modalDeletarRev:      { type: Boolean, required: true },
  modoEdicaoRev:        { type: Boolean, required: true },
  revisaoSelecionada:   { type: Object,  default: null },
  revisaoDetalhes:      { type: Object,  default: null },
  ordenacaoRev:         { type: Object,  required: true },
})

const emit = defineEmits([
  'fecharRevisoes',
  'abrirModalCriarRevisao', 'abrirModalEditarRev', 'abrirModalDetalhesRev',
  'confirmarDeletarRev', 'deletarRev', 'salvarRev', 'fecharModalRev',
  'limparFiltrosRev', 'irParaPaginaRev',
  'update:filtroTextoRev', 'update:filtroInicioRev', 'update:filtroFimRev',
  'update:modalDetalhesRev', 'update:modalDeletarRev',
  'validarDataRev', 'bloquearResponsavelInvalido',
  'onInputCustoRev', 'bloquearCustoExcedente',
])

// ── Erros locais ────────────────────────────────────────────
const erroKmLocal          = ref(null)
const erroResponsavelLocal = ref(null)

const CUSTO_MAXIMO = 999999.99

/**
 * Processa a máscara de moeda diretamente no filho usando o valor do evento.
 * Emite 'onInputCustoRev' com { exibicao, custo, erro } para o pai atualizar
 * custoExibicaoRev, formRev.custo e erroCustoRev de forma síncrona.
 */
function onInputCustoLocal(e) {
  const digits = e.target.value.replace(/\D/g, '').slice(0, 8)
  if (!digits) {
    e.target.value = ''
    emit('onInputCustoRev', { exibicao: '', custo: '', erro: null })
    return
  }
  const num = parseInt(digits, 10) / 100
  const exibicao = num.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
  const erro = num > CUSTO_MAXIMO
    ? `Valor máximo permitido: R$ 999.999,99. Atual: ${exibicao}`
    : null
  e.target.value = exibicao
  emit('onInputCustoRev', { exibicao, custo: num.toFixed(2), erro })
}

/** Quilometragem: aceita só dígitos, max 6 chars */
function onInputKm(e) {
  let v = e.target.value.replace(/\D/g, '').slice(0, 6)
  e.target.value = v
  props.formRev.quilometragem = v
  erroKmLocal.value = null
}

/** Valida km ao sair do campo */
function validarKmLocal(e) {
  const v = String(e.target.value).trim()
  if (!v) { erroKmLocal.value = 'Informe a quilometragem.'; return }
  const n = parseInt(v, 10)
  if (isNaN(n) || n < 0) { erroKmLocal.value = 'Quilometragem inválida.'; return }
  if (n > 999999)         { erroKmLocal.value = 'Quilometragem não pode ultrapassar 999.999 km.'; return }
  erroKmLocal.value = null
}

/** Valida responsável ao sair do campo */
function validarResponsavelLocal() {
  const v = props.formRev.responsavel.trim()
  if (!v) { erroResponsavelLocal.value = 'Informe o responsável.'; return }
  if (v.length < 2) { erroResponsavelLocal.value = 'Nome muito curto.'; return }
  erroResponsavelLocal.value = null
}

/** Dispara validação do custo ao sair do campo (reutiliza erro do pai) */
function validarCustoLocal() {
  if (!props.custoExibicaoRev) {
    // deixa o pai emitir o erro ao tentar salvar
  }
}
</script>

<style scoped>
.tabela-revisoes-wrapper { width: 100%; overflow-x: auto; }
.tabela-revisoes {
  width: 100%; min-width: 780px;
  table-layout: fixed; border-collapse: collapse;
}
.rcol-data        { width: 100px; }
.rcol-km          { width: 110px; }
.rcol-flex        { width: 110px; }
.rcol-responsavel { width: 160px; }
.rcol-custo       { width: 120px; }
.rcol-acoes       { width: 280px; }
.tabela-revisoes tbody tr td {
  vertical-align: middle; overflow: hidden;
  text-overflow: ellipsis; white-space: nowrap; padding: 8px 12px;
}

/* Placeholders em itálico */
.offcanvas-body input::placeholder,
.offcanvas-body textarea::placeholder {
  font-style: italic;
  color: #9ca3af;
}
</style>