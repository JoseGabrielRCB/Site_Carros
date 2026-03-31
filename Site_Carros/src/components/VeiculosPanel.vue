<template>
  <transition name="slide-veiculos">
    <div v-if="panelVeiculos && !panelRevisoes" class="veiculos-subpanel">

      <!-- Cabeçalho -->
      <div class="subpanel-header">
        <button class="btn-voltar" @click="$emit('fecharVeiculos')">← Voltar para Proprietários</button>
        <div class="subpanel-titulo">
          <span class="subpanel-badge">🚗 Veículos</span>
          <h2>
            {{ proprietarioVeiculos?.nome }}
            <span class="subpanel-sub">{{ proprietarioVeiculos?.cpf }}</span>
          </h2>
        </div>
        <button class="btn btn-sucesso btn-sm" @click="$emit('abrirModalCriarVeiculo')">+ Novo veículo</button>
      </div>

      <p v-if="mensagemVei" :class="['alerta', mensagemVei.tipo === 'sucesso' ? 'alerta-sucesso' : 'alerta-erro']">
        {{ mensagemVei.texto }}
      </p>

      <!-- Filtros -->
      <div class="filtros">
        <input :value="filtroTextoVei" @input="$emit('update:filtroTextoVei', $event.target.value)"
          class="filtro-input" type="text" placeholder="Buscar por placa, marca ou modelo..." />
        <select :value="filtroTipoVei" @change="$emit('update:filtroTipoVei', $event.target.value)" class="filtro-select">
          <option value="">Todos os tipos</option>
          <option value="Carro">Carro</option>
          <option value="Moto">Moto</option>
          <option value="Triciclo">Triciclo</option>
          <option value="Caminhão">Caminhão</option>
        </select>
        <button class="btn btn-neutro" v-if="filtroTextoVei || filtroTipoVei" @click="$emit('limparFiltrosVei')">
          Limpar filtros
        </button>
      </div>

      <p class="contador-resultados" v-if="!carregandoVei">
        {{ veiculosFiltradosVei.length }} veículo(s) encontrado(s)
      </p>
      <p v-if="carregandoVei" class="estado-loading">Carregando veículos...</p>

      <!-- Tabela -->
      <div class="tabela-veiculos-wrapper" v-if="!carregandoVei">
        <table class="tabela-veiculos">
          <colgroup>
            <col class="col-placa"> <col class="col-tipo">
            <col class="col-marcamodelo"> <col class="col-ano"> <col class="col-acoes-vei">
          </colgroup>
          <thead>
            <tr>
              <th class="col-ordenavel" @click="alternarOrdenacao(ordenacaoVei, 'placa')">
                Placa <span class="sort-icon">{{ iconeOrdenacao(ordenacaoVei, 'placa') }}</span>
              </th>
              <th class="col-ordenavel" @click="alternarOrdenacao(ordenacaoVei, 'tipo')">
                Tipo <span class="sort-icon">{{ iconeOrdenacao(ordenacaoVei, 'tipo') }}</span>
              </th>
              <th class="col-ordenavel" @click="alternarOrdenacao(ordenacaoVei, 'marca')">
                Marca / Modelo <span class="sort-icon">{{ iconeOrdenacao(ordenacaoVei, 'marca') }}</span>
              </th>
              <th class="col-ordenavel" @click="alternarOrdenacao(ordenacaoVei, 'ano')">
                Ano <span class="sort-icon">{{ iconeOrdenacao(ordenacaoVei, 'ano') }}</span>
              </th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="veiculosPaginadosVei.length === 0">
              <td colspan="5" class="estado-vazio">Nenhum veículo encontrado para este proprietário.</td>
            </tr>
            <tr v-for="v in veiculosPaginadosVei" :key="v.id">
              <td><strong>{{ v.placa }}</strong></td>
              <td><span :class="badgeTipo(v.tipo)">{{ v.tipo }}</span></td>
              <td>{{ v.marca }} {{ v.modelo }}</td>
              <td>{{ v.ano }}</td>
              <td>
                <div class="acoes-cell">
                  <button class="btn btn-info btn-sm"     @click="$emit('abrirRevisoes', v)">Revisões</button>
                  <button class="btn btn-primario btn-sm" @click="$emit('abrirModalDetalhesVei', v)">🔍</button>
                  <button class="btn btn-info btn-sm"     @click="$emit('abrirModalEditarVeiculo', v)">✏️</button>
                  <button class="btn btn-perigo btn-sm"   @click="$emit('confirmarDeletarVei', v)">Excluir</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div class="paginacao" v-if="totalPaginasVei > 1">
          <button class="btn-paginacao" :disabled="paginaAtualVei === 1" @click="$emit('irParaPaginaVei', 1)">«</button>
          <button class="btn-paginacao" :disabled="paginaAtualVei === 1" @click="$emit('irParaPaginaVei', paginaAtualVei - 1)">← Anterior</button>
          <button v-for="n in paginasVisiveisVei" :key="n"
            class="btn-paginacao" :class="{ 'btn-paginacao-ativo': n === paginaAtualVei }"
            @click="$emit('irParaPaginaVei', n)">{{ n }}</button>
          <button class="btn-paginacao" :disabled="paginaAtualVei === totalPaginasVei" @click="$emit('irParaPaginaVei', paginaAtualVei + 1)">Próximo →</button>
          <button class="btn-paginacao" :disabled="paginaAtualVei === totalPaginasVei" @click="$emit('irParaPaginaVei', totalPaginasVei)">»</button>
          <span class="paginacao-info">Página {{ paginaAtualVei }} de {{ totalPaginasVei }}</span>
        </div>
      </div>

      <!-- Modal detalhes -->
      <div class="modal-overlay" v-if="modalDetalhesVei" @click.self="$emit('update:modalDetalhesVei', false)">
        <div class="modal-card modal-card-lg">
          <div class="modal-header detalhe-header">
            <div>
              <h2 class="detalhe-nome">{{ veiculoDetalhes?.placa }}</h2>
              <p class="detalhe-meta-veiculo">{{ veiculoDetalhes?.marca }} {{ veiculoDetalhes?.modelo }} — {{ veiculoDetalhes?.ano }}</p>
            </div>
            <button class="modal-fechar" @click="$emit('update:modalDetalhesVei', false)">✕</button>
          </div>
          <div class="modal-body detalhes-grid" v-if="veiculoDetalhes">
            <div class="detalhe-item"><span class="detalhe-label">👤 Proprietário</span><span class="detalhe-valor">{{ proprietarioVeiculos?.nome }}</span></div>
            <div class="detalhe-item"><span class="detalhe-label">🏷️ Placa</span><span class="detalhe-valor">{{ veiculoDetalhes.placa }}</span></div>
            <div class="detalhe-item"><span class="detalhe-label">🚗 Tipo</span><span class="detalhe-valor">{{ veiculoDetalhes.tipo }}</span></div>
            <div class="detalhe-item"><span class="detalhe-label">🏭 Marca</span><span class="detalhe-valor">{{ veiculoDetalhes.marca }}</span></div>
            <div class="detalhe-item"><span class="detalhe-label">📋 Modelo</span><span class="detalhe-valor">{{ veiculoDetalhes.modelo }}</span></div>
            <div class="detalhe-item"><span class="detalhe-label">📅 Ano</span><span class="detalhe-valor">{{ veiculoDetalhes.ano }}</span></div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-neutro" @click="$emit('update:modalDetalhesVei', false)">Fechar</button>
            <button class="btn btn-primario" @click="() => { $emit('update:modalDetalhesVei', false); $emit('abrirModalEditarVeiculo', veiculoDetalhes) }">Editar veículo</button>
          </div>
        </div>
      </div>

      <!-- Modal exclusão -->
      <div class="modal-overlay" v-if="modalDeletarVei" @click.self="$emit('update:modalDeletarVei', false)">
        <div class="modal-card modal-card-sm">
          <div class="modal-header">
            <h2>Confirmar exclusão</h2>
            <button class="modal-fechar" @click="$emit('update:modalDeletarVei', false)">✕</button>
          </div>
          <p style="margin: 16px 24px;">
            Deseja excluir o veículo <strong>{{ veiculoSelecionadoVei?.marca }} {{ veiculoSelecionadoVei?.modelo }}</strong>
            ({{ veiculoSelecionadoVei?.placa }})? Todas as revisões vinculadas serão removidas.
          </p>
          <div class="modal-footer">
            <button class="btn btn-neutro" @click="$emit('update:modalDeletarVei', false)">Cancelar</button>
            <button class="btn btn-perigo" @click="$emit('deletarVei')" :disabled="salvandoVei">
              {{ salvandoVei ? 'Excluindo...' : 'Confirmar exclusão' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Offcanvas criar/editar veículo -->
      <div class="offcanvas-overlay" :class="{ ativo: panelVeiculoForm }" @click.self="$emit('fecharModalVeiculo')">
        <aside class="offcanvas-panel" :class="{ aberto: panelVeiculoForm }">
          <div class="offcanvas-header">
            <h2>{{ modoEdicaoVei ? 'Editar veículo' : 'Novo veículo' }}</h2>
            <button class="offcanvas-fechar" @click="$emit('fecharModalVeiculo')">✕</button>
          </div>
          <div class="offcanvas-body">
            <form @submit.prevent="$emit('salvarVeiculo')" novalidate>

              <!-- Placa: preenchimento dinâmico com traço automático -->
              <div class="form-grupo">
                <label>Placa *</label>
                <input
                  :value="formVei.placa"
                  @input="onInputPlaca($event)"
                  @keydown="bloquearPlacaLocal($event)"
                  @blur="$emit('validarPlaca')"
                  type="text"
                  placeholder="Ex: ABC-1234 ou ABC-1D23"
                  maxlength="8"
                  class="input-placa"
                  required
                />
                <span class="campo-info">Formato: ABC-1234 (antiga) ou ABC-1D23 (Mercosul)</span>
                <span class="campo-erro" v-if="erroPlacaVei">{{ erroPlacaVei }}</span>
              </div>

              <!-- Ano: máx 4 dígitos, só números, validação no blur -->
              <div class="form-grupo">
                <label>Ano *</label>
                <input
                  :value="formVei.ano"
                  @input="onInputAno($event)"
                  @blur="validarAnoLocal($event)"
                  type="text"
                  inputmode="numeric"
                  placeholder="Ex: 2020"
                  maxlength="4"
                  required
                />
                <span class="campo-erro" v-if="erroAnoLocal">{{ erroAnoLocal }}</span>
              </div>

              <div class="form-row">
                <div class="form-grupo">
                  <label>Marca *</label>
                  <select :value="formVei.marca" @change="$emit('updateFormVei', 'marca', $event.target.value)" required>
                    <option value="">Selecione a marca</option>
                    <option v-for="m in Object.keys(MARCA_MODELOS)" :key="m" :value="m">{{ m }}</option>
                  </select>
                </div>
                <div class="form-grupo">
                  <label>
                    Modelo *
                    <span class="label-hint" v-if="!formVei.marca">— selecione a marca primeiro</span>
                  </label>
                  <select :value="formVei.modelo" @change="$emit('updateFormVei', 'modelo', $event.target.value)"
                    :disabled="!formVei.marca" required>
                    <option value="">{{ formVei.marca ? 'Selecione o modelo' : 'Selecione a marca primeiro' }}</option>
                    <option v-for="m in modelosDisponiveisVei" :key="m" :value="m">{{ m }}</option>
                  </select>
                </div>
              </div>

              <div class="form-grupo" v-if="!modoEdicaoVei">
                <label>Tipo de veículo *</label>
                <select :value="formVei.tipo" @change="$emit('updateFormVei', 'tipo', $event.target.value)" required>
                  <option value="">Selecione o tipo</option>
                  <option value="carro">Carro</option>
                  <option value="moto">Moto</option>
                  <option value="triciclo">Triciclo</option>
                  <option value="caminhao">Caminhão</option>
                </select>
              </div>

              <template v-if="formVei.tipo === 'carro'">
                <div class="form-separador">Dados do carro</div>
                <div class="form-row">
                  <div class="form-grupo">
                    <label>Nº de portas *</label>
                    <input :value="formVei.numero_portas" @input="$emit('updateFormVei', 'numero_portas', $event.target.value)"
                      type="number" placeholder="Ex: 4" min="2" max="6" required />
                  </div>
                  <div class="form-grupo">
                    <label>Combustível *</label>
                    <select :value="formVei.tipo_combustivel" @change="$emit('updateFormVei', 'tipo_combustivel', $event.target.value)" required>
                      <option value="">Selecione</option>
                      <option v-for="c in ['Gasolina','Etanol','Flex','Diesel','Elétrico','Híbrido']" :key="c" :value="c">{{ c }}</option>
                    </select>
                  </div>
                </div>
                <div class="form-grupo">
                  <label>Ar condicionado</label>
                  <select :value="formVei.ar_condicionado" @change="$emit('updateFormVei', 'ar_condicionado', $event.target.value === 'true')">
                    <option :value="true">Sim</option>
                    <option :value="false">Não</option>
                  </select>
                </div>
              </template>

              <template v-if="formVei.tipo === 'moto'">
                <div class="form-separador">Dados da moto</div>
                <div class="form-row">
                  <div class="form-grupo">
                    <label>Cilindradas *</label>
                    <input :value="formVei.cilindradas" @input="$emit('updateFormVei', 'cilindradas', $event.target.value)"
                      type="number" placeholder="Ex: 150" min="50" required />
                  </div>
                  <div class="form-grupo">
                    <label>Tipo de partida *</label>
                    <select :value="formVei.tipo_partida" @change="$emit('updateFormVei', 'tipo_partida', $event.target.value)" required>
                      <option value="">Selecione</option>
                      <option v-for="p in ['Elétrica','Pedal','Ambos']" :key="p" :value="p">{{ p }}</option>
                    </select>
                  </div>
                </div>
                <div class="form-grupo">
                  <label>Refrigeração *</label>
                  <select :value="formVei.refrigeracao" @change="$emit('updateFormVei', 'refrigeracao', $event.target.value)" required>
                    <option value="">Selecione</option>
                    <option v-for="r in ['Ar','Água','Óleo']" :key="r" :value="r">{{ r }}</option>
                  </select>
                </div>
              </template>

              <template v-if="formVei.tipo === 'triciclo'">
                <div class="form-separador">Dados do triciclo</div>
                <div class="form-row">
                  <div class="form-grupo">
                    <label>Tipo de tração *</label>
                    <input :value="formVei.tipo_tracao" @input="$emit('updateFormVei', 'tipo_tracao', $event.target.value)"
                      type="text" placeholder="Ex: Dianteira" required />
                  </div>
                  <div class="form-grupo">
                    <label>Capacidade de carga (kg) *</label>
                    <input :value="formVei.capacidade_carga" @input="$emit('updateFormVei', 'capacidade_carga', $event.target.value)"
                      type="number" placeholder="Ex: 300" min="0" required />
                  </div>
                </div>
              </template>

              <template v-if="formVei.tipo === 'caminhao'">
                <div class="form-separador">Dados do caminhão</div>
                <div class="form-row">
                  <div class="form-grupo">
                    <label>Qtd. de eixos *</label>
                    <input :value="formVei.quantidade_eixos" @input="$emit('updateFormVei', 'quantidade_eixos', $event.target.value)"
                      type="number" placeholder="Ex: 2" min="2" required />
                  </div>
                  <div class="form-grupo">
                    <label>Capacidade (ton) *</label>
                    <input :value="formVei.capacidade_toneladas" @input="$emit('updateFormVei', 'capacidade_toneladas', $event.target.value)"
                      type="number" placeholder="Ex: 5.0" min="0" required />
                  </div>
                </div>
                <div class="form-grupo">
                  <label>Tipo de carroceria *</label>
                  <input :value="formVei.tipo_carroceria" @input="$emit('updateFormVei', 'tipo_carroceria', $event.target.value)"
                    type="text" placeholder="Ex: Baú, Graneleiro..." required />
                </div>
              </template>

              <p v-if="erroFormVei" class="form-erro">{{ erroFormVei }}</p>

              <div class="offcanvas-footer">
                <button type="button" class="btn btn-neutro" @click="$emit('fecharModalVeiculo')">Cancelar</button>
                <button type="submit" class="btn btn-sucesso" :disabled="salvandoVei || !!erroPlacaVei || !!erroAnoLocal">
                  {{ salvandoVei ? 'Salvando...' : modoEdicaoVei ? 'Salvar alterações' : 'Criar veículo' }}
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
import { badgeTipo } from '@/composables/useFormatters'
import { MARCA_MODELOS } from '@/composables/useVeiculos'

const props = defineProps({
  panelVeiculos:        { type: Boolean, required: true },
  panelRevisoes:        { type: Boolean, required: true },
  proprietarioVeiculos: { type: Object,  default: null },
  carregandoVei:        { type: Boolean, required: true },
  salvandoVei:          { type: Boolean, required: true },
  mensagemVei:          { type: Object,  default: null },
  erroFormVei:          { type: String,  default: null },
  erroPlacaVei:         { type: String,  default: null },
  formVei:              { type: Object,  required: true },
  anoAtual:             { type: Number,  required: true },
  filtroTextoVei:       { type: String,  required: true },
  filtroTipoVei:        { type: String,  required: true },
  paginaAtualVei:       { type: Number,  required: true },
  totalPaginasVei:      { type: Number,  required: true },
  paginasVisiveisVei:   { type: Array,   required: true },
  veiculosFiltradosVei: { type: Array,   required: true },
  veiculosPaginadosVei: { type: Array,   required: true },
  panelVeiculoForm:     { type: Boolean, required: true },
  modalDetalhesVei:     { type: Boolean, required: true },
  modalDeletarVei:      { type: Boolean, required: true },
  modoEdicaoVei:        { type: Boolean, required: true },
  veiculoSelecionadoVei:{ type: Object,  default: null },
  veiculoDetalhes:      { type: Object,  default: null },
  modelosDisponiveisVei:{ type: Array,   required: true },
  ordenacaoVei:         { type: Object,  required: true },
})

const emit = defineEmits([
  'fecharVeiculos', 'abrirModalCriarVeiculo', 'abrirRevisoes',
  'abrirModalDetalhesVei', 'abrirModalEditarVeiculo',
  'confirmarDeletarVei', 'deletarVei', 'salvarVeiculo', 'fecharModalVeiculo',
  'limparFiltrosVei', 'irParaPaginaVei',
  'inputPlaca', 'bloquearPlacaInvalida', 'validarPlaca',
  'updateFormVei',
  'update:filtroTextoVei', 'update:filtroTipoVei',
  'update:modalDetalhesVei', 'update:modalDeletarVei',
])

// ── Erro de ano (local ao componente) ───────────────────────
const erroAnoLocal = ref(null)

/**
 * Máscara dinâmica de placa — aplicada localmente no filho.
 * Insere o traço automaticamente após as 3 primeiras letras.
 * Emite inputPlaca para o pai manter formVei.placa atualizado.
 */
function onInputPlaca(e) {
  let raw = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 7)
  const formatted = raw.length > 3 ? raw.slice(0, 3) + '-' + raw.slice(3) : raw
  e.target.value = formatted
  emit('inputPlaca', e)
}

/** Permite apenas dígitos, limita a 4 chars */
function onInputAno(e) {
  let v = e.target.value.replace(/\D/g, '').slice(0, 4)
  e.target.value = v
  emit('updateFormVei', 'ano', v)
  erroAnoLocal.value = null
}

/** Valida ao sair do campo */
function validarAnoLocal(e) {
  const v = String(e.target.value).trim()
  if (!v) { erroAnoLocal.value = 'Informe o ano.'; return }
  const n = parseInt(v, 10)
  if (isNaN(n) || v.length < 4) { erroAnoLocal.value = 'Ano inválido — informe 4 dígitos.'; return }
  if (n < 1900) { erroAnoLocal.value = 'Ano não pode ser anterior a 1900.'; return }
  if (n > props.anoAtual) { erroAnoLocal.value = `Ano não pode ser maior que ${props.anoAtual}.`; return }
  erroAnoLocal.value = null
}

/**
 * Bloqueia apenas caracteres claramente inválidos para placa.
 * Letras, números e traço são permitidos — a máscara cuida da formatação.
 */
function bloquearPlacaLocal(e) {
  const controle = ['Backspace','Delete','Tab','ArrowLeft','ArrowRight','Home','End']
  if (e.ctrlKey || e.metaKey || controle.includes(e.key)) return
  if (!/^[a-zA-Z0-9\-]$/.test(e.key)) e.preventDefault()
}
</script>

<style scoped>
.tabela-veiculos-wrapper { width: 100%; overflow-x: auto; }
.tabela-veiculos { width: 100%; min-width: 620px; table-layout: fixed; border-collapse: collapse; }
.col-placa       { width: 110px; }
.col-tipo        { width: 100px; }
.col-marcamodelo { width: auto; }
.col-ano         { width: 80px; }
.col-acoes-vei   { width: 340px; }
.tabela-veiculos tbody tr td {
  vertical-align: middle; overflow: hidden;
  text-overflow: ellipsis; white-space: nowrap; padding: 8px 12px;
}

/* Placeholders em itálico em todos os campos do offcanvas */
.offcanvas-body input::placeholder,
.offcanvas-body textarea::placeholder {
  font-style: italic;
  color: #9ca3af;
}

.input-placa { text-transform: uppercase; letter-spacing: 1px; }
</style>