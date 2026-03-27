<template>
  <div class="pagina">

    <!-- ══════════════════════════════════════════════════════════
         PAINEL DE REVISÕES (subjanela embutida, sem navegação)
         Aparece quando panelRevisoes === true, sobrepondo a lista
         de veículos. Botão "← Voltar" fecha e retorna à lista.
    ══════════════════════════════════════════════════════════ -->
    <transition name="slide-revisoes">
      <div v-if="panelRevisoes" class="revisoes-subpanel">

        <!-- Cabeçalho da subjanela -->
        <div class="subpanel-header">
          <button class="btn-voltar" @click="fecharRevisoes">← Voltar para Veículos</button>
          <div class="subpanel-titulo">
            <span class="subpanel-badge">🔍 Revisões</span>
            <h2>
              {{ veiculoRevisoes?.placa }}
              <span class="subpanel-sub">{{ veiculoRevisoes?.marca }} {{ veiculoRevisoes?.modelo }}</span>
            </h2>
          </div>
          <button class="btn btn-sucesso btn-sm" @click="abrirModalCriarRevisao">+ Nova revisão</button>
        </div>

        <!-- Alerta de revisões -->
        <p v-if="mensagemRev" :class="['alerta', mensagemRev.tipo === 'sucesso' ? 'alerta-sucesso' : 'alerta-erro']">
          {{ mensagemRev.texto }}
        </p>

        <!-- Filtros de revisão -->
        <div class="filtros">
          <input v-model="filtroTextoRev" class="filtro-input" type="text" placeholder="Buscar por responsável ou descrição..." />
          <input v-model="filtroInicioRev" class="filtro-input" type="date" title="Data inicial" />
          <input v-model="filtroFimRev"   class="filtro-input" type="date" title="Data final" />
          <button class="btn btn-neutro" v-if="filtroTextoRev || filtroInicioRev || filtroFimRev" @click="limparFiltrosRev">
            Limpar filtros
          </button>
        </div>

        <p class="contador-resultados" v-if="!carregandoRev">
          {{ revisoesFiltradas.length }} revisão(ões) encontrada(s)
        </p>

        <p v-if="carregandoRev" class="estado-loading">Carregando revisões...</p>

        <!-- Tabela de revisões -->
        <div class="tabela-revisoes-wrapper" v-if="!carregandoRev">
          <table class="tabela-revisoes">
            <colgroup>
              <col class="col-data">
              <col class="col-km">
              <col class="col-flex">
              <col class="col-responsavel">
              <col class="col-custo">
              <col class="col-acoes-rev">
            </colgroup>
            <thead>
              <tr>
                <th>Data</th>
                <th>KM</th>
                <th>Descrição</th>
                <th>Responsável</th>
                <th>Custo</th>
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
                    <button class="btn btn-info btn-sm"     @click="abrirModalDetalhesRev(r)">🔍 Detalhes</button>
                    <button class="btn btn-primario btn-sm" @click="abrirModalEditarRev(r)">Editar</button>
                    <button class="btn btn-perigo btn-sm"   @click="confirmarDeletarRev(r)">Excluir</button>
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
            <button class="btn-paginacao" :disabled="paginaAtualRev === 1" @click="irParaPaginaRev(1)">«</button>
            <button class="btn-paginacao" :disabled="paginaAtualRev === 1" @click="irParaPaginaRev(paginaAtualRev - 1)">← Anterior</button>
            <button v-for="n in paginasVisiveisRev" :key="n"
              class="btn-paginacao" :class="{ 'btn-paginacao-ativo': n === paginaAtualRev }"
              @click="irParaPaginaRev(n)">{{ n }}</button>
            <button class="btn-paginacao" :disabled="paginaAtualRev === totalPaginasRev" @click="irParaPaginaRev(paginaAtualRev + 1)">Próximo →</button>
            <button class="btn-paginacao" :disabled="paginaAtualRev === totalPaginasRev" @click="irParaPaginaRev(totalPaginasRev)">»</button>
            <span class="paginacao-info">Página {{ paginaAtualRev }} de {{ totalPaginasRev }}</span>
          </div>
        </div>

        <!-- Modal detalhes de revisão -->
        <div class="modal-overlay" v-if="modalDetalhesRev" @click.self="modalDetalhesRev = false">
          <div class="modal-card modal-card-lg">
            <div class="modal-header detalhe-header">
              <div>
                <h2 class="detalhe-nome">Revisão — {{ veiculoRevisoes?.placa }}</h2>
                <p class="detalhe-meta-revisao">{{ formatarData(revisaoDetalhes?.data_revisao) }}</p>
              </div>
              <button class="modal-fechar" @click="modalDetalhesRev = false">✕</button>
            </div>
            <div class="modal-body detalhes-grid" v-if="revisaoDetalhes">
              <div class="detalhe-item">
                <span class="detalhe-label">🚗 Veículo</span>
                <span class="detalhe-valor">{{ veiculoRevisoes?.placa }} — {{ veiculoRevisoes?.marca }} {{ veiculoRevisoes?.modelo }}</span>
              </div>
              <div class="detalhe-item">
                <span class="detalhe-label">👤 Proprietário</span>
                <span class="detalhe-valor">{{ veiculoRevisoes?.proprietario_nome }}</span>
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
              <button class="btn btn-neutro" @click="modalDetalhesRev = false">Fechar</button>
              <button class="btn btn-primario" @click="() => { modalDetalhesRev = false; abrirModalEditarRev(revisaoDetalhes) }">
                Editar revisão
              </button>
            </div>
          </div>
        </div>

        <!-- Modal exclusão de revisão -->
        <div class="modal-overlay" v-if="modalDeletarRev" @click.self="modalDeletarRev = false">
          <div class="modal-card modal-card-sm">
            <div class="modal-header">
              <h2>Confirmar exclusão</h2>
              <button class="modal-fechar" @click="modalDeletarRev = false">✕</button>
            </div>
            <p style="margin: 16px 0;">
              Deseja excluir a revisão do veículo <strong>{{ veiculoRevisoes?.placa }}</strong>
              realizada em <strong>{{ formatarData(revisaoSelecionada?.data_revisao) }}</strong>?
            </p>
            <div class="modal-footer">
              <button class="btn btn-neutro" @click="modalDeletarRev = false">Cancelar</button>
              <button class="btn btn-perigo" @click="deletarRev" :disabled="salvandoRev">
                {{ salvandoRev ? 'Excluindo...' : 'Confirmar exclusão' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Offcanvas de criação/edição de revisão -->
        <div class="offcanvas-overlay" :class="{ ativo: panelRevisaoForm }" @click.self="fecharModalRev">
          <aside class="offcanvas-panel" :class="{ aberto: panelRevisaoForm }">
            <div class="offcanvas-header">
              <h2>{{ modoEdicaoRev ? 'Editar revisão' : 'Nova revisão' }}</h2>
              <button class="offcanvas-fechar" @click="fecharModalRev">✕</button>
            </div>
            <div class="offcanvas-body">
              <form @submit.prevent="salvarRev" novalidate>

                <!-- Veículo fixado (não editável, já vem do contexto) -->
                <div class="form-grupo">
                  <label>Veículo</label>
                  <input type="text" :value="`${veiculoRevisoes?.placa} — ${veiculoRevisoes?.marca} ${veiculoRevisoes?.modelo}`" disabled class="input-disabled" />
                </div>

                <!-- Data + KM -->
                <div class="form-row">
                  <div class="form-grupo">
                    <label>Data da revisão *</label>
                    <input v-model="formRev.data_revisao" type="date"
                      :max="dataHoje" :min="dataMinima" @change="validarDataRev" required />
                    <span class="campo-erro" v-if="erroDataRev">{{ erroDataRev }}</span>
                  </div>
                  <div class="form-grupo">
                    <label>Quilometragem (km) *</label>
                    <input v-model="formRev.quilometragem" type="number" placeholder="45000" min="0" step="0.01" required />
                  </div>
                </div>

                <!-- Descrição -->
                <div class="form-grupo">
                  <label>Descrição dos serviços *</label>
                  <textarea
                    v-model="formRev.descricao"
                    rows="3"
                    placeholder="Ex: Troca de óleo, filtro de ar..."
                    maxlength="500"
                    required
                  ></textarea>
                  <span class="campo-contador">{{ formRev.descricao.length }}/500</span>
                </div>

                <!-- Responsável + Custo -->
                <div class="form-row">
                  <div class="form-grupo">
                    <label>Responsável *</label>
                    <input
                      v-model="formRev.responsavel"
                      type="text"
                      placeholder="Nome da oficina ou mecânico"
                      maxlength="100"
                      @keydown="bloquearResponsavelInvalido"
                      required
                    />
                    <span class="campo-contador">{{ formRev.responsavel.length }}/100</span>
                    <span class="campo-info">Apenas letras, espaços e hífens</span>
                  </div>
                  <div class="form-grupo">
                    <label>Custo (R$) *</label>
                    <input v-model="custoExibicaoRev" type="text" placeholder="R$ 0,00"
                      @input="onInputCustoRev" inputmode="numeric" required />
                    <span class="campo-erro" v-if="erroCustoRev">{{ erroCustoRev }}</span>
                  </div>
                </div>

                <p v-if="erroFormRev" class="form-erro">{{ erroFormRev }}</p>

                <div class="offcanvas-footer">
                  <button type="button" class="btn btn-neutro" @click="fecharModalRev">Cancelar</button>
                  <button type="submit" class="btn btn-sucesso"
                    :disabled="salvandoRev || !!erroDataRev">
                    {{ salvandoRev ? 'Salvando...' : modoEdicaoRev ? 'Salvar alterações' : 'Criar revisão' }}
                  </button>
                </div>

              </form>
            </div>
          </aside>
        </div>

      </div>
    </transition>

    <!-- ══════════════════════════════════════════════════════════
         TELA PRINCIPAL — Lista de Veículos
         v-show (não v-if) para preservar estado ao voltar do painel
    ══════════════════════════════════════════════════════════ -->
    <div v-show="!panelRevisoes">

      <div class="pagina-header">
        <h1>Veículos</h1>
        <button class="btn btn-sucesso" @click="abrirModalCriar">+ Novo veículo</button>
      </div>

      <p v-if="mensagem" :class="['alerta', mensagem.tipo === 'sucesso' ? 'alerta-sucesso' : 'alerta-erro']">
        {{ mensagem.texto }}
      </p>

      <div class="filtro-ativo-tag" v-if="filtroProprietarioNome">
        <span class="filtro-ativo-icone">👤</span>
        <span class="filtro-ativo-texto">Exibindo veículos de: <strong>{{ filtroProprietarioNome }}</strong></span>
        <button class="filtro-ativo-limpar" @click="limparFiltroProprietario">✕ Limpar filtro</button>
      </div>

      <div class="filtros">
        <input v-model="filtroTexto" class="filtro-input" type="text" placeholder="Buscar por placa, marca ou modelo..." />
        <select v-model="filtroTipo" class="filtro-select">
          <option value="">Todos os tipos</option>
          <option value="Carro">Carro</option>
          <option value="Moto">Moto</option>
          <option value="Triciclo">Triciclo</option>
          <option value="Caminhão">Caminhão</option>
        </select>
      </div>

      <p v-if="carregando" class="estado-loading">Carregando...</p>

      <div class="tabela-wrapper" v-if="!carregando">
        <table>
          <thead>
            <tr>
              <th>Placa</th>
              <th>Tipo</th>
              <th>Marca / Modelo</th>
              <th>Ano</th>
              <th>Proprietário</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="veiculosPaginados.length === 0">
              <td colspan="6" class="estado-vazio">
                <span v-if="filtroProprietarioNome">Nenhum veículo encontrado para <strong>{{ filtroProprietarioNome }}</strong>.</span>
                <span v-else>Nenhum veículo encontrado.</span>
              </td>
            </tr>
            <tr v-for="v in veiculosPaginados" :key="v.id">
              <td><strong>{{ v.placa }}</strong></td>
              <td><span :class="badgeTipo(v.tipo)">{{ v.tipo }}</span></td>
              <td>{{ v.marca }} {{ v.modelo }}</td>
              <td>{{ v.ano }}</td>
              <td>{{ v.proprietario_nome }}</td>
              <td class="acoes">
                <button class="btn btn-info btn-sm" @click="abrirRevisoes(v)" title="Ver revisões">🔍 Ver</button>
                <button class="btn btn-primario btn-sm" @click="abrirModalEditar(v)">Editar</button>
                <button class="btn btn-perigo btn-sm" @click="confirmarDeletar(v)">Excluir</button>
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

      <!-- Offcanvas de veículo (criar / editar) -->
      <div class="offcanvas-overlay" :class="{ ativo: panelAberto }" @click.self="fecharModal">
        <aside class="offcanvas-panel" :class="{ aberto: panelAberto }">

          <div class="offcanvas-header">
            <h2>{{ modoEdicao ? 'Editar veículo' : 'Novo veículo' }}</h2>
            <button class="offcanvas-fechar" @click="fecharModal">✕</button>
          </div>

          <div class="offcanvas-body">
            <form @submit.prevent="salvar" novalidate>

              <!-- Proprietário -->
              <div class="form-grupo" style="position: relative;">
                <label>Proprietário *</label>
                <input
                  v-model="termoBuscaProprietario"
                  type="text"
                  placeholder="Buscar por nome ou CPF..."
                  class="input-busca-proprietario"
                  @input="onInputProprietario"
                  @focus="mostrarDropdownProprietario = true"
                  autocomplete="off"
                />
                <ul v-if="mostrarDropdownProprietario && proprietariosFiltradosForm.length > 0" class="dropdown-proprietario">
                  <li v-for="u in proprietariosFiltradosForm" :key="u.id"
                    @mousedown.prevent="selecionarProprietario(u)" class="dropdown-proprietario-item">
                    <span class="dp-nome">{{ u.nome }}</span>
                    <span class="dp-cpf">{{ u.cpf }}</span>
                  </li>
                </ul>
                <div v-if="mostrarDropdownProprietario && termoBuscaProprietario && proprietariosFiltradosForm.length === 0"
                  class="dropdown-proprietario dropdown-vazio">Nenhum proprietário encontrado.</div>
                <span class="campo-erro" v-if="erroProprietario">{{ erroProprietario }}</span>
              </div>

              <!-- Placa -->
              <div class="form-grupo">
                <label>Placa *</label>
                <input
                  v-model="form.placa"
                  type="text"
                  placeholder="ABC-1234 ou ABC1D23"
                  maxlength="8"
                  @keydown="bloquearPlacaInvalida"
                  @input="aplicarMascaraPlaca"
                  @blur="validarPlaca"
                  required
                />
                <span class="campo-info">Formato: ABC-1234 (antiga) ou ABC-1D23 (Mercosul) · máx. 8 chars</span>
                <span class="campo-erro" v-if="erroPlaca">{{ erroPlaca }}</span>
              </div>

              <!-- Ano -->
              <div class="form-grupo">
                <label>Ano *</label>
                <input v-model="form.ano" type="number" placeholder="2020" min="1900" :max="anoAtual" required />
              </div>

              <!-- Marca / Modelo em cascata -->
              <div class="form-row">
                <div class="form-grupo">
                  <label>Marca *</label>
                  <select v-model="form.marca" required>
                    <option value="">Selecione a marca</option>
                    <option v-for="m in Object.keys(MARCA_MODELOS)" :key="m" :value="m">{{ m }}</option>
                  </select>
                </div>
                <div class="form-grupo">
                  <label>
                    Modelo *
                    <span class="label-hint" v-if="!form.marca">— selecione a marca primeiro</span>
                  </label>
                  <select v-model="form.modelo" :disabled="!form.marca" required>
                    <option value="">{{ form.marca ? 'Selecione o modelo' : 'Selecione a marca primeiro' }}</option>
                    <option v-for="m in modelosDisponiveis" :key="m" :value="m">{{ m }}</option>
                  </select>
                </div>
              </div>

              <!-- Tipo (só na criação) -->
              <div class="form-grupo" v-if="!modoEdicao">
                <label>Tipo de veículo *</label>
                <select v-model="form.tipo" required>
                  <option value="">Selecione o tipo</option>
                  <option value="carro">Carro</option>
                  <option value="moto">Moto</option>
                  <option value="triciclo">Triciclo</option>
                  <option value="caminhao">Caminhão</option>
                </select>
              </div>

              <!-- Campos extras por tipo -->
              <template v-if="form.tipo === 'carro'">
                <div class="form-separador">Dados do carro</div>
                <div class="form-row">
                  <div class="form-grupo">
                    <label>Nº de portas *</label>
                    <input v-model="form.numero_portas" type="number" placeholder="4" min="2" max="6" required />
                  </div>
                  <div class="form-grupo">
                    <label>Combustível *</label>
                    <select v-model="form.tipo_combustivel" required>
                      <option value="">Selecione</option>
                      <option value="Gasolina">Gasolina</option>
                      <option value="Etanol">Etanol</option>
                      <option value="Flex">Flex</option>
                      <option value="Diesel">Diesel</option>
                      <option value="Elétrico">Elétrico</option>
                      <option value="Híbrido">Híbrido</option>
                    </select>
                  </div>
                </div>
                <div class="form-grupo">
                  <label>Ar condicionado</label>
                  <select v-model="form.ar_condicionado">
                    <option :value="true">Sim</option>
                    <option :value="false">Não</option>
                  </select>
                </div>
              </template>

              <template v-if="form.tipo === 'moto'">
                <div class="form-separador">Dados da moto</div>
                <div class="form-row">
                  <div class="form-grupo">
                    <label>Cilindradas *</label>
                    <input v-model="form.cilindradas" type="number" placeholder="150" min="50" required />
                  </div>
                  <div class="form-grupo">
                    <label>Tipo de partida *</label>
                    <select v-model="form.tipo_partida" required>
                      <option value="">Selecione</option>
                      <option value="Elétrica">Elétrica</option>
                      <option value="Pedal">Pedal</option>
                      <option value="Ambos">Ambos</option>
                    </select>
                  </div>
                </div>
                <div class="form-grupo">
                  <label>Refrigeração *</label>
                  <select v-model="form.refrigeracao" required>
                    <option value="">Selecione</option>
                    <option value="Ar">Ar</option>
                    <option value="Água">Água</option>
                    <option value="Óleo">Óleo</option>
                  </select>
                </div>
              </template>

              <template v-if="form.tipo === 'triciclo'">
                <div class="form-separador">Dados do triciclo</div>
                <div class="form-row">
                  <div class="form-grupo">
                    <label>Tipo de tração *</label>
                    <input v-model="form.tipo_tracao" type="text" placeholder="Dianteira" required />
                  </div>
                  <div class="form-grupo">
                    <label>Capacidade de carga (kg) *</label>
                    <input v-model="form.capacidade_carga" type="number" placeholder="300" min="0" required />
                  </div>
                </div>
              </template>

              <template v-if="form.tipo === 'caminhao'">
                <div class="form-separador">Dados do caminhão</div>
                <div class="form-row">
                  <div class="form-grupo">
                    <label>Qtd. de eixos *</label>
                    <input v-model="form.quantidade_eixos" type="number" placeholder="2" min="2" required />
                  </div>
                  <div class="form-grupo">
                    <label>Capacidade (ton) *</label>
                    <input v-model="form.capacidade_toneladas" type="number" placeholder="5" min="0" required />
                  </div>
                </div>
                <div class="form-grupo">
                  <label>Tipo de carroceria *</label>
                  <input v-model="form.tipo_carroceria" type="text" placeholder="Baú, Graneleiro..." required />
                </div>
              </template>

              <p v-if="erroForm" class="form-erro">{{ erroForm }}</p>

              <div class="offcanvas-footer">
                <button type="button" class="btn btn-neutro" @click="fecharModal">Cancelar</button>
                <button type="submit" class="btn btn-sucesso"
                  :disabled="salvando || !!erroPlaca || !!erroProprietario">
                  {{ salvando ? 'Salvando...' : modoEdicao ? 'Salvar alterações' : 'Criar veículo' }}
                </button>
              </div>

            </form>
          </div>
        </aside>
      </div>

      <!-- Modal de exclusão de veículo -->
      <div class="modal-overlay" v-if="modalDeletar" @click.self="modalDeletar = false">
        <div class="modal-card modal-card-sm">
          <div class="modal-header">
            <h2>Confirmar exclusão</h2>
            <button class="modal-fechar" @click="modalDeletar = false">✕</button>
          </div>
          <p style="margin: 16px 0;">
            Deseja excluir o veículo <strong>{{ veiculoSelecionado?.marca }} {{ veiculoSelecionado?.modelo }}</strong>
            ({{ veiculoSelecionado?.placa }})? Todas as revisões vinculadas serão removidas.
          </p>
          <div class="modal-footer">
            <button class="btn btn-neutro" @click="modalDeletar = false">Cancelar</button>
            <button class="btn btn-perigo" @click="deletar" :disabled="salvando">
              {{ salvando ? 'Excluindo...' : 'Confirmar exclusão' }}
            </button>
          </div>
        </div>
      </div>

    </div><!-- fim v-show veículos -->
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter }             from 'vue-router'
import api                                 from '@/services/api'

const route  = useRoute()
const router = useRouter()

// ══════════════════════════════════════════════════════════════
// ESTADO — Veículos
// ══════════════════════════════════════════════════════════════
const veiculos           = ref([])
const usuarios           = ref([])
const carregando         = ref(true)
const salvando           = ref(false)
const mensagem           = ref(null)
const erroForm           = ref(null)
const erroPlaca          = ref(null)
const erroProprietario   = ref(null)
const panelAberto        = ref(false)
const modalDeletar       = ref(false)
const modoEdicao         = ref(false)
const veiculoSelecionado = ref(null)
const filtroTexto        = ref('')
const filtroTipo         = ref('')
const anoAtual           = new Date().getFullYear()
const ITENS_POR_PAGINA   = 10
const paginaAtual        = ref(1)
const filtroProprietarioId   = ref(null)
const filtroProprietarioNome = ref('')
const termoBuscaProprietario    = ref('')
const mostrarDropdownProprietario = ref(false)

// ══════════════════════════════════════════════════════════════
// ESTADO — Subpainel de Revisões
// ══════════════════════════════════════════════════════════════
const panelRevisoes      = ref(false)
const veiculoRevisoes    = ref(null)   // veículo cujas revisões estão abertas
const revisoes           = ref([])
const carregandoRev      = ref(false)
const salvandoRev        = ref(false)
const mensagemRev        = ref(null)
const erroFormRev        = ref(null)
const erroDataRev        = ref(null)
const erroCustoRev       = ref(null)
const panelRevisaoForm   = ref(false)  // offcanvas criar/editar revisão
const modalDetalhesRev   = ref(false)
const modalDeletarRev    = ref(false)
const modoEdicaoRev      = ref(false)
const revisaoSelecionada = ref(null)
const revisaoDetalhes    = ref(null)
const filtroTextoRev     = ref('')
const filtroInicioRev    = ref('')
const filtroFimRev       = ref('')
const paginaAtualRev     = ref(1)
const ITENS_REV          = 10
const custoExibicaoRev   = ref('')
const dataHoje           = new Date().toISOString().split('T')[0]
const dataMinima         = '2020-12-01'

const formRevVazio = { veiculo: '', data_revisao: '', quilometragem: '', descricao: '', responsavel: '', custo: '' }
const formRev = ref({ ...formRevVazio })

// ══════════════════════════════════════════════════════════════
// MARCA → MODELO (cascata)
// ══════════════════════════════════════════════════════════════
const MARCA_MODELOS = {
  'Toyota':       ['Corolla', 'Hilux', 'Yaris', 'RAV4', 'Camry'],
  'Volkswagen':   ['Fusca', 'Golf', 'Polo', 'Gol', 'Tiguan'],
  'Ford':         ['Mustang', 'Ka', 'EcoSport', 'Ranger', 'Bronco'],
  'Ferrari':      ['F40', 'F50', '488 GTB', 'Roma', 'SF90'],
  'BMW':          ['Série 3', 'Série 5', 'X1', 'X5', 'M3'],
  'Mercedes-Benz':['Classe A', 'Classe C', 'GLA', 'GLE', 'AMG GT'],
  'Honda':        ['Civic', 'HR-V', 'Fit', 'CR-V', 'City'],
  'Chevrolet':    ['Camaro', 'Onix', 'Tracker', 'S10', 'Equinox'],
  'Tesla':        ['Model 3', 'Model S', 'Model X', 'Model Y', 'Cybertruck'],
  'Porsche':      ['911', 'Cayenne', 'Macan', 'Panamera', 'Taycan'],
  'Hyundai':      ['HB20', 'Creta', 'Tucson', 'i30', 'Azera'],
  'Audi':         ['A3', 'A4', 'Q3', 'Q5', 'TT'],
  'Lamborghini':  ['Huracán', 'Urus', 'Aventador', 'Revuelto', 'Sterrato'],
  'Nissan':       ['Skyline GT-R', 'Frontier', 'Kicks', 'Versa', 'Sentra'],
  'Fiat':         ['Fiat 500', 'Strada', 'Argo', 'Pulse', 'Toro'],
}

const formVazio = {
  proprietario: '', placa: '', marca: '', modelo: '', ano: '', tipo: '',
  numero_portas: '', tipo_combustivel: '', ar_condicionado: true,
  cilindradas: '', tipo_partida: '', refrigeracao: '',
  tipo_tracao: '', capacidade_carga: '',
  quantidade_eixos: '', capacidade_toneladas: '', tipo_carroceria: '',
}
const form = ref({ ...formVazio })

// modelosDisponiveis e watch devem vir APÓS a declaração de form
const modelosDisponiveis = computed(() =>
  form.value.marca ? (MARCA_MODELOS[form.value.marca] ?? []) : []
)
watch(() => form.value.marca, () => { form.value.modelo = '' })

// ══════════════════════════════════════════════════════════════
// COMPUTEDS — Veículos
// ══════════════════════════════════════════════════════════════
const proprietariosFiltradosForm = computed(() => {
  const termo = termoBuscaProprietario.value.toLowerCase().trim()
  if (!termo) return usuarios.value.slice(0, 8)
  return usuarios.value.filter(u =>
    u.nome.toLowerCase().includes(termo) || u.cpf.includes(termo)
  ).slice(0, 8)
})

const veiculosFiltrados = computed(() =>
  veiculos.value
    .filter(v => {
      if (filtroProprietarioId.value && v.proprietario !== Number(filtroProprietarioId.value)) return false
      const texto = filtroTexto.value.toLowerCase()
      const bateTexto = !texto || v.placa.toLowerCase().includes(texto) ||
        v.marca.toLowerCase().includes(texto) || v.modelo.toLowerCase().includes(texto)
      const bateTipo = !filtroTipo.value || v.tipo === filtroTipo.value
      return bateTexto && bateTipo
    })
    .sort((a, b) => a.placa.localeCompare(b.placa))
)

const totalPaginas = computed(() => Math.ceil(veiculosFiltrados.value.length / ITENS_POR_PAGINA))
const veiculosPaginados = computed(() => {
  const inicio = (paginaAtual.value - 1) * ITENS_POR_PAGINA
  return veiculosFiltrados.value.slice(inicio, inicio + ITENS_POR_PAGINA)
})
const paginasVisiveis = computed(() => {
  const total = totalPaginas.value, atual = paginaAtual.value
  let inicio = Math.max(1, atual - 2), fim = Math.min(total, inicio + 4)
  if (fim - inicio < 4) inicio = Math.max(1, fim - 4)
  const p = []; for (let i = inicio; i <= fim; i++) p.push(i); return p
})

watch([filtroTexto, filtroTipo, filtroProprietarioId], () => { paginaAtual.value = 1 })
const irParaPagina = (n) => { if (n >= 1 && n <= totalPaginas.value) paginaAtual.value = n }

// ══════════════════════════════════════════════════════════════
// COMPUTEDS — Revisões
// ══════════════════════════════════════════════════════════════
const revisoesFiltradas = computed(() =>
  revisoes.value
    .filter(r => {
      const txt = filtroTextoRev.value.toLowerCase()
      const bateTexto = !txt ||
        r.responsavel?.toLowerCase().includes(txt) ||
        r.descricao?.toLowerCase().includes(txt)
      return bateTexto &&
        (!filtroInicioRev.value || r.data_revisao >= filtroInicioRev.value) &&
        (!filtroFimRev.value    || r.data_revisao <= filtroFimRev.value)
    })
    .sort((a, b) => new Date(b.data_revisao) - new Date(a.data_revisao))
)

const totalPaginasRev = computed(() => Math.ceil(revisoesFiltradas.value.length / ITENS_REV))
const revisoesPaginadasRev = computed(() => {
  const i = (paginaAtualRev.value - 1) * ITENS_REV
  return revisoesFiltradas.value.slice(i, i + ITENS_REV)
})
const paginasVisiveisRev = computed(() => {
  const total = totalPaginasRev.value, atual = paginaAtualRev.value
  let ini = Math.max(1, atual - 2), fim = Math.min(total, ini + 4)
  if (fim - ini < 4) ini = Math.max(1, fim - 4)
  const p = []; for (let i = ini; i <= fim; i++) p.push(i); return p
})
const totalCustosRev = computed(() =>
  revisoesFiltradas.value.reduce((a, r) => a + parseFloat(r.custo || 0), 0).toFixed(2)
)

watch([filtroTextoRev, filtroInicioRev, filtroFimRev], () => { paginaAtualRev.value = 1 })
const irParaPaginaRev = (n) => { if (n >= 1 && n <= totalPaginasRev.value) paginaAtualRev.value = n }

// ══════════════════════════════════════════════════════════════
// MOUNTED
// ══════════════════════════════════════════════════════════════
onMounted(async () => {
  if (route.query.proprietario_id) {
    filtroProprietarioId.value   = route.query.proprietario_id
    filtroProprietarioNome.value = route.query.proprietario_nome || ''
  }
  try {
    const [resV, resU] = await Promise.all([api.get('veiculos/'), api.get('users/')])
    veiculos.value = resV.data; usuarios.value = resU.data
  } catch { exibirMensagem('Erro ao carregar dados.', 'erro') }
  finally { carregando.value = false }
})

// ══════════════════════════════════════════════════════════════
// AÇÕES — Subpainel de Revisões
// ══════════════════════════════════════════════════════════════
const abrirRevisoes = async (veiculo) => {
  veiculoRevisoes.value = veiculo
  panelRevisoes.value   = true
  filtroTextoRev.value  = ''
  filtroInicioRev.value = ''
  filtroFimRev.value    = ''
  paginaAtualRev.value  = 1
  carregandoRev.value   = true
  try {
    const { data } = await api.get(`revisoes/?veiculo_id=${veiculo.id}`)
    revisoes.value = data
  } catch { exibirMensagemRev('Erro ao carregar revisões.', 'erro') }
  finally { carregandoRev.value = false }
}

const fecharRevisoes = () => {
  panelRevisoes.value  = false
  veiculoRevisoes.value = null
  revisoes.value = []
  panelRevisaoForm.value = false
  modalDetalhesRev.value = false
  modalDeletarRev.value  = false
}

const limparFiltrosRev = () => {
  filtroTextoRev.value = ''; filtroInicioRev.value = ''; filtroFimRev.value = ''
}

const abrirModalDetalhesRev = (r) => { revisaoDetalhes.value = r; modalDetalhesRev.value = true }

const abrirModalCriarRevisao = () => {
  modoEdicaoRev.value = false
  formRev.value = { ...formRevVazio, veiculo: veiculoRevisoes.value.id }
  erroFormRev.value = erroDataRev.value = erroCustoRev.value = null
  custoExibicaoRev.value = ''
  panelRevisaoForm.value = true
}

const abrirModalEditarRev = (r) => {
  modoEdicaoRev.value = true; revisaoSelecionada.value = r
  formRev.value = {
    veiculo: r.veiculo, data_revisao: r.data_revisao,
    quilometragem: r.quilometragem, descricao: r.descricao,
    responsavel: r.responsavel, custo: r.custo
  }
  custoExibicaoRev.value = parseFloat(r.custo || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
  erroFormRev.value = erroDataRev.value = erroCustoRev.value = null
  panelRevisaoForm.value = true
}

const fecharModalRev = () => {
  panelRevisaoForm.value = false
  erroFormRev.value = erroDataRev.value = erroCustoRev.value = null
}

const confirmarDeletarRev = (r) => { revisaoSelecionada.value = r; modalDeletarRev.value = true }

const salvarRev = async () => {
  if (!validarDataRev()) return
  salvandoRev.value = true; erroFormRev.value = null
  try {
    if (modoEdicaoRev.value) {
      const { data } = await api.put(`revisoes/${revisaoSelecionada.value.id}/update/`, formRev.value)
      const idx = revisoes.value.findIndex(r => r.id === revisaoSelecionada.value.id)
      if (idx !== -1) revisoes.value[idx] = { ...revisoes.value[idx], ...data }
      exibirMensagemRev('Revisão atualizada com sucesso.', 'sucesso')
    } else {
      const { data } = await api.post('revisoes/creat/', formRev.value)
      revisoes.value.unshift({
        ...data,
        veiculo_placa: veiculoRevisoes.value.placa,
        veiculo_marca: veiculoRevisoes.value.marca,
        veiculo_modelo: veiculoRevisoes.value.modelo,
        proprietario_nome: veiculoRevisoes.value.proprietario_nome,
      })
      exibirMensagemRev('Revisão criada com sucesso.', 'sucesso')
    }
    fecharModalRev()
  } catch (e) {
    const erros = e.response?.data
    erroFormRev.value = erros ? Object.values(erros).flat().join(' ') : 'Erro ao salvar.'
  } finally { salvandoRev.value = false }
}

const deletarRev = async () => {
  salvandoRev.value = true
  try {
    await api.delete(`revisoes/${revisaoSelecionada.value.id}/delete/`)
    revisoes.value = revisoes.value.filter(r => r.id !== revisaoSelecionada.value.id)
    modalDeletarRev.value = false
    exibirMensagemRev('Revisão excluída com sucesso.', 'sucesso')
  } catch { exibirMensagemRev('Erro ao excluir revisão.', 'erro') }
  finally { salvandoRev.value = false }
}

// ══════════════════════════════════════════════════════════════
// AÇÕES — Veículos
// ══════════════════════════════════════════════════════════════
const limparFiltroProprietario = () => {
  filtroProprietarioId.value = null; filtroProprietarioNome.value = ''
  router.replace({ name: 'veiculos' })
}

const bloquearPlacaInvalida = (e) => {
  const permitidas = ['Backspace','Delete','Tab','ArrowLeft','ArrowRight','Home','End']
  if (e.ctrlKey || e.metaKey) return
  if (permitidas.includes(e.key)) return
  if (!/^[a-zA-Z0-9]$/.test(e.key)) e.preventDefault()
}

const aplicarMascaraPlaca = () => {
  let v = form.value.placa.toUpperCase().replace(/[^A-Z0-9-]/g, '')
  const limpo = v.replace(/-/g, '').slice(0, 7)
  v = limpo.length > 3 ? limpo.slice(0, 3) + '-' + limpo.slice(3) : limpo
  form.value.placa = v; erroPlaca.value = null
}

const validarPlaca = () => {
  const placa = form.value.placa.toUpperCase()
  if (!/^[A-Z]{3}-\d{4}$/.test(placa) && !/^[A-Z]{3}-\d[A-Z]\d{2}$/.test(placa)) {
    erroPlaca.value = 'Placa inválida. Use ABC-1234 ou ABC-1D23.'; return false
  }
  erroPlaca.value = null; return true
}

const onInputProprietario = () => { form.value.proprietario = ''; erroProprietario.value = null }
const selecionarProprietario = (u) => {
  form.value.proprietario = u.id
  termoBuscaProprietario.value = `${u.nome} — ${u.cpf}`
  mostrarDropdownProprietario.value = false; erroProprietario.value = null
}
const validarProprietarioExiste = () => {
  mostrarDropdownProprietario.value = false
  if (!form.value.proprietario) { erroProprietario.value = 'Selecione um proprietário válido.'; return false }
  erroProprietario.value = null; return true
}

const abrirModalCriar = () => {
  modoEdicao.value = false; form.value = { ...formVazio }
  erroForm.value = erroPlaca.value = erroProprietario.value = null
  termoBuscaProprietario.value = ''; mostrarDropdownProprietario.value = false
  panelAberto.value = true
}
const abrirModalEditar = (v) => {
  modoEdicao.value = true; veiculoSelecionado.value = v
  form.value = { ...formVazio, proprietario: v.proprietario, placa: v.placa,
    marca: v.marca, modelo: v.modelo, ano: v.ano, tipo: v.tipo.toLowerCase().replace('ã','a') }
  const prop = usuarios.value.find(u => u.id === v.proprietario)
  termoBuscaProprietario.value = prop ? `${prop.nome} — ${prop.cpf}` : ''
  erroForm.value = erroPlaca.value = erroProprietario.value = null
  mostrarDropdownProprietario.value = false; panelAberto.value = true
}
const fecharModal = () => {
  panelAberto.value = false; erroForm.value = erroPlaca.value = erroProprietario.value = null
  mostrarDropdownProprietario.value = false
}

const salvar = async () => {
  if (!validarProprietarioExiste() || !validarPlaca()) return
  salvando.value = true; erroForm.value = null
  try {
    if (modoEdicao.value) {
      const { data } = await api.put(`veiculos/${veiculoSelecionado.value.id}/update/`, {
        proprietario: form.value.proprietario, placa: form.value.placa,
        marca: form.value.marca, modelo: form.value.modelo, ano: form.value.ano,
      })
      const idx = veiculos.value.findIndex(v => v.id === veiculoSelecionado.value.id)
      if (idx !== -1) veiculos.value[idx] = { ...veiculos.value[idx], ...data }
      exibirMensagem(`Veículo ${data.placa} atualizado.`, 'sucesso')
    } else {
      const { data } = await api.post('veiculos/creat/', montarPayload())
      veiculos.value.push(data)
      exibirMensagem(`Veículo ${data.placa} criado.`, 'sucesso')
    }
    fecharModal()
  } catch (e) {
    const erros = e.response?.data
    erroForm.value = erros ? Object.values(erros).flat().join(' ') : 'Erro ao salvar.'
  } finally { salvando.value = false }
}

const montarPayload = () => {
  const base = { proprietario: form.value.proprietario, placa: form.value.placa,
    marca: form.value.marca, modelo: form.value.modelo, ano: form.value.ano, tipo: form.value.tipo }
  const extras = {
    carro:    { numero_portas: form.value.numero_portas, tipo_combustivel: form.value.tipo_combustivel, ar_condicionado: form.value.ar_condicionado },
    moto:     { cilindradas: form.value.cilindradas, tipo_partida: form.value.tipo_partida, refrigeracao: form.value.refrigeracao },
    triciclo: { tipo_tracao: form.value.tipo_tracao, capacidade_carga: form.value.capacidade_carga },
    caminhao: { quantidade_eixos: form.value.quantidade_eixos, capacidade_toneladas: form.value.capacidade_toneladas, tipo_carroceria: form.value.tipo_carroceria },
  }
  return { ...base, ...(extras[form.value.tipo] || {}) }
}

const confirmarDeletar = (v) => { veiculoSelecionado.value = v; modalDeletar.value = true }
const deletar = async () => {
  salvando.value = true
  try {
    await api.delete(`veiculos/${veiculoSelecionado.value.id}/delete/`)
    veiculos.value = veiculos.value.filter(v => v.id !== veiculoSelecionado.value.id)
    modalDeletar.value = false; exibirMensagem(`Veículo ${veiculoSelecionado.value.placa} excluído.`, 'sucesso')
  } catch { exibirMensagem('Erro ao excluir veículo.', 'erro') }
  finally { salvando.value = false }
}

// ══════════════════════════════════════════════════════════════
// VALIDAÇÕES — Revisão
// ══════════════════════════════════════════════════════════════
const validarDataRev = () => {
  const d = formRev.value.data_revisao; if (!d) return true
  if (d > dataHoje)   { erroDataRev.value = 'Não é permitido selecionar datas futuras.'; return false }
  if (d < dataMinima) { erroDataRev.value = 'Não são aceitas revisões anteriores a dezembro de 2020.'; return false }
  erroDataRev.value = null; return true
}

const onInputCustoRev = () => {
  const digits = custoExibicaoRev.value.replace(/\D/g, '')
  if (!digits) { custoExibicaoRev.value = ''; formRev.value.custo = ''; return }
  const num = parseInt(digits, 10) / 100
  formRev.value.custo     = num.toFixed(2)
  custoExibicaoRev.value  = num.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
  erroCustoRev.value = null
}

const bloquearResponsavelInvalido = (e) => {
  const permitidas = ['Backspace','Delete','Tab','ArrowLeft','ArrowRight','Home','End',' ']
  if (e.ctrlKey || e.metaKey) return
  if (permitidas.includes(e.key)) return
  if (!/^[\p{L}'\-]$/u.test(e.key)) e.preventDefault()
}

// ══════════════════════════════════════════════════════════════
// HELPERS
// ══════════════════════════════════════════════════════════════
const badgeTipo = (tipo) => {
  const mapa = { 'Carro':'badge badge-carro','Moto':'badge badge-moto','Triciclo':'badge badge-masculino','Caminhão':'badge badge-feminino' }
  return mapa[tipo] || 'badge'
}
const exibirMensagem    = (texto, tipo) => { mensagem.value    = { texto, tipo }; setTimeout(() => { mensagem.value    = null }, 4000) }
const exibirMensagemRev = (texto, tipo) => { mensagemRev.value = { texto, tipo }; setTimeout(() => { mensagemRev.value = null }, 4000) }
const formatarData  = (d) => { if (!d) return '—'; const [a,m,dia] = d.split('-'); return `${dia}/${m}/${a}` }
const formatarMoeda = (v) => Number(v).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
const formatarKm    = (k) => Number(k).toLocaleString('pt-BR') + ' km'
</script>

<style scoped>
/* ═══════════════════════════════════════════════════
   TRANSIÇÃO — subpainel de revisões desliza da direita
═══════════════════════════════════════════════════ */
.slide-revisoes-enter-active,
.slide-revisoes-leave-active {
  transition: transform 0.32s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.32s ease;
}
.slide-revisoes-enter-from,
.slide-revisoes-leave-to {
  transform: translateX(40px);
  opacity: 0;
}

/* ═══════════════════════════════════════════════════
   SUBPAINEL — cabeçalho e layout geral
═══════════════════════════════════════════════════ */
.revisoes-subpanel {
  padding-bottom: 40px;
}

.subpanel-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 0 18px;
  border-bottom: 2px solid #e5e7eb;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.btn-voltar {
  background: none;
  border: 1.5px solid #d1d5db;
  color: #374151;
  padding: 7px 14px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.88rem;
  font-weight: 600;
  transition: background 0.15s, border-color 0.15s;
  white-space: nowrap;
}
.btn-voltar:hover { background: #f3f4f6; border-color: #9ca3af; }

.subpanel-titulo {
  flex: 1;
  display: flex;
  align-items: baseline;
  gap: 10px;
  flex-wrap: wrap;
}
.subpanel-titulo h2 {
  font-size: 1.15rem;
  font-weight: 700;
  margin: 0;
  color: #111827;
  display: flex;
  align-items: baseline;
  gap: 8px;
  flex-wrap: wrap;
}
.subpanel-sub {
  font-size: 0.85rem;
  font-weight: 400;
  color: #6b7280;
}
.subpanel-badge {
  font-size: 0.75rem;
  font-weight: 600;
  background: #eff6ff;
  color: #2563eb;
  padding: 3px 8px;
  border-radius: 20px;
  border: 1px solid #bfdbfe;
  white-space: nowrap;
}

/* ═══════════════════════════════════════════════════
   TABELA DE REVISÕES
═══════════════════════════════════════════════════ */
.tabela-revisoes-wrapper { width: 100%; overflow-x: auto; }
.tabela-revisoes {
  width: 100%; min-width: 800px;
  table-layout: fixed; border-collapse: collapse;
}
.col-data       { width: 100px; }
.col-km         { width: 110px; }
.col-flex       { width: 110px; }
.col-responsavel{ width: 160px; }
.col-custo      { width: 120px; }
.col-acoes-rev  { width: 280px; }

.tabela-revisoes tbody tr td {
  vertical-align: middle; overflow: hidden;
  text-overflow: ellipsis; white-space: nowrap;
  padding: 8px 12px;
}
.td-descricao { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.td-km, .td-custo { text-align: right; }
.acoes-cell { display: flex; align-items: center; justify-content: flex-end; gap: 8px; }

/* ═══════════════════════════════════════════════════
   OFFCANVAS (veículo e revisão — mesmo padrão)
═══════════════════════════════════════════════════ */
.offcanvas-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.45);
  z-index: 200; opacity: 0; pointer-events: none; transition: opacity 0.3s ease;
}
.offcanvas-overlay.ativo { opacity: 1; pointer-events: all; }

.offcanvas-panel {
  position: fixed; top: 0; right: 0; bottom: 0;
  width: 100%; max-width: 520px; background: #fff;
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

/* ═══════════════════════════════════════════════════
   INPUTS AUXILIARES
═══════════════════════════════════════════════════ */
.input-disabled {
  background: #f3f4f6; color: #6b7280;
  cursor: not-allowed; opacity: 0.8;
}
.campo-info    { display: block; font-size: 0.72rem; color: #9ca3af; margin-top: 2px; }
.campo-contador{ display: block; text-align: right; font-size: 0.72rem; color: #9ca3af; margin-top: 2px; }

/* ═══════════════════════════════════════════════════
   SELECT DESABILITADO (cascata Marca→Modelo)
═══════════════════════════════════════════════════ */
select:disabled { background: #f3f4f6; color: #9ca3af; cursor: not-allowed; opacity: 0.7; }
.label-hint { font-size: 0.72rem; color: #ef4444; font-weight: 400; margin-left: 4px; }
</style>