<template>
  <div class="pagina">

    <!-- ══════════════════════════════════════════════════════════
         NÍVEL 3 — SUBPAINEL DE REVISÕES
    ══════════════════════════════════════════════════════════ -->
    <transition name="slide-revisoes">
      <div v-if="panelRevisoes" class="revisoes-subpanel">

        <div class="subpanel-header">
          <button class="btn-voltar" @click="fecharRevisoes">← Voltar para Veículos</button>
          <div class="subpanel-titulo">
            <span class="subpanel-badge subpanel-badge--rev">📋</span>
            <h2>
              {{ veiculoRevisoes?.placa }}
              <span class="subpanel-sub">{{ veiculoRevisoes?.marca }} {{ veiculoRevisoes?.modelo }}</span>
            </h2>
          </div>
          <button class="btn btn-sucesso btn-sm" @click="abrirModalCriarRevisao">+ Nova revisão</button>
        </div>

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

        <div class="tabela-revisoes-wrapper" v-if="!carregandoRev">
          <table class="tabela-revisoes">
            <colgroup>
              <col class="rcol-data">
              <col class="rcol-km">
              <col class="rcol-flex">
              <col class="rcol-responsavel">
              <col class="rcol-custo">
              <col class="rcol-acoes">
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
                    <button class="btn btn-info btn-sm"     @click="abrirModalDetalhesRev(r)">🔍</button>
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
                <p class="detalhe-meta-veiculo">{{ formatarData(revisaoDetalhes?.data_revisao) }}</p>
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

        <!-- Offcanvas criar/editar revisão -->
        <div class="offcanvas-overlay" :class="{ ativo: panelRevisaoForm }" @click.self="fecharModalRev">
          <aside class="offcanvas-panel" :class="{ aberto: panelRevisaoForm }">
            <div class="offcanvas-header">
              <h2>{{ modoEdicaoRev ? 'Editar revisão' : 'Nova revisão' }}</h2>
              <button class="offcanvas-fechar" @click="fecharModalRev">✕</button>
            </div>
            <div class="offcanvas-body">
              <form @submit.prevent="salvarRev" novalidate>

                <div class="form-grupo">
                  <label>Veículo</label>
                  <input type="text"
                    :value="`${veiculoRevisoes?.placa} — ${veiculoRevisoes?.marca} ${veiculoRevisoes?.modelo}`"
                    disabled class="input-disabled" />
                </div>
                <div class="form-grupo">
                  <label>Proprietário</label>
                  <input type="text" :value="proprietarioVeiculos?.nome" disabled class="input-disabled" />
                </div>

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

                <div class="form-grupo">
                  <label>Descrição dos serviços *</label>
                  <textarea v-model="formRev.descricao" rows="3"
                    placeholder="Ex: Troca de óleo, filtro de ar..."
                    maxlength="500" required></textarea>
                  <span class="campo-contador">{{ formRev.descricao.length }}/500</span>
                </div>

                <div class="form-row">
                  <div class="form-grupo">
                    <label>Responsável *</label>
                    <input v-model="formRev.responsavel" type="text"
                      placeholder="Nome da oficina ou mecânico"
                      maxlength="100"
                      @keydown="bloquearResponsavelInvalido"
                      required />
                    <span class="campo-contador">{{ formRev.responsavel.length }}/100</span>
                    <span class="campo-info">Apenas letras, espaços e hífens</span>
                  </div>
                  <div class="form-grupo">
                    <label>
                      Custo (R$) *
                      <span class="label-hint">máx. R$&nbsp;12.000,00</span>
                    </label>
                    <input v-model="custoExibicaoRev" type="text"
                      placeholder="R$ 0,00"
                      @input="onInputCustoRev"
                      @keydown="bloquearCustoExcedente"
                      inputmode="numeric"
                      required />
                    <span class="campo-erro" v-if="erroCustoRev">{{ erroCustoRev }}</span>
                    <span class="campo-info" v-else>Valor máximo: R$&nbsp;12.000,00</span>
                  </div>
                </div>

                <p v-if="erroFormRev" class="form-erro">{{ erroFormRev }}</p>

                <div class="offcanvas-footer">
                  <button type="button" class="btn btn-neutro" @click="fecharModalRev">Cancelar</button>
                  <button type="submit" class="btn btn-sucesso"
                    :disabled="salvandoRev || !!erroDataRev || !!erroCustoRev">
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
         NÍVEL 2 — SUBPAINEL DE VEÍCULOS
    ══════════════════════════════════════════════════════════ -->
    <transition name="slide-veiculos">
      <div v-if="panelVeiculos && !panelRevisoes" class="veiculos-subpanel">

        <div class="subpanel-header">
          <button class="btn-voltar" @click="fecharVeiculos">← Voltar para Proprietários</button>
          <div class="subpanel-titulo">
            <span class="subpanel-badge">🚗 Veículos</span>
            <h2>
              {{ proprietarioVeiculos?.nome }}
              <span class="subpanel-sub">{{ proprietarioVeiculos?.cpf }}</span>
            </h2>
          </div>
          <button class="btn btn-sucesso btn-sm" @click="abrirModalCriarVeiculo">+ Novo veículo</button>
        </div>

        <p v-if="mensagemVei" :class="['alerta', mensagemVei.tipo === 'sucesso' ? 'alerta-sucesso' : 'alerta-erro']">
          {{ mensagemVei.texto }}
        </p>

        <div class="filtros">
          <input v-model="filtroTextoVei" class="filtro-input" type="text" placeholder="Buscar por placa, marca ou modelo..." />
          <select v-model="filtroTipoVei" class="filtro-select">
            <option value="">Todos os tipos</option>
            <option value="Carro">Carro</option>
            <option value="Moto">Moto</option>
            <option value="Triciclo">Triciclo</option>
            <option value="Caminhão">Caminhão</option>
          </select>
          <button class="btn btn-neutro" v-if="filtroTextoVei || filtroTipoVei" @click="limparFiltrosVei">
            Limpar filtros
          </button>
        </div>

        <p class="contador-resultados" v-if="!carregandoVei">
          {{ veiculosFiltradosVei.length }} veículo(s) encontrado(s)
        </p>
        <p v-if="carregandoVei" class="estado-loading">Carregando veículos...</p>

        <div class="tabela-veiculos-wrapper" v-if="!carregandoVei">
          <table class="tabela-veiculos">
            <colgroup>
              <col class="col-placa">
              <col class="col-tipo">
              <col class="col-marcamodelo">
              <col class="col-ano">
              <col class="col-acoes-vei">
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
                    <button class="btn btn-info btn-sm"     @click="abrirRevisoes(v)">📋</button>
                    <button class="btn btn-primario btn-sm" @click="abrirModalDetalhesVei(v)">🔍 Detalhes</button>
                    <button class="btn btn-info btn-sm"     @click="abrirModalEditarVeiculo(v)">Editar</button>
                    <button class="btn btn-perigo btn-sm"   @click="confirmarDeletarVei(v)">Excluir</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>

          <div class="paginacao" v-if="totalPaginasVei > 1">
            <button class="btn-paginacao" :disabled="paginaAtualVei === 1" @click="irParaPaginaVei(1)">«</button>
            <button class="btn-paginacao" :disabled="paginaAtualVei === 1" @click="irParaPaginaVei(paginaAtualVei - 1)">← Anterior</button>
            <button v-for="n in paginasVisiveisVei" :key="n"
              class="btn-paginacao" :class="{ 'btn-paginacao-ativo': n === paginaAtualVei }"
              @click="irParaPaginaVei(n)">{{ n }}</button>
            <button class="btn-paginacao" :disabled="paginaAtualVei === totalPaginasVei" @click="irParaPaginaVei(paginaAtualVei + 1)">Próximo →</button>
            <button class="btn-paginacao" :disabled="paginaAtualVei === totalPaginasVei" @click="irParaPaginaVei(totalPaginasVei)">»</button>
            <span class="paginacao-info">Página {{ paginaAtualVei }} de {{ totalPaginasVei }}</span>
          </div>
        </div>

        <!-- Modal detalhes de veículo -->
        <div class="modal-overlay" v-if="modalDetalhesVei" @click.self="modalDetalhesVei = false">
          <div class="modal-card modal-card-lg">
            <div class="modal-header detalhe-header">
              <div>
                <h2 class="detalhe-nome">{{ veiculoDetalhes?.placa }}</h2>
                <p class="detalhe-meta-veiculo">{{ veiculoDetalhes?.marca }} {{ veiculoDetalhes?.modelo }} — {{ veiculoDetalhes?.ano }}</p>
              </div>
              <button class="modal-fechar" @click="modalDetalhesVei = false">✕</button>
            </div>
            <div class="modal-body detalhes-grid" v-if="veiculoDetalhes">
              <div class="detalhe-item">
                <span class="detalhe-label">👤 Proprietário</span>
                <span class="detalhe-valor">{{ proprietarioVeiculos?.nome }}</span>
              </div>
              <div class="detalhe-item">
                <span class="detalhe-label">🏷️ Placa</span>
                <span class="detalhe-valor">{{ veiculoDetalhes.placa }}</span>
              </div>
              <div class="detalhe-item">
                <span class="detalhe-label">🚗 Tipo</span>
                <span class="detalhe-valor">{{ veiculoDetalhes.tipo }}</span>
              </div>
              <div class="detalhe-item">
                <span class="detalhe-label">🏭 Marca</span>
                <span class="detalhe-valor">{{ veiculoDetalhes.marca }}</span>
              </div>
              <div class="detalhe-item">
                <span class="detalhe-label">📋 Modelo</span>
                <span class="detalhe-valor">{{ veiculoDetalhes.modelo }}</span>
              </div>
              <div class="detalhe-item">
                <span class="detalhe-label">📅 Ano</span>
                <span class="detalhe-valor">{{ veiculoDetalhes.ano }}</span>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn btn-neutro" @click="modalDetalhesVei = false">Fechar</button>
              <button class="btn btn-primario" @click="() => { modalDetalhesVei = false; abrirModalEditarVeiculo(veiculoDetalhes) }">
                Editar veículo
              </button>
            </div>
          </div>
        </div>

        <!-- Modal exclusão de veículo -->
        <div class="modal-overlay" v-if="modalDeletarVei" @click.self="modalDeletarVei = false">
          <div class="modal-card modal-card-sm">
            <div class="modal-header">
              <h2>Confirmar exclusão</h2>
              <button class="modal-fechar" @click="modalDeletarVei = false">✕</button>
            </div>
            <p style="margin: 16px 0;">
              Deseja excluir o veículo <strong>{{ veiculoSelecionadoVei?.marca }} {{ veiculoSelecionadoVei?.modelo }}</strong>
              ({{ veiculoSelecionadoVei?.placa }})? Todas as revisões vinculadas serão removidas.
            </p>
            <div class="modal-footer">
              <button class="btn btn-neutro" @click="modalDeletarVei = false">Cancelar</button>
              <button class="btn btn-perigo" @click="deletarVei" :disabled="salvandoVei">
                {{ salvandoVei ? 'Excluindo...' : 'Confirmar exclusão' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Offcanvas criar/editar veículo -->
        <div class="offcanvas-overlay" :class="{ ativo: panelVeiculoForm }" @click.self="fecharModalVeiculo">
          <aside class="offcanvas-panel" :class="{ aberto: panelVeiculoForm }">
            <div class="offcanvas-header">
              <h2>{{ modoEdicaoVei ? 'Editar veículo' : 'Novo veículo' }}</h2>
              <button class="offcanvas-fechar" @click="fecharModalVeiculo">✕</button>
            </div>
            <div class="offcanvas-body">
              <form @submit.prevent="salvarVeiculo" novalidate>

                <div class="form-grupo">
                  <label>Proprietário</label>
                  <input type="text"
                    :value="`${proprietarioVeiculos?.nome} — ${proprietarioVeiculos?.cpf}`"
                    disabled class="input-disabled" />
                </div>

                <div class="form-grupo">
                  <label>Placa *</label>
                  <input v-model="formVei.placa" type="text"
                    placeholder="ABC-1234 ou ABC1D23" maxlength="8"
                    @keydown="bloquearPlacaInvalida"
                    @input="aplicarMascaraPlaca"
                    @blur="validarPlaca" required />
                  <span class="campo-info">Formato: ABC-1234 (antiga) ou ABC-1D23 (Mercosul) · máx. 8 chars</span>
                  <span class="campo-erro" v-if="erroPlacaVei">{{ erroPlacaVei }}</span>
                </div>

                <div class="form-grupo">
                  <label>Ano *</label>
                  <input v-model="formVei.ano" type="number" placeholder="2020" min="1900" :max="anoAtual" required />
                </div>

                <div class="form-row">
                  <div class="form-grupo">
                    <label>Marca *</label>
                    <select v-model="formVei.marca" required>
                      <option value="">Selecione a marca</option>
                      <option v-for="m in Object.keys(MARCA_MODELOS)" :key="m" :value="m">{{ m }}</option>
                    </select>
                  </div>
                  <div class="form-grupo">
                    <label>
                      Modelo *
                      <span class="label-hint" v-if="!formVei.marca">— selecione a marca primeiro</span>
                    </label>
                    <select v-model="formVei.modelo" :disabled="!formVei.marca" required>
                      <option value="">{{ formVei.marca ? 'Selecione o modelo' : 'Selecione a marca primeiro' }}</option>
                      <option v-for="m in modelosDisponiveisVei" :key="m" :value="m">{{ m }}</option>
                    </select>
                  </div>
                </div>

                <div class="form-grupo" v-if="!modoEdicaoVei">
                  <label>Tipo de veículo *</label>
                  <select v-model="formVei.tipo" required>
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
                      <input v-model="formVei.numero_portas" type="number" placeholder="4" min="2" max="6" required />
                    </div>
                    <div class="form-grupo">
                      <label>Combustível *</label>
                      <select v-model="formVei.tipo_combustivel" required>
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
                    <select v-model="formVei.ar_condicionado">
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
                      <input v-model="formVei.cilindradas" type="number" placeholder="150" min="50" required />
                    </div>
                    <div class="form-grupo">
                      <label>Tipo de partida *</label>
                      <select v-model="formVei.tipo_partida" required>
                        <option value="">Selecione</option>
                        <option value="Elétrica">Elétrica</option>
                        <option value="Pedal">Pedal</option>
                        <option value="Ambos">Ambos</option>
                      </select>
                    </div>
                  </div>
                  <div class="form-grupo">
                    <label>Refrigeração *</label>
                    <select v-model="formVei.refrigeracao" required>
                      <option value="">Selecione</option>
                      <option value="Ar">Ar</option>
                      <option value="Água">Água</option>
                      <option value="Óleo">Óleo</option>
                    </select>
                  </div>
                </template>

                <template v-if="formVei.tipo === 'triciclo'">
                  <div class="form-separador">Dados do triciclo</div>
                  <div class="form-row">
                    <div class="form-grupo">
                      <label>Tipo de tração *</label>
                      <input v-model="formVei.tipo_tracao" type="text" placeholder="Dianteira" required />
                    </div>
                    <div class="form-grupo">
                      <label>Capacidade de carga (kg) *</label>
                      <input v-model="formVei.capacidade_carga" type="number" placeholder="300" min="0" required />
                    </div>
                  </div>
                </template>

                <template v-if="formVei.tipo === 'caminhao'">
                  <div class="form-separador">Dados do caminhão</div>
                  <div class="form-row">
                    <div class="form-grupo">
                      <label>Qtd. de eixos *</label>
                      <input v-model="formVei.quantidade_eixos" type="number" placeholder="2" min="2" required />
                    </div>
                    <div class="form-grupo">
                      <label>Capacidade (ton) *</label>
                      <input v-model="formVei.capacidade_toneladas" type="number" placeholder="5" min="0" required />
                    </div>
                  </div>
                  <div class="form-grupo">
                    <label>Tipo de carroceria *</label>
                    <input v-model="formVei.tipo_carroceria" type="text" placeholder="Baú, Graneleiro..." required />
                  </div>
                </template>

                <p v-if="erroFormVei" class="form-erro">{{ erroFormVei }}</p>

                <div class="offcanvas-footer">
                  <button type="button" class="btn btn-neutro" @click="fecharModalVeiculo">Cancelar</button>
                  <button type="submit" class="btn btn-sucesso" :disabled="salvandoVei || !!erroPlacaVei">
                    {{ salvandoVei ? 'Salvando...' : modoEdicaoVei ? 'Salvar alterações' : 'Criar veículo' }}
                  </button>
                </div>

              </form>
            </div>
          </aside>
        </div>

      </div>
    </transition>

    <!-- ══════════════════════════════════════════════════════════
         NÍVEL 1 — TELA PRINCIPAL: Lista de Proprietários
    ══════════════════════════════════════════════════════════ -->
    <div v-show="!panelVeiculos && !panelRevisoes">

      <div class="pagina-header">
        <h1>Proprietários</h1>
        <button class="btn btn-sucesso" @click="abrirModalCriar">+ Novo proprietário</button>
      </div>

      <p v-if="mensagem" :class="['alerta', mensagem.tipo === 'sucesso' ? 'alerta-sucesso' : 'alerta-erro']">
        {{ mensagem.texto }}
      </p>

      <div class="barra-busca" v-if="!carregando">
        <input v-model="termoBusca" type="text" placeholder="Buscar por nome ou CPF..." class="input-busca" />
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
                <input v-model="form.nome" type="text" placeholder="Ex: João da Silva" maxlength="100" required />
                <span class="campo-contador">{{ form.nome.length }}/100</span>
              </div>
              <div class="form-grupo">
                <label>CPF *</label>
                <input v-model="form.cpf" type="text" placeholder="000.000.000-00" maxlength="14"
                  @keydown="bloquearCpfInvalido" @input="aplicarMascaraCpf" @blur="validarCpf" required />
                <span class="campo-erro" v-if="erroCpf">{{ erroCpf }}</span>
              </div>
              <div class="form-row">
                <div class="form-grupo">
                  <label>Gênero *</label>
                  <select v-model="form.genero" required>
                    <option value="">Selecione</option>
                    <option value="M">Masculino</option>
                    <option value="F">Feminino</option>
                  </select>
                </div>
                <div class="form-grupo">
                  <label>Data de nascimento *</label>
                  <input v-model="form.data_nascimento" type="date" :max="dataMaxima" @change="validarIdade" required />
                  <span class="campo-erro" v-if="erroData">{{ erroData }}</span>
                </div>
              </div>
              <div class="form-grupo">
                <label>Endereço</label>
                <input v-model="form.endereco" type="text" placeholder="Rua, número, cidade" maxlength="200" />
                <span class="campo-contador">{{ form.endereco.length }}/200</span>
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
          <p style="margin: 16px 0;">
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

    </div><!-- fim v-show proprietários -->
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import api from '@/services/api'

// ══════════════════════════════════════════════════════════════
// UTILITÁRIO GENÉRICO DE ORDENAÇÃO
//
// IMPORTANTE — como funciona o unwrap do Vue no template:
//   Quando um `ref` é passado como argumento de função no template,
//   o Vue faz o unwrap automático e entrega o valor bruto ({ coluna, direcao }).
//   Por isso as funções abaixo recebem o objeto reativo diretamente,
//   sem precisar acessar `.value`.
//   Já dentro dos `computed` (código JS puro), usamos `estado.value`
//   para acessar o conteúdo do ref normalmente.
// ══════════════════════════════════════════════════════════════

/**
 * Cria o estado de ordenação como um ref reativo.
 * Uso interno (JS): `estado.value.coluna`
 * Uso no template (passado p/ funções): Vue faz unwrap → objeto bruto
 */
const criarOrdenacao = (colunaInicial = '', direcaoInicial = 'asc') =>
  ref({ coluna: colunaInicial, direcao: direcaoInicial })

/**
 * Chamada pelo template via @click.
 * Recebe o objeto bruto { coluna, direcao } (Vue já fez o unwrap do ref).
 */
const alternarOrdenacao = (estado, col) => {
  if (estado.coluna === col) {
    estado.direcao = estado.direcao === 'asc' ? 'desc' : 'asc'
  } else {
    estado.coluna  = col
    estado.direcao = 'asc'
  }
}

/**
 * Chamada pelo template via {{ }}.
 * Recebe o objeto bruto { coluna, direcao } (Vue já fez o unwrap do ref).
 * Retorna: ↕ (inativo) | ↑ (asc) | ↓ (desc)
 */
const iconeOrdenacao = (estado, col) => {
  if (!estado || estado.coluna !== col) return '↕'
  return estado.direcao === 'asc' ? '↑' : '↓'
}

/**
 * Chamada dentro de computed (código JS puro).
 * Recebe o ref e acessa `.value` explicitamente.
 * Suporta strings (localeCompare pt-BR), números e datas ISO.
 * @param {Array}  lista      — array de objetos já filtrado
 * @param {Ref}    estadoRef  — ref({ coluna, direcao })
 * @param {Array}  numericos  — nomes de colunas numéricas
 */
const aplicarOrdenacao = (lista, estadoRef, numericos = []) => {
  const { coluna, direcao } = estadoRef.value
  if (!coluna) return lista

  return [...lista].sort((a, b) => {
    let valA = a[coluna]
    let valB = b[coluna]

    if (numericos.includes(coluna)) {
      valA = parseFloat(valA) || 0
      valB = parseFloat(valB) || 0
      return direcao === 'asc' ? valA - valB : valB - valA
    }

    // Strings e datas ISO yyyy-mm-dd (ordena lexicograficamente — funciona direto)
    valA = valA == null ? '' : String(valA)
    valB = valB == null ? '' : String(valB)
    const cmp = valA.localeCompare(valB, 'pt-BR', { sensitivity: 'base' })
    return direcao === 'asc' ? cmp : -cmp
  })
}

// ══════════════════════════════════════════════════════════════
// ESTADO — Proprietários (Nível 1)
// ══════════════════════════════════════════════════════════════
const usuarios           = ref([])
const carregando         = ref(true)
const salvando           = ref(false)
const mensagem           = ref(null)
const erroForm           = ref(null)
const erroCpf            = ref(null)
const erroData           = ref(null)
const panelAberto        = ref(false)
const modalDeletar       = ref(false)
const modoEdicao         = ref(false)
const usuarioSelecionado = ref(null)
const termoBusca         = ref('')
const paginaAtual        = ref(1)
// Metadados de paginação vindos do servidor
const totalRegistros     = ref(0)
const totalPaginasServidor = ref(1)
const formVazio = { nome: '', cpf: '', genero: '', data_nascimento: '', endereco: '' }
const form      = ref({ ...formVazio })

// Ordenação — Proprietários (padrão: nome asc)
const ordenacaoProp = criarOrdenacao('nome', 'asc')

// ══════════════════════════════════════════════════════════════
// ESTADO — Subpainel Veículos (Nível 2)
// ══════════════════════════════════════════════════════════════
const panelVeiculos          = ref(false)
const proprietarioVeiculos   = ref(null)
const veiculosDoProprietario = ref([])
const carregandoVei          = ref(false)
const salvandoVei            = ref(false)
const mensagemVei            = ref(null)
const erroFormVei            = ref(null)
const erroPlacaVei           = ref(null)
const panelVeiculoForm       = ref(false)
const modalDetalhesVei       = ref(false)
const modalDeletarVei        = ref(false)
const modoEdicaoVei          = ref(false)
const veiculoSelecionadoVei  = ref(null)
const veiculoDetalhes        = ref(null)
const filtroTextoVei         = ref('')
const filtroTipoVei          = ref('')
const paginaAtualVei         = ref(1)
const ITENS_VEI              = 10
const anoAtual               = new Date().getFullYear()

// Ordenação — Veículos (padrão: placa asc)
const ordenacaoVei = criarOrdenacao('placa', 'asc')

// ══════════════════════════════════════════════════════════════
// ESTADO — Subpainel Revisões (Nível 3)
// ══════════════════════════════════════════════════════════════
const panelRevisoes      = ref(false)
const veiculoRevisoes    = ref(null)
const revisoes           = ref([])
const carregandoRev      = ref(false)
const salvandoRev        = ref(false)
const mensagemRev        = ref(null)
const erroFormRev        = ref(null)
const erroDataRev        = ref(null)
const erroCustoRev       = ref(null)
const panelRevisaoForm   = ref(false)
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
const CUSTO_MAXIMO       = 12000.00

const formRevVazio = { veiculo: '', data_revisao: '', quilometragem: '', descricao: '', responsavel: '', custo: '' }
const formRev = ref({ ...formRevVazio })

// Ordenação — Revisões (padrão: data_revisao desc)
const ordenacaoRev = criarOrdenacao('data_revisao', 'desc')

// ══════════════════════════════════════════════════════════════
// MARCA → MODELO
// ══════════════════════════════════════════════════════════════
const MARCA_MODELOS = {
  'Toyota':        ['Corolla', 'Hilux', 'Yaris', 'RAV4', 'Camry'],
  'Volkswagen':    ['Fusca', 'Golf', 'Polo', 'Gol', 'Tiguan'],
  'Ford':          ['Mustang', 'Ka', 'EcoSport', 'Ranger', 'Bronco'],
  'Ferrari':       ['F40', 'F50', '488 GTB', 'Roma', 'SF90'],
  'BMW':           ['Série 3', 'Série 5', 'X1', 'X5', 'M3'],
  'Mercedes-Benz': ['Classe A', 'Classe C', 'GLA', 'GLE', 'AMG GT'],
  'Honda':         ['Civic', 'HR-V', 'Fit', 'CR-V', 'City'],
  'Chevrolet':     ['Camaro', 'Onix', 'Tracker', 'S10', 'Equinox'],
  'Tesla':         ['Model 3', 'Model S', 'Model X', 'Model Y', 'Cybertruck'],
  'Porsche':       ['911', 'Cayenne', 'Macan', 'Panamera', 'Taycan'],
  'Hyundai':       ['HB20', 'Creta', 'Tucson', 'i30', 'Azera'],
  'Audi':          ['A3', 'A4', 'Q3', 'Q5', 'TT'],
  'Lamborghini':   ['Huracán', 'Urus', 'Aventador', 'Revuelto', 'Sterrato'],
  'Nissan':        ['Skyline GT-R', 'Frontier', 'Kicks', 'Versa', 'Sentra'],
  'Fiat':          ['Fiat 500', 'Strada', 'Argo', 'Pulse', 'Toro'],
}

const formVeiVazio = {
  proprietario: '', placa: '', marca: '', modelo: '', ano: '', tipo: '',
  numero_portas: '', tipo_combustivel: '', ar_condicionado: true,
  cilindradas: '', tipo_partida: '', refrigeracao: '',
  tipo_tracao: '', capacidade_carga: '',
  quantidade_eixos: '', capacidade_toneladas: '', tipo_carroceria: '',
}
const formVei = ref({ ...formVeiVazio })

const modelosDisponiveisVei = computed(() =>
  formVei.value.marca ? (MARCA_MODELOS[formVei.value.marca] ?? []) : []
)
watch(() => formVei.value.marca, () => { formVei.value.modelo = '' })

// ══════════════════════════════════════════════════════════════
// COMPUTEDS — Proprietários
//
// Modelo de ordenação LOCAL:
//   - A busca (termoBusca) e a troca de página fazem request ao servidor.
//   - A ordenação por coluna é aplicada APENAS sobre os registros já
//     carregados na página atual, sem nenhum request extra.
//   - Trocar de página mantém a ordenação ativa (o computed re-aplica).
// ══════════════════════════════════════════════════════════════
const dataMaxima = computed(() => {
  const d = new Date(); d.setFullYear(d.getFullYear() - 18)
  return d.toISOString().split('T')[0]
})

// Ordena localmente os registros já carregados, preservando a seleção
// de página. Colunas numéricas são comparadas como número; demais como
// string pt-BR para respeitar acentos (ç, ã, é…).
const COLUNAS_NUMERICAS_PROP = new Set(['idade', 'total_veiculos'])

const usuariosPaginados = computed(() => {
  const { coluna, direcao } = ordenacaoProp.value
  if (!coluna) return usuarios.value

  return [...usuarios.value].sort((a, b) => {
    let vA = a[coluna], vB = b[coluna]

    if (COLUNAS_NUMERICAS_PROP.has(coluna)) {
      vA = parseFloat(vA) || 0
      vB = parseFloat(vB) || 0
      return direcao === 'asc' ? vA - vB : vB - vA
    }

    vA = vA == null ? '' : String(vA)
    vB = vB == null ? '' : String(vB)
    const cmp = vA.localeCompare(vB, 'pt-BR', { sensitivity: 'base' })
    return direcao === 'asc' ? cmp : -cmp
  })
})

// Mantido para compatibilidade com o contador de registros no template
const usuariosFiltrados = computed(() => usuarios.value)
const totalPaginas      = computed(() => totalPaginasServidor.value)

const paginasVisiveis = computed(() => {
  const total = totalPaginas.value, atual = paginaAtual.value
  let inicio = Math.max(1, atual - 2), fim = Math.min(total, inicio + 4)
  if (fim - inicio < 4) inicio = Math.max(1, fim - 4)
  const p = []; for (let i = inicio; i <= fim; i++) p.push(i); return p
})

// Somente termoBusca dispara request (reseta para pág. 1 para refletir filtro).
// Mudança de ordenação NÃO dispara request — só reordena localmente via computed.
watch(termoBusca, () => { paginaAtual.value = 1; buscar() })

// Trocar de página: mantém ordenação, apenas busca a fatia correta no servidor.
const irParaPagina = (n) => {
  if (n >= 1 && n <= totalPaginas.value && n !== paginaAtual.value) {
    paginaAtual.value = n
    buscar()
  }
}

// ══════════════════════════════════════════════════════════════
// COMPUTEDS — Veículos
// ══════════════════════════════════════════════════════════════
const veiculosFiltradosVei = computed(() => {
  const lista = veiculosDoProprietario.value.filter(v => {
    const texto = filtroTextoVei.value.toLowerCase()
    const bateTexto = !texto ||
      v.placa.toLowerCase().includes(texto) ||
      v.marca.toLowerCase().includes(texto) ||
      v.modelo.toLowerCase().includes(texto)
    return bateTexto && (!filtroTipoVei.value || v.tipo === filtroTipoVei.value)
  })
  // Colunas numéricas de veículos
  return aplicarOrdenacao(lista, ordenacaoVei, ['ano'])
})

const totalPaginasVei = computed(() => Math.ceil(veiculosFiltradosVei.value.length / ITENS_VEI))
const veiculosPaginadosVei = computed(() => {
  const i = (paginaAtualVei.value - 1) * ITENS_VEI
  return veiculosFiltradosVei.value.slice(i, i + ITENS_VEI)
})
const paginasVisiveisVei = computed(() => {
  const total = totalPaginasVei.value, atual = paginaAtualVei.value
  let ini = Math.max(1, atual - 2), fim = Math.min(total, ini + 4)
  if (fim - ini < 4) ini = Math.max(1, fim - 4)
  const p = []; for (let i = ini; i <= fim; i++) p.push(i); return p
})

watch([filtroTextoVei, filtroTipoVei], () => { paginaAtualVei.value = 1 })
watch(ordenacaoVei, () => { paginaAtualVei.value = 1 }, { deep: true })

const irParaPaginaVei = (n) => { if (n >= 1 && n <= totalPaginasVei.value) paginaAtualVei.value = n }

// ══════════════════════════════════════════════════════════════
// COMPUTEDS — Revisões
// ══════════════════════════════════════════════════════════════
const revisoesFiltradas = computed(() => {
  const lista = revisoes.value.filter(r => {
    const txt = filtroTextoRev.value.toLowerCase()
    const bateTexto = !txt ||
      r.responsavel?.toLowerCase().includes(txt) ||
      r.descricao?.toLowerCase().includes(txt)
    return bateTexto &&
      (!filtroInicioRev.value || r.data_revisao >= filtroInicioRev.value) &&
      (!filtroFimRev.value    || r.data_revisao <= filtroFimRev.value)
  })
  // Colunas numéricas de revisões
  return aplicarOrdenacao(lista, ordenacaoRev, ['quilometragem', 'custo'])
})

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
watch(ordenacaoRev, () => { paginaAtualRev.value = 1 }, { deep: true })

const irParaPaginaRev = (n) => { if (n >= 1 && n <= totalPaginasRev.value) paginaAtualRev.value = n }

// ══════════════════════════════════════════════════════════════
// MOUNTED
// ══════════════════════════════════════════════════════════════
onMounted(async () => { await buscar() })

// ══════════════════════════════════════════════════════════════
// AÇÕES — Proprietários
// ══════════════════════════════════════════════════════════════
const buscar = async () => {
  carregando.value = true
  try {
    // Monta o ordering para o backend: ex. "nome", "-idade", "total_veiculos"
    const { coluna, direcao } = ordenacaoProp.value
    const ordering = coluna ? (direcao === 'desc' ? `-${coluna}` : coluna) : 'nome'

    const { data } = await api.get('users/', {
      params: {
        page:     paginaAtual.value,
        search:   termoBusca.value.trim() || undefined,
        ordering,
      }
    })

    // Suporta duas formas de resposta do backend:
    //   1. Envelope paginado: { count, total_pages, page, results: [...] }
    //   2. Array legado:      [ ...usuários... ]  (backend ainda não atualizado)
    if (Array.isArray(data)) {
      // Resposta legada — faz paginação no cliente como fallback
      const ITENS = 10
      const inicio = (paginaAtual.value - 1) * ITENS
      const termo  = termoBusca.value.toLowerCase().trim()
      const filtrado = termo
        ? data.filter(u => u.nome.toLowerCase().includes(termo) || u.cpf.includes(termo))
        : data
      totalRegistros.value       = filtrado.length
      totalPaginasServidor.value = Math.max(1, Math.ceil(filtrado.length / ITENS))
      usuarios.value             = filtrado.slice(inicio, inicio + ITENS)
    } else {
      // Envelope paginado — usa diretamente os dados do servidor
      usuarios.value             = Array.isArray(data?.results) ? data.results : []
      totalRegistros.value       = data?.count       ?? 0
      totalPaginasServidor.value = data?.total_pages ?? 1
    }
  } catch {
    exibirMensagem('Erro ao carregar proprietários.', 'erro')
    usuarios.value             = []
    totalRegistros.value       = 0
    totalPaginasServidor.value = 1
  } finally {
    carregando.value = false
  }
}
const abrirModalCriar = () => {
  modoEdicao.value = false; form.value = { ...formVazio }
  erroForm.value = erroCpf.value = erroData.value = null
  panelAberto.value = true
}
const abrirModalEditar = (u) => {
  modoEdicao.value = true; usuarioSelecionado.value = u
  form.value = { nome: u.nome, cpf: u.cpf, genero: u.genero, data_nascimento: u.data_nascimento, endereco: u.endereco || '' }
  erroForm.value = erroCpf.value = erroData.value = null
  panelAberto.value = true
}
const fecharModal = () => { panelAberto.value = false; erroForm.value = erroCpf.value = erroData.value = null }
const salvar = async () => {
  if (!validarCpf() || !validarIdade()) return
  salvando.value = true; erroForm.value = null
  try {
    if (modoEdicao.value) {
      const { data } = await api.put(`users/${usuarioSelecionado.value.id}/update/`, form.value)
      exibirMensagem(`Proprietário ${data.nome} atualizado.`, 'sucesso')
    } else {
      const { data } = await api.post('users/creat/', form.value)
      exibirMensagem(`Proprietário ${data.nome} criado.`, 'sucesso')
    }
    fecharModal()
    await buscar()   // recarrega a página atual do servidor
  } catch (e) {
    const erros = e.response?.data
    erroForm.value = erros ? Object.values(erros).flat().join(' ') : 'Erro ao salvar.'
  } finally { salvando.value = false }
}
const confirmarDeletar = (u) => { usuarioSelecionado.value = u; modalDeletar.value = true }
const deletar = async () => {
  salvando.value = true
  try {
    const nome = usuarioSelecionado.value.nome
    await api.delete(`users/${usuarioSelecionado.value.id}/delete/`)
    modalDeletar.value = false
    exibirMensagem(`Proprietário ${nome} excluído.`, 'sucesso')
    // Se era o último da página e não é a primeira, volta uma página
    if (usuarios.value.length === 1 && paginaAtual.value > 1) paginaAtual.value -= 1
    await buscar()
  } catch { exibirMensagem('Erro ao excluir.', 'erro') }
  finally { salvando.value = false }
}

// ══════════════════════════════════════════════════════════════
// AÇÕES — Veículos
// ══════════════════════════════════════════════════════════════
const abrirVeiculos = async (usuario) => {
  proprietarioVeiculos.value  = usuario
  panelVeiculos.value         = true
  filtroTextoVei.value        = ''
  filtroTipoVei.value         = ''
  paginaAtualVei.value        = 1
  carregandoVei.value         = true
  try {
    const { data } = await api.get(`veiculos/proprietario/${usuario.id}/`)
    veiculosDoProprietario.value = data
  } catch { exibirMensagemVei('Erro ao carregar veículos.', 'erro') }
  finally { carregandoVei.value = false }
}
const fecharVeiculos = () => {
  panelVeiculos.value = false; proprietarioVeiculos.value = null
  veiculosDoProprietario.value = []; panelVeiculoForm.value = false
  modalDetalhesVei.value = false; modalDeletarVei.value = false
}
const limparFiltrosVei = () => { filtroTextoVei.value = ''; filtroTipoVei.value = '' }
const abrirModalDetalhesVei = (v) => { veiculoDetalhes.value = v; modalDetalhesVei.value = true }
const abrirModalCriarVeiculo = () => {
  modoEdicaoVei.value = false
  formVei.value = { ...formVeiVazio, proprietario: proprietarioVeiculos.value.id }
  erroFormVei.value = erroPlacaVei.value = null; panelVeiculoForm.value = true
}
const abrirModalEditarVeiculo = (v) => {
  modoEdicaoVei.value = true; veiculoSelecionadoVei.value = v
  formVei.value = { ...formVeiVazio, proprietario: v.proprietario, placa: v.placa,
    marca: v.marca, modelo: v.modelo, ano: v.ano, tipo: v.tipo?.toLowerCase().replace('ã','a') || '' }
  erroFormVei.value = erroPlacaVei.value = null; panelVeiculoForm.value = true
}
const fecharModalVeiculo = () => { panelVeiculoForm.value = false; erroFormVei.value = erroPlacaVei.value = null }
const confirmarDeletarVei = (v) => { veiculoSelecionadoVei.value = v; modalDeletarVei.value = true }
const salvarVeiculo = async () => {
  if (!validarPlaca()) return
  salvandoVei.value = true; erroFormVei.value = null
  try {
    if (modoEdicaoVei.value) {
      const { data } = await api.put(`veiculos/${veiculoSelecionadoVei.value.id}/update/`, {
        proprietario: formVei.value.proprietario, placa: formVei.value.placa,
        marca: formVei.value.marca, modelo: formVei.value.modelo, ano: formVei.value.ano,
      })
      const idx = veiculosDoProprietario.value.findIndex(v => v.id === veiculoSelecionadoVei.value.id)
      if (idx !== -1) veiculosDoProprietario.value[idx] = { ...veiculosDoProprietario.value[idx], ...data }
      exibirMensagemVei(`Veículo ${data.placa} atualizado.`, 'sucesso')
    } else {
      const { data } = await api.post('veiculos/creat/', montarPayloadVeiculo())
      veiculosDoProprietario.value.push(data)
      const prop = usuarios.value.find(u => u.id === proprietarioVeiculos.value.id)
      if (prop) prop.total_veiculos = (prop.total_veiculos || 0) + 1
      exibirMensagemVei(`Veículo ${data.placa} criado.`, 'sucesso')
    }
    fecharModalVeiculo()
  } catch (e) {
    const erros = e.response?.data
    erroFormVei.value = erros ? Object.values(erros).flat().join(' ') : 'Erro ao salvar.'
  } finally { salvandoVei.value = false }
}
const montarPayloadVeiculo = () => {
  const base = { proprietario: formVei.value.proprietario, placa: formVei.value.placa,
    marca: formVei.value.marca, modelo: formVei.value.modelo, ano: formVei.value.ano, tipo: formVei.value.tipo }
  const extras = {
    carro:    { numero_portas: formVei.value.numero_portas, tipo_combustivel: formVei.value.tipo_combustivel, ar_condicionado: formVei.value.ar_condicionado },
    moto:     { cilindradas: formVei.value.cilindradas, tipo_partida: formVei.value.tipo_partida, refrigeracao: formVei.value.refrigeracao },
    triciclo: { tipo_tracao: formVei.value.tipo_tracao, capacidade_carga: formVei.value.capacidade_carga },
    caminhao: { quantidade_eixos: formVei.value.quantidade_eixos, capacidade_toneladas: formVei.value.capacidade_toneladas, tipo_carroceria: formVei.value.tipo_carroceria },
  }
  return { ...base, ...(extras[formVei.value.tipo] || {}) }
}
const deletarVei = async () => {
  salvandoVei.value = true
  try {
    await api.delete(`veiculos/${veiculoSelecionadoVei.value.id}/delete/`)
    veiculosDoProprietario.value = veiculosDoProprietario.value.filter(v => v.id !== veiculoSelecionadoVei.value.id)
    const prop = usuarios.value.find(u => u.id === proprietarioVeiculos.value.id)
    if (prop && prop.total_veiculos > 0) prop.total_veiculos -= 1
    modalDeletarVei.value = false
    exibirMensagemVei(`Veículo ${veiculoSelecionadoVei.value.placa} excluído.`, 'sucesso')
  } catch { exibirMensagemVei('Erro ao excluir veículo.', 'erro') }
  finally { salvandoVei.value = false }
}

// ══════════════════════════════════════════════════════════════
// AÇÕES — Revisões
// ══════════════════════════════════════════════════════════════
const abrirRevisoes = async (veiculo) => {
  veiculoRevisoes.value = veiculo
  panelRevisoes.value   = true
  filtroTextoRev.value  = ''; filtroInicioRev.value = ''; filtroFimRev.value = ''
  paginaAtualRev.value  = 1
  carregandoRev.value   = true
  try {
    const { data } = await api.get(`revisoes/veiculo/${veiculo.id}/`)
    revisoes.value = data
  } catch { exibirMensagemRev('Erro ao carregar revisões.', 'erro') }
  finally { carregandoRev.value = false }
}
const fecharRevisoes = () => {
  panelRevisoes.value = false; veiculoRevisoes.value = null; revisoes.value = []
  panelRevisaoForm.value = false; modalDetalhesRev.value = false; modalDeletarRev.value = false
}
const limparFiltrosRev = () => { filtroTextoRev.value = ''; filtroInicioRev.value = ''; filtroFimRev.value = '' }
const abrirModalDetalhesRev = (r) => { revisaoDetalhes.value = r; modalDetalhesRev.value = true }
const abrirModalCriarRevisao = () => {
  modoEdicaoRev.value = false
  formRev.value = { ...formRevVazio, veiculo: veiculoRevisoes.value.id }
  erroFormRev.value = erroDataRev.value = erroCustoRev.value = null
  custoExibicaoRev.value = ''; panelRevisaoForm.value = true
}
const abrirModalEditarRev = (r) => {
  modoEdicaoRev.value = true; revisaoSelecionada.value = r
  formRev.value = { veiculo: r.veiculo, data_revisao: r.data_revisao,
    quilometragem: r.quilometragem, descricao: r.descricao, responsavel: r.responsavel, custo: r.custo }
  custoExibicaoRev.value = parseFloat(r.custo || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
  erroFormRev.value = erroDataRev.value = erroCustoRev.value = null
  panelRevisaoForm.value = true
}
const fecharModalRev = () => {
  panelRevisaoForm.value = false; erroFormRev.value = erroDataRev.value = erroCustoRev.value = null
}
const confirmarDeletarRev = (r) => { revisaoSelecionada.value = r; modalDeletarRev.value = true }
const salvarRev = async () => {
  if (!validarDataRev()) return
  const custoNum = parseFloat(formRev.value.custo)
  if (!formRev.value.custo || isNaN(custoNum) || custoNum <= 0) {
    erroCustoRev.value = 'Informe um custo válido maior que R$ 0,00.'; return
  }
  if (custoNum > CUSTO_MAXIMO) {
    erroCustoRev.value = 'O valor não pode ultrapassar R$ 12.000,00.'; return
  }
  salvandoRev.value = true; erroFormRev.value = null
  try {
    if (modoEdicaoRev.value) {
      const { data } = await api.put(`revisoes/${revisaoSelecionada.value.id}/update/`, formRev.value)
      const idx = revisoes.value.findIndex(r => r.id === revisaoSelecionada.value.id)
      if (idx !== -1) revisoes.value[idx] = { ...revisoes.value[idx], ...data }
      exibirMensagemRev('Revisão atualizada com sucesso.', 'sucesso')
    } else {
      const { data } = await api.post('revisoes/creat/', formRev.value)
      revisoes.value.unshift({ ...data,
        veiculo_placa: veiculoRevisoes.value.placa, veiculo_marca: veiculoRevisoes.value.marca,
        veiculo_modelo: veiculoRevisoes.value.modelo, proprietario_nome: proprietarioVeiculos.value?.nome })
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
    modalDeletarRev.value = false; exibirMensagemRev('Revisão excluída com sucesso.', 'sucesso')
  } catch { exibirMensagemRev('Erro ao excluir revisão.', 'erro') }
  finally { salvandoRev.value = false }
}

// ══════════════════════════════════════════════════════════════
// VALIDAÇÕES — Proprietário
// ══════════════════════════════════════════════════════════════
const bloquearCpfInvalido = (e) => {
  const permitidas = ['Backspace','Delete','Tab','ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Home','End']
  if (e.ctrlKey || e.metaKey) return
  if (permitidas.includes(e.key)) return
  if (!/^\d$/.test(e.key)) e.preventDefault()
}
const aplicarMascaraCpf = () => {
  let v = form.value.cpf.replace(/\D/g, '').slice(0, 11)
  if (v.length > 9)      v = v.replace(/(\d{3})(\d{3})(\d{3})(\d{0,2})/, '$1.$2.$3-$4')
  else if (v.length > 6) v = v.replace(/(\d{3})(\d{3})(\d{0,3})/, '$1.$2.$3')
  else if (v.length > 3) v = v.replace(/(\d{3})(\d{0,3})/, '$1.$2')
  form.value.cpf = v; erroCpf.value = null
}
const validarCpf = () => {
  const cpf = form.value.cpf.replace(/\D/g, '')
  if (cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) { erroCpf.value = 'CPF inválido.'; return false }
  const calc  = (f) => cpf.slice(0, f - 1).split('').reduce((a, d, i) => a + Number(d) * (f - i), 0)
  const resto = (s) => { const r = (s * 10) % 11; return r >= 10 ? 0 : r }
  if (resto(calc(10)) !== Number(cpf[9]) || resto(calc(11)) !== Number(cpf[10])) { erroCpf.value = 'CPF inválido.'; return false }
  erroCpf.value = null; return true
}
const validarIdade = () => {
  const nasc = new Date(form.value.data_nascimento), hoje = new Date()
  let idade = hoje.getFullYear() - nasc.getFullYear()
  const m = hoje.getMonth() - nasc.getMonth()
  if (m < 0 || (m === 0 && hoje.getDate() < nasc.getDate())) idade--
  if (nasc > hoje) { erroData.value = 'Data não pode ser futura.'; return false }
  if (idade < 18)  { erroData.value = 'Mínimo 18 anos.'; return false }
  erroData.value = null; return true
}

// ══════════════════════════════════════════════════════════════
// VALIDAÇÕES — Veículo
// ══════════════════════════════════════════════════════════════
const bloquearPlacaInvalida = (e) => {
  const permitidas = ['Backspace','Delete','Tab','ArrowLeft','ArrowRight','Home','End']
  if (e.ctrlKey || e.metaKey) return
  if (permitidas.includes(e.key)) return
  if (!/^[a-zA-Z0-9]$/.test(e.key)) e.preventDefault()
}
const aplicarMascaraPlaca = () => {
  let v = formVei.value.placa.toUpperCase().replace(/[^A-Z0-9-]/g, '')
  const limpo = v.replace(/-/g, '').slice(0, 7)
  v = limpo.length > 3 ? limpo.slice(0, 3) + '-' + limpo.slice(3) : limpo
  formVei.value.placa = v; erroPlacaVei.value = null
}
const validarPlaca = () => {
  const placa = formVei.value.placa.toUpperCase()
  if (!/^[A-Z]{3}-\d{4}$/.test(placa) && !/^[A-Z]{3}-\d[A-Z]\d{2}$/.test(placa)) {
    erroPlacaVei.value = 'Placa inválida. Use ABC-1234 ou ABC-1D23.'; return false
  }
  erroPlacaVei.value = null; return true
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
const bloquearResponsavelInvalido = (e) => {
  const permitidas = ['Backspace','Delete','Tab','ArrowLeft','ArrowRight','Home','End',' ']
  if (e.ctrlKey || e.metaKey) return
  if (permitidas.includes(e.key)) return
  if (!/^[\p{L}'\-]$/u.test(e.key)) e.preventDefault()
}
const onInputCustoRev = () => {
  const digits = custoExibicaoRev.value.replace(/\D/g, '').slice(0, 7)
  if (!digits) {
    custoExibicaoRev.value = ''; formRev.value.custo = ''; erroCustoRev.value = null; return
  }
  const num = parseInt(digits, 10) / 100
  formRev.value.custo    = num.toFixed(2)
  custoExibicaoRev.value = num.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
  erroCustoRev.value = num > CUSTO_MAXIMO
    ? `Valor máximo permitido é R$ 12.000,00. Atual: ${custoExibicaoRev.value}`
    : null
}
const bloquearCustoExcedente = (e) => {
  const controle = ['Backspace','Delete','Tab','ArrowLeft','ArrowRight','Home','End']
  if (e.ctrlKey || e.metaKey || controle.includes(e.key)) return
  if (!/^\d$/.test(e.key)) return
  const digits = custoExibicaoRev.value.replace(/\D/g, '')
  if (digits.length >= 7) e.preventDefault()
}

// ══════════════════════════════════════════════════════════════
// HELPERS
// ══════════════════════════════════════════════════════════════
const badgeTipo = (tipo) => {
  const mapa = { 'Carro':'badge badge-carro','Moto':'badge badge-moto','Triciclo':'badge badge-masculino','Caminhão':'badge badge-feminino' }
  return mapa[tipo] || 'badge'
}
const formatarData  = (d) => { if (!d) return '—'; const [a,m,dia] = d.split('-'); return `${dia}/${m}/${a}` }
const formatarMoeda = (v) => Number(v).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
const formatarKm    = (k) => Number(k).toLocaleString('pt-BR') + ' km'
const exibirMensagem    = (texto, tipo) => { mensagem.value    = { texto, tipo }; setTimeout(() => { mensagem.value    = null }, 4000) }
const exibirMensagemVei = (texto, tipo) => { mensagemVei.value = { texto, tipo }; setTimeout(() => { mensagemVei.value = null }, 4000) }
const exibirMensagemRev = (texto, tipo) => { mensagemRev.value = { texto, tipo }; setTimeout(() => { mensagemRev.value = null }, 4000) }
</script>

<style scoped>
/* ═══════════════════════════════════════════════════
   TRANSIÇÕES — slide dos subpaineis
═══════════════════════════════════════════════════ */
.slide-veiculos-enter-active,
.slide-veiculos-leave-active,
.slide-revisoes-enter-active,
.slide-revisoes-leave-active {
  transition: transform 0.32s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.32s ease;
}
.slide-veiculos-enter-from,
.slide-veiculos-leave-to,
.slide-revisoes-enter-from,
.slide-revisoes-leave-to {
  transform: translateX(40px);
  opacity: 0;
}

/* ═══════════════════════════════════════════════════
   SUBPAINEIS
═══════════════════════════════════════════════════ */
.veiculos-subpanel,
.revisoes-subpanel { padding-bottom: 40px; }

.subpanel-header {
  display: flex; align-items: center; gap: 16px;
  padding: 14px 0 18px; border-bottom: 2px solid #e5e7eb;
  margin-bottom: 20px; flex-wrap: wrap;
}
.btn-voltar {
  background: none; border: 1.5px solid #d1d5db; color: #374151;
  padding: 7px 14px; border-radius: 6px; cursor: pointer;
  font-size: 0.88rem; font-weight: 600;
  transition: background 0.15s, border-color 0.15s; white-space: nowrap;
}
.btn-voltar:hover { background: #f3f4f6; border-color: #9ca3af; }
.subpanel-titulo { flex: 1; display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; }
.subpanel-titulo h2 {
  font-size: 1.15rem; font-weight: 700; margin: 0; color: #111827;
  display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap;
}
.subpanel-sub { font-size: 0.85rem; font-weight: 400; color: #6b7280; }

.subpanel-badge {
  font-size: 0.75rem; font-weight: 600; background: #f0fdf4; color: #16a34a;
  padding: 3px 8px; border-radius: 20px; border: 1px solid #bbf7d0; white-space: nowrap;
}
.subpanel-badge--rev { background: #eff6ff; color: #2563eb; border-color: #bfdbfe; }

.contador-resultados { font-size: 0.82rem; color: #6b7280; margin: 0 0 10px; }

/* ═══════════════════════════════════════════════════
   ORDENAÇÃO — cabeçalhos clicáveis
═══════════════════════════════════════════════════ */
.col-ordenavel {
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
  transition: background-color 0.15s, color 0.15s;
}
.col-ordenavel:hover {
  background-color: #eff6ff;
  color: #2563eb;
}
/* Destaque visual quando a coluna está ativa (contém ↑ ou ↓) */
.col-ordenavel:has(.sort-icon:not(:empty)) {
  color: inherit;
}
.sort-icon {
  display: inline-block;
  margin-left: 4px;
  font-size: 0.75rem;
  color: #9ca3af;
  vertical-align: middle;
  transition: color 0.15s;
}
.col-ordenavel:hover .sort-icon {
  color: #2563eb;
}

/* ═══════════════════════════════════════════════════
   TABELA DE VEÍCULOS
═══════════════════════════════════════════════════ */
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

/* ═══════════════════════════════════════════════════
   TABELA DE REVISÕES
═══════════════════════════════════════════════════ */
.tabela-revisoes-wrapper { width: 100%; overflow-x: auto; }
.tabela-revisoes { width: 100%; min-width: 780px; table-layout: fixed; border-collapse: collapse; }
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
.td-descricao { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.td-km, .td-custo { text-align: right; }
.acoes-cell { display: flex; align-items: center; justify-content: flex-end; gap: 6px; flex-wrap: wrap; }

/* ═══════════════════════════════════════════════════
   TABELA PRINCIPAL — Proprietários
═══════════════════════════════════════════════════ */
.col-acoes-prop { width: 190px; min-width: 190px; }
.acoes-cell-prop { display: flex; align-items: center; justify-content: center; gap: 5px; white-space: nowrap; }
table tbody tr td { vertical-align: middle; }
.btn-xs {
  padding: 3px 8px; font-size: 0.75rem; border-radius: 5px;
  line-height: 1.4; cursor: pointer; border: none; font-weight: 500; transition: opacity 0.15s;
}
.btn-xs:hover { opacity: 0.85; }

/* ═══════════════════════════════════════════════════
   FILTROS
═══════════════════════════════════════════════════ */
.filtros { display: flex; gap: 10px; margin-bottom: 14px; flex-wrap: wrap; align-items: center; }
.filtro-input, .filtro-select {
  padding: 7px 10px; border: 1px solid #d1d5db; border-radius: 6px;
  font-size: 0.88rem; background: #fff; color: #111827;
}
.filtro-input  { flex: 1; min-width: 180px; }
.filtro-select { min-width: 140px; }

/* ═══════════════════════════════════════════════════
   OFFCANVAS
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
  font-size: 1.1rem; cursor: pointer; padding: 4px 8px; border-radius: 4px; transition: color 0.2s;
}
.offcanvas-fechar:hover { color: #fff; }
.offcanvas-body { flex: 1; overflow-y: auto; padding: 24px; }
.offcanvas-footer {
  display: flex; justify-content: flex-end; gap: 10px;
  padding: 16px 24px; border-top: 1px solid #e5e7eb;
  background: #f9fafb; flex-shrink: 0; margin-top: 20px;
}

/* ═══════════════════════════════════════════════════
   DETALHES — modais
═══════════════════════════════════════════════════ */
.detalhe-header        { align-items: flex-start; }
.detalhe-nome          { font-size: 1.2rem; font-weight: 700; margin: 0; }
.detalhe-meta-veiculo  { font-size: 0.82rem; color: #6b7280; margin: 4px 0 0; }
.detalhes-grid         { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; padding: 20px 24px; }
.detalhe-item          { display: flex; flex-direction: column; gap: 4px; }
.detalhe-item-full     { grid-column: 1 / -1; }
.detalhe-label         { font-size: 0.72rem; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; }
.detalhe-valor         { font-size: 0.95rem; font-weight: 500; color: #111827; }
.detalhe-descricao     { white-space: pre-wrap; word-break: break-word; }
.detalhe-custo         { color: #16a34a; font-weight: 700; }

/* ═══════════════════════════════════════════════════
   FORMULÁRIO
═══════════════════════════════════════════════════ */
.form-separador {
  font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.08em; color: #6b7280;
  border-top: 1px solid #e5e7eb; padding-top: 14px; margin: 16px 0 12px;
}
.input-disabled  { background: #f3f4f6; color: #6b7280; cursor: not-allowed; opacity: 0.8; }
.campo-info      { display: block; font-size: 0.72rem; color: #9ca3af; margin-top: 2px; }
.campo-contador  { display: block; text-align: right; font-size: 0.72rem; color: #9ca3af; margin-top: 2px; }
.label-hint      { font-size: 0.72rem; color: #ef4444; font-weight: 400; margin-left: 4px; }
select:disabled  { background: #f3f4f6; color: #9ca3af; cursor: not-allowed; opacity: 0.7; }
</style>