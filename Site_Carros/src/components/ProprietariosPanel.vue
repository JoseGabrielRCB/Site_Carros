<template>
  <div class="pagina">

    <!-- Nível 3: Revisões -->
    <RevisoesPanel
      :panelRevisoes="panelRevisoes"
      :veiculoRevisoes="veiculoRevisoes"
      :proprietarioVeiculos="proprietarioVeiculos"
      :carregandoRev="carregandoRev"
      :salvandoRev="salvandoRev"
      :mensagemRev="mensagemRev"
      :erroFormRev="erroFormRev"
      :erroDataRev="erroDataRev"
      :erroCustoRev="erroCustoRev"
      :formRev="formRev"
      :custoExibicaoRev="custoExibicaoRev"
      :dataHoje="dataHoje"
      :dataMinima="dataMinima"
      :filtroTextoRev="filtroTextoRev"
      :filtroInicioRev="filtroInicioRev"
      :filtroFimRev="filtroFimRev"
      :paginaAtualRev="paginaAtualRev"
      :totalPaginasRev="totalPaginasRev"
      :paginasVisiveisRev="paginasVisiveisRev"
      :revisoesFiltradas="revisoesFiltradas"
      :revisoesPaginadasRev="revisoesPaginadasRev"
      :totalCustosRev="totalCustosRev"
      :panelRevisaoForm="panelRevisaoForm"
      :modalDetalhesRev="modalDetalhesRev"
      :modalDeletarRev="modalDeletarRev"
      :modoEdicaoRev="modoEdicaoRev"
      :revisaoSelecionada="revisaoSelecionada"
      :revisaoDetalhes="revisaoDetalhes"
      :ordenacaoRev="ordenacaoRev"
      @fecharRevisoes="fecharRevisoes"
      @abrirModalCriarRevisao="abrirModalCriarRevisao"
      @abrirModalEditarRev="abrirModalEditarRev"
      @abrirModalDetalhesRev="abrirModalDetalhesRev"
      @confirmarDeletarRev="confirmarDeletarRev"
      @deletarRev="deletarRev"
      @salvarRev="salvarRev"
      @fecharModalRev="fecharModalRev"
      @limparFiltrosRev="limparFiltrosRev"
      @irParaPaginaRev="irParaPaginaRev"
      @validarDataRev="validarDataRev"
      @bloquearResponsavelInvalido="bloquearResponsavelInvalido"
      @onInputCustoRev="onInputCustoRev"
      @bloquearCustoExcedente="bloquearCustoExcedente"
      @update:filtroTextoRev="filtroTextoRev = $event"
      @update:filtroInicioRev="filtroInicioRev = $event"
      @update:filtroFimRev="filtroFimRev = $event"
      @update:paginaAtualRev="paginaAtualRev = $event"
      @update:modalDetalhesRev="modalDetalhesRev = $event"
      @update:modalDeletarRev="modalDeletarRev = $event"
      @update:panelRevisaoForm="panelRevisaoForm = $event"
      @update:custoExibicaoRev="custoExibicaoRev = $event"
      @update:erroCustoRev="erroCustoRev = $event"
    />

    <!-- Nível 2: Veículos -->
    <VeiculosPanel
      :panelVeiculos="panelVeiculos"
      :panelRevisoes="panelRevisoes"
      :proprietarioVeiculos="proprietarioVeiculos"
      :carregandoVei="carregandoVei"
      :salvandoVei="salvandoVei"
      :mensagemVei="mensagemVei"
      :erroFormVei="erroFormVei"
      :erroPlacaVei="erroPlacaVei"
      :formVei="formVei"
      :anoAtual="anoAtual"
      :filtroTextoVei="filtroTextoVei"
      :filtroTipoVei="filtroTipoVei"
      :paginaAtualVei="paginaAtualVei"
      :totalPaginasVei="totalPaginasVei"
      :paginasVisiveisVei="paginasVisiveisVei"
      :veiculosFiltradosVei="veiculosFiltradosVei"
      :veiculosPaginadosVei="veiculosPaginadosVei"
      :panelVeiculoForm="panelVeiculoForm"
      :modalDetalhesVei="modalDetalhesVei"
      :modalDeletarVei="modalDeletarVei"
      :modoEdicaoVei="modoEdicaoVei"
      :veiculoSelecionadoVei="veiculoSelecionadoVei"
      :veiculoDetalhes="veiculoDetalhes"
      :modelosDisponiveisVei="modelosDisponiveisVei"
      :ordenacaoVei="ordenacaoVei"
      @fecharVeiculos="fecharVeiculos"
      @abrirModalCriarVeiculo="abrirModalCriarVeiculo"
      @abrirRevisoes="abrirRevisoes"
      @abrirModalDetalhesVei="abrirModalDetalhesVei"
      @abrirModalEditarVeiculo="abrirModalEditarVeiculo"
      @confirmarDeletarVei="confirmarDeletarVei"
      @deletarVei="deletarVei"
      @salvarVeiculo="salvarVeiculo"
      @fecharModalVeiculo="fecharModalVeiculo"
      @limparFiltrosVei="limparFiltrosVei"
      @irParaPaginaVei="irParaPaginaVei"
      @inputPlaca="aplicarMascaraPlaca($event); formVei.placa = $event.target.value"
      @bloquearPlacaInvalida="bloquearPlacaInvalida"
      @validarPlaca="validarPlaca"
      @updateFormVei="(campo, val) => { formVei[campo] = val }"
      @update:filtroTextoVei="filtroTextoVei = $event"
      @update:filtroTipoVei="filtroTipoVei = $event"
      @update:modalDetalhesVei="modalDetalhesVei = $event"
      @update:modalDeletarVei="modalDeletarVei = $event"
    />

    <!-- Nível 1: Proprietários -->
    <div v-show="!panelVeiculos && !panelRevisoes">

      <div class="pagina-header">
        <h1>Proprietários</h1>
        <button class="btn btn-sucesso" @click="abrirModalCriar">+ Novo proprietário</button>
      </div>

      <p v-if="mensagem" :class="['alerta', mensagem.tipo === 'sucesso' ? 'alerta-sucesso' : 'alerta-erro']">
        {{ mensagem.texto }}
      </p>

      <!-- Barra de busca: sempre visível — sem v-if para o input nunca ser desmontado -->
      <div class="barra-busca">
        <div class="busca-campo-wrapper">
          <input
            :value="termoBusca"
            @input="termoBusca = $event.target.value"
            @keydown.enter.prevent="buscar"
            type="text"
            placeholder="Buscar por nome ou CPF… (Enter para pesquisar)"
            class="input-busca"
          />
          <button
            v-if="termoBusca"
            class="btn-limpar-busca"
            @mousedown.prevent
            @click="termoBusca = ''; buscar()"
            title="Limpar busca"
          >✕</button>
        </div>
        <button class="btn btn-primario btn-sm" @click="buscar">Buscar</button>
        <span class="busca-contador">{{ totalRegistros }} registro(s) encontrado(s)</span>
      </div>

      <p v-if="carregando" class="estado-loading">Carregando...</p>

      <div class="tabela-wrapper" v-if="!carregando">
        <table>
          <thead>
            <tr>
              <th class="col-ordenavel" @click="alternarOrdenacao(ordenacaoProp, 'nome')">
                Nome <span class="sort-icon">{{ iconeOrdenacao(ordenacaoProp, 'nome') }}</span>
              </th>
              <th class="col-ordenavel" @click="alternarOrdenacao(ordenacaoProp, 'cpf')">
                CPF <span class="sort-icon">{{ iconeOrdenacao(ordenacaoProp, 'cpf') }}</span>
              </th>
              <th class="col-ordenavel" @click="alternarOrdenacao(ordenacaoProp, 'genero')">
                Gênero <span class="sort-icon">{{ iconeOrdenacao(ordenacaoProp, 'genero') }}</span>
              </th>
              <th class="col-ordenavel" @click="alternarOrdenacao(ordenacaoProp, 'data_nascimento')">
                Nascimento <span class="sort-icon">{{ iconeOrdenacao(ordenacaoProp, 'data_nascimento') }}</span>
              </th>
              <th class="col-ordenavel" @click="alternarOrdenacao(ordenacaoProp, 'idade')">
                Idade <span class="sort-icon">{{ iconeOrdenacao(ordenacaoProp, 'idade') }}</span>
              </th>
              <th class="col-ordenavel" @click="alternarOrdenacao(ordenacaoProp, 'endereco')">
                Endereço <span class="sort-icon">{{ iconeOrdenacao(ordenacaoProp, 'endereco') }}</span>
              </th>
              <th class="col-ordenavel" @click="alternarOrdenacao(ordenacaoProp, 'total_veiculos')">
                Veículos <span class="sort-icon">{{ iconeOrdenacao(ordenacaoProp, 'total_veiculos') }}</span>
              </th>
              <th class="col-acoes-prop">Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="usuariosPaginados.length === 0">
              <td colspan="8" class="estado-vazio">Nenhum proprietário encontrado.</td>
            </tr>
            <tr v-for="u in usuariosPaginados" :key="u.id">
              <td>{{ u.nome }}</td>
              <td>{{ u.cpf }}</td>
              <td>
                <span :class="u.genero === 'M' ? 'badge badge-masculino' : 'badge badge-feminino'">
                  {{ u.genero_display }}
                </span>
              </td>
              <td>{{ formatarData(u.data_nascimento) }}</td>
              <td>{{ u.idade }} anos</td>
              <td>{{ u.endereco || '—' }}</td>
              <td><span class="badge badge-carro">{{ u.total_veiculos }}</span></td>
              <td>
                <div class="acoes-cell-prop">
                  <button class="btn btn-info btn-xs"     @click="abrirVeiculos(u)" title="Ver veículos">🚗</button>
                  <button class="btn btn-primario btn-xs" @click="abrirModalEditar(u)">Editar</button>
                  <button class="btn btn-perigo btn-xs"   @click="confirmarDeletar(u)">Excluir</button>
                </div>
              </td>
            </tr>
          </tbody>
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

      <!-- Offcanvas proprietário -->
      <div class="offcanvas-overlay" :class="{ ativo: panelAberto }" @click.self="fecharModal">
        <aside class="offcanvas-panel" :class="{ aberto: panelAberto }">
          <div class="offcanvas-header">
            <h2>{{ modoEdicao ? 'Editar proprietário' : 'Novo proprietário' }}</h2>
            <button class="offcanvas-fechar" @click="fecharModal" title="Fechar">✕</button>
          </div>
          <div class="offcanvas-body">
            <form @submit.prevent="salvar" novalidate>

              <div class="form-grupo">
                <label>Nome completo *</label>
                <input v-model="form.nome" type="text"
                  placeholder="Ex: João da Silva"
                  maxlength="100"
                  @blur="form.nome = form.nome.trim()"
                  required />
                <span class="campo-contador">{{ form.nome.length }}/100</span>
              </div>

              <div class="form-grupo">
                <label>CPF *</label>
                <input v-model="form.cpf" type="text"
                  placeholder="000.000.000-00"
                  maxlength="14"
                  @keydown="bloquearCpfInvalido"
                  @input="aplicarMascaraCpf"
                  @blur="validarCpf"
                  required />
                <span class="campo-erro" v-if="erroCpf">{{ erroCpf }}</span>
              </div>

              <!-- Gênero: botões de bolinha -->
              <div class="form-grupo">
                <label>Gênero *</label>
                <div class="genero-botoes">
                  <button type="button" class="genero-btn"
                    :class="{ 'genero-btn--ativo': form.genero === 'M', 'genero-btn--masculino': form.genero === 'M' }"
                    @click="form.genero = 'M'">
                    <span class="genero-bolinha">
                      <span class="genero-bolinha-inner" v-if="form.genero === 'M'"></span>
                    </span>
                    <span class="genero-icone">♂</span> Masculino
                  </button>
                  <button type="button" class="genero-btn"
                    :class="{ 'genero-btn--ativo': form.genero === 'F', 'genero-btn--feminino': form.genero === 'F' }"
                    @click="form.genero = 'F'">
                    <span class="genero-bolinha">
                      <span class="genero-bolinha-inner" v-if="form.genero === 'F'"></span>
                    </span>
                    <span class="genero-icone">♀</span> Feminino
                  </button>
                </div>
              </div>

              <div class="form-grupo">
                <label>Data de nascimento *</label>
                <input v-model="form.data_nascimento" type="date"
                  :max="dataMaxima"
                  @blur="validarIdade"
                  @change="validarIdade"
                  required />
                <span class="campo-erro" v-if="erroData">{{ erroData }}</span>
              </div>

              <!-- CEP + Endereço automático -->
              <div class="form-grupo">
                <label>CEP</label>
                <div class="cep-wrapper">
                  <input v-model="form.cep" type="text"
                    placeholder="00000-000"
                    maxlength="9"
                    @keydown="bloquearCepInvalido"
                    @input="aplicarMascaraCep"
                    @blur="buscarCep"
                    class="cep-input" />
                  <span class="cep-status" v-if="buscandoCep"><span class="cep-spinner"></span></span>
                  <span class="cep-status cep-status--ok"  v-else-if="cepEncontrado">✓</span>
                  <span class="cep-status cep-status--err" v-else-if="erroCep">✗</span>
                </div>
                <span class="campo-erro" v-if="erroCep">{{ erroCep }}</span>
                <span class="campo-info" v-else>Digite o CEP para preencher o endereço automaticamente</span>
              </div>

              <div class="form-grupo">
                <label>Endereço</label>
                <input v-model="form.endereco" type="text"
                  placeholder="Preenchido automaticamente pelo CEP"
                  readonly class="input-disabled" />
                <span class="campo-info" v-if="form.endereco">Endereço obtido via CEP · somente leitura</span>
              </div>

              <p v-if="erroForm" class="form-erro">{{ erroForm }}</p>

              <div class="offcanvas-footer">
                <button type="button" class="btn btn-neutro" @click="fecharModal">Cancelar</button>
                <button type="submit" class="btn btn-sucesso" :disabled="salvando || !!erroCpf || !!erroData">
                  {{ salvando ? 'Salvando...' : modoEdicao ? 'Salvar alterações' : 'Criar proprietário' }}
                </button>
              </div>
            </form>
          </div>
        </aside>
      </div>

      <!-- Modal exclusão de proprietário -->
      <div class="modal-overlay" v-if="modalDeletar" @click.self="modalDeletar = false">
        <div class="modal-card modal-card-sm">
          <div class="modal-header">
            <h2>Confirmar exclusão</h2>
            <button class="modal-fechar" @click="modalDeletar = false">✕</button>
          </div>
          <p style="margin: 16px 24px;">
            Deseja excluir <strong>{{ usuarioSelecionado?.nome }}</strong>?
            Veículos e revisões vinculados serão removidos (CASCADE).
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
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { alternarOrdenacao, iconeOrdenacao } from '@/composables/useOrdenacao'
import { formatarData } from '@/composables/useFormatters'
import { useProprietarios } from '@/composables/useProprietarios'
import { useVeiculos } from '@/composables/useVeiculos'
import { useRevisoes } from '@/composables/useRevisoes'
import VeiculosPanel from './VeiculosPanel.vue'
import RevisoesPanel from './RevisoesPanel.vue'

// ── Proprietários ───────────────────────────────────────────
const {
  usuarios, carregando, salvando, mensagem, erroForm, erroCpf, erroData,
  panelAberto, modalDeletar, modoEdicao, usuarioSelecionado, termoBusca,
  paginaAtual, totalRegistros, form, ordenacaoProp,
  buscandoCep, erroCep, cepEncontrado,
  dataMaxima, usuariosPaginados, totalPaginas, paginasVisiveis,
  buscar, irParaPagina,
  abrirModalCriar, abrirModalEditar, fecharModal, salvar,
  confirmarDeletar, deletar,
  bloquearCpfInvalido, aplicarMascaraCpf, validarCpf, validarIdade,
  bloquearCepInvalido, aplicarMascaraCep, buscarCep,
} = useProprietarios()

// ── Veículos ────────────────────────────────────────────────
const {
  panelVeiculos, proprietarioVeiculos, veiculosDoProprietario,
  carregandoVei, salvandoVei, mensagemVei, erroFormVei, erroPlacaVei,
  panelVeiculoForm, modalDetalhesVei, modalDeletarVei,
  modoEdicaoVei, veiculoSelecionadoVei, veiculoDetalhes,
  filtroTextoVei, filtroTipoVei, paginaAtualVei, anoAtual, formVei, ordenacaoVei,
  modelosDisponiveisVei, veiculosFiltradosVei, totalPaginasVei,
  veiculosPaginadosVei, paginasVisiveisVei,
  abrirVeiculos, fecharVeiculos, irParaPaginaVei, limparFiltrosVei,
  abrirModalDetalhesVei, abrirModalCriarVeiculo, abrirModalEditarVeiculo,
  fecharModalVeiculo, confirmarDeletarVei, salvarVeiculo, deletarVei,
  bloquearPlacaInvalida, aplicarMascaraPlaca, validarPlaca,
} = useVeiculos(usuarios)

// ── Revisões ────────────────────────────────────────────────
const veiculoRevisoes = ref(null)

const {
  panelRevisoes, revisoes, carregandoRev, salvandoRev, mensagemRev,
  erroFormRev, erroDataRev, erroCustoRev, panelRevisaoForm,
  modalDetalhesRev, modalDeletarRev, modoEdicaoRev,
  revisaoSelecionada, revisaoDetalhes,
  filtroTextoRev, filtroInicioRev, filtroFimRev,
  paginaAtualRev, custoExibicaoRev, formRev, ordenacaoRev,
  dataHoje, dataMinima,
  revisoesFiltradas, totalPaginasRev, revisoesPaginadasRev,
  paginasVisiveisRev, totalCustosRev,
  abrirRevisoes, fecharRevisoes, irParaPaginaRev, limparFiltrosRev,
  abrirModalDetalhesRev, abrirModalCriarRevisao, abrirModalEditarRev,
  fecharModalRev, confirmarDeletarRev, salvarRev, deletarRev,
  validarDataRev, bloquearResponsavelInvalido,
  onInputCustoRev, bloquearCustoExcedente,
} = useRevisoes(veiculoRevisoes, proprietarioVeiculos)

onMounted(() => buscar())
</script>

<style>
@import '@/assets/styles/shared.css';
</style>

<style scoped>
.col-acoes-prop { width: 190px; min-width: 190px; }

/* Wrapper do campo de busca com botão X interno */
.busca-campo-wrapper {
  position: relative;
  flex: 1;
  max-width: 380px;
}
.busca-campo-wrapper .input-busca {
  width: 100%;
  padding-right: 32px; /* espaço para o X */
}
.btn-limpar-busca {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #9ca3af;
  font-size: 0.85rem;
  cursor: pointer;
  padding: 2px 4px;
  line-height: 1;
  border-radius: 3px;
  transition: color 0.15s;
}
.btn-limpar-busca:hover { color: #374151; }
</style>