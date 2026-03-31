import { ref, computed, watch } from 'vue'
import api from '@/services/api'
import { criarOrdenacao, aplicarOrdenacao } from './useOrdenacao'
import { useMensagem } from './useFormatters'

const ITENS_REV    = 10
const CUSTO_MAXIMO = 999999.99          // ← novo limite: R$ 999.999,99
const DATA_HOJE    = new Date().toISOString().split('T')[0]
const DATA_MINIMA  = '2020-12-01'

const FORM_REV_VAZIO = {
  veiculo: '', data_revisao: '', quilometragem: '', descricao: '', responsavel: '', custo: ''
}

export function useRevisoes(veiculoRevisoes, proprietarioVeiculos) {
  // ── Estado ─────────────────────────────────────────────────
  const panelRevisoes      = ref(false)
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
  const custoExibicaoRev   = ref('')
  const formRev            = ref({ ...FORM_REV_VAZIO })
  const ordenacaoRev       = criarOrdenacao('data_revisao', 'desc')

  const { exibir: exibirMensagemRev } = useMensagem(mensagemRev)

  // ── Computeds ──────────────────────────────────────────────
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
    return aplicarOrdenacao(lista, ordenacaoRev, ['quilometragem', 'custo'])
  })

  const totalPaginasRev = computed(() =>
    Math.max(1, Math.ceil(revisoesFiltradas.value.length / ITENS_REV))
  )

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

  // ── Ações ──────────────────────────────────────────────────
  const abrirRevisoes = async (veiculo) => {
    veiculoRevisoes.value = veiculo
    panelRevisoes.value   = true
    filtroTextoRev.value  = ''
    filtroInicioRev.value = ''
    filtroFimRev.value    = ''
    paginaAtualRev.value  = 1
    carregandoRev.value   = true
    try {
      const { data } = await api.get(`revisoes/veiculo/${veiculo.id}/`)
      revisoes.value = data
    } catch {
      exibirMensagemRev('Erro ao carregar revisões.', 'erro')
    } finally {
      carregandoRev.value = false
    }
  }

  const fecharRevisoes = () => {
    panelRevisoes.value    = false
    revisoes.value         = []
    panelRevisaoForm.value = false
    modalDetalhesRev.value = false
    modalDeletarRev.value  = false
  }

  const irParaPaginaRev = (n) => {
    if (n >= 1 && n <= totalPaginasRev.value) paginaAtualRev.value = n
  }

  const limparFiltrosRev = () => {
    filtroTextoRev.value  = ''
    filtroInicioRev.value = ''
    filtroFimRev.value    = ''
  }

  const abrirModalDetalhesRev = (r) => {
    revisaoDetalhes.value  = r
    modalDetalhesRev.value = true
  }

  const abrirModalCriarRevisao = () => {
    modoEdicaoRev.value = false
    formRev.value = { ...FORM_REV_VAZIO, veiculo: veiculoRevisoes.value.id }
    erroFormRev.value = erroDataRev.value = erroCustoRev.value = null
    custoExibicaoRev.value = ''
    panelRevisaoForm.value = true
  }

  const abrirModalEditarRev = (r) => {
    modoEdicaoRev.value      = true
    revisaoSelecionada.value = r
    formRev.value = {
      veiculo:        r.veiculo,
      data_revisao:   r.data_revisao,
      quilometragem:  r.quilometragem,
      descricao:      r.descricao,
      responsavel:    r.responsavel,
      custo:          r.custo,
    }
    custoExibicaoRev.value = parseFloat(r.custo || 0)
      .toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
    erroFormRev.value = erroDataRev.value = erroCustoRev.value = null
    panelRevisaoForm.value = true
  }

  const fecharModalRev = () => {
    panelRevisaoForm.value = false
    erroFormRev.value = erroDataRev.value = erroCustoRev.value = null
  }

  const confirmarDeletarRev = (r) => {
    revisaoSelecionada.value = r
    modalDeletarRev.value    = true
  }

  const salvarRev = async () => {
    if (!validarDataRev()) return
    const custoNum = parseFloat(formRev.value.custo)
    if (!formRev.value.custo || isNaN(custoNum) || custoNum <= 0) {
      erroCustoRev.value = 'Informe um valor válido maior que R$ 0,00.'; return
    }
    if (custoNum > CUSTO_MAXIMO) {
      erroCustoRev.value = 'O valor não pode ultrapassar R$ 999.999,99.'; return
    }
    salvandoRev.value = true
    erroFormRev.value = null
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
          veiculo_placa:     veiculoRevisoes.value.placa,
          veiculo_marca:     veiculoRevisoes.value.marca,
          veiculo_modelo:    veiculoRevisoes.value.modelo,
          proprietario_nome: proprietarioVeiculos.value?.nome,
        })
        exibirMensagemRev('Revisão criada com sucesso.', 'sucesso')
      }
      fecharModalRev()
    } catch (e) {
      const erros = e.response?.data
      erroFormRev.value = erros ? Object.values(erros).flat().join(' ') : 'Erro ao salvar a revisão.'
    } finally {
      salvandoRev.value = false
    }
  }

  const deletarRev = async () => {
    salvandoRev.value = true
    try {
      await api.delete(`revisoes/${revisaoSelecionada.value.id}/delete/`)
      revisoes.value = revisoes.value.filter(r => r.id !== revisaoSelecionada.value.id)
      modalDeletarRev.value = false
      exibirMensagemRev('Revisão excluída com sucesso.', 'sucesso')
    } catch {
      exibirMensagemRev('Erro ao excluir a revisão.', 'erro')
    } finally {
      salvandoRev.value = false
    }
  }

  // ── Validações ─────────────────────────────────────────────
  const validarDataRev = () => {
    const d = formRev.value.data_revisao
    if (!d) return true
    if (d > DATA_HOJE)   { erroDataRev.value = 'Não é permitido selecionar datas futuras.'; return false }
    if (d < DATA_MINIMA) { erroDataRev.value = 'Não são aceitas revisões anteriores a dezembro de 2020.'; return false }
    erroDataRev.value = null; return true
  }

  const bloquearResponsavelInvalido = (e) => {
    const permitidas = ['Backspace','Delete','Tab','ArrowLeft','ArrowRight','Home','End',' ']
    if (e.ctrlKey || e.metaKey || permitidas.includes(e.key)) return
    if (!/^[\p{L}'\-]$/u.test(e.key)) e.preventDefault()
  }

  /**
   * Recebe { exibicao, custo, erro } emitido pelo filho RevisoesPanel.
   * Atualiza custoExibicaoRev, formRev.custo e erroCustoRev de forma síncrona.
   */
  const onInputCustoRev = ({ exibicao, custo, erro }) => {
    custoExibicaoRev.value = exibicao
    formRev.value.custo    = custo
    erroCustoRev.value     = erro
  }

  const bloquearCustoExcedente = (e) => {
    const controle = ['Backspace','Delete','Tab','ArrowLeft','ArrowRight','Home','End']
    if (e.ctrlKey || e.metaKey || controle.includes(e.key)) return
    if (!/^\d$/.test(e.key)) return
    const digits = custoExibicaoRev.value.replace(/\D/g, '')
    if (digits.length >= 8) e.preventDefault()   // 8 dígitos = R$ 999.999,99
  }

  return {
    // estado
    panelRevisoes, revisoes, carregandoRev, salvandoRev, mensagemRev,
    erroFormRev, erroDataRev, erroCustoRev, panelRevisaoForm,
    modalDetalhesRev, modalDeletarRev, modoEdicaoRev,
    revisaoSelecionada, revisaoDetalhes,
    filtroTextoRev, filtroInicioRev, filtroFimRev,
    paginaAtualRev, custoExibicaoRev, formRev, ordenacaoRev,
    // constantes
    dataHoje: DATA_HOJE,
    dataMinima: DATA_MINIMA,
    // computeds
    revisoesFiltradas, totalPaginasRev, revisoesPaginadasRev,
    paginasVisiveisRev, totalCustosRev,
    // ações
    abrirRevisoes, fecharRevisoes, irParaPaginaRev, limparFiltrosRev,
    abrirModalDetalhesRev, abrirModalCriarRevisao, abrirModalEditarRev,
    fecharModalRev, confirmarDeletarRev, salvarRev, deletarRev,
    // validações
    validarDataRev, bloquearResponsavelInvalido,
    onInputCustoRev, bloquearCustoExcedente,
  }
}