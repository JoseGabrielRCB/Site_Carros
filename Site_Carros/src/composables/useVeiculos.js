import { ref, computed, watch } from 'vue'
import api from '@/services/api'
import { criarOrdenacao, aplicarOrdenacao } from './useOrdenacao'
import { useMensagem } from './useFormatters'

const ITENS_VEI = 10

export const MARCA_MODELOS = {
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

const FORM_VEI_VAZIO = {
  proprietario: '', placa: '', marca: '', modelo: '', ano: '', tipo: '',
  numero_portas: '', tipo_combustivel: '', ar_condicionado: true,
  cilindradas: '', tipo_partida: '', refrigeracao: '',
  tipo_tracao: '', capacidade_carga: '',
  quantidade_eixos: '', capacidade_toneladas: '', tipo_carroceria: '',
}

export function useVeiculos(usuarios) {
  // ── Estado ─────────────────────────────────────────────────
  const panelVeiculos         = ref(false)
  const proprietarioVeiculos  = ref(null)
  const veiculosDoProprietario = ref([])
  const carregandoVei         = ref(false)
  const salvandoVei           = ref(false)
  const mensagemVei           = ref(null)
  const erroFormVei           = ref(null)
  const erroPlacaVei          = ref(null)
  const panelVeiculoForm      = ref(false)
  const modalDetalhesVei      = ref(false)
  const modalDeletarVei       = ref(false)
  const modoEdicaoVei         = ref(false)
  const veiculoSelecionadoVei = ref(null)
  const veiculoDetalhes       = ref(null)
  const filtroTextoVei        = ref('')
  const filtroTipoVei         = ref('')
  const paginaAtualVei        = ref(1)
  const anoAtual              = new Date().getFullYear()
  const formVei               = ref({ ...FORM_VEI_VAZIO })
  const ordenacaoVei          = criarOrdenacao('placa', 'asc')

  const { exibir: exibirMensagemVei } = useMensagem(mensagemVei)

  // ── Computeds ──────────────────────────────────────────────
  const modelosDisponiveisVei = computed(() =>
    formVei.value.marca ? (MARCA_MODELOS[formVei.value.marca] ?? []) : []
  )

  const veiculosFiltradosVei = computed(() => {
    const lista = veiculosDoProprietario.value.filter(v => {
      const texto = filtroTextoVei.value.toLowerCase()
      const bateTexto = !texto ||
        v.placa.toLowerCase().includes(texto) ||
        v.marca.toLowerCase().includes(texto) ||
        v.modelo.toLowerCase().includes(texto)
      return bateTexto && (!filtroTipoVei.value || v.tipo === filtroTipoVei.value)
    })
    return aplicarOrdenacao(lista, ordenacaoVei, ['ano'])
  })

  const totalPaginasVei = computed(() =>
    Math.ceil(veiculosFiltradosVei.value.length / ITENS_VEI)
  )

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

  watch(() => formVei.value.marca, () => { formVei.value.modelo = '' })
  watch([filtroTextoVei, filtroTipoVei], () => { paginaAtualVei.value = 1 })
  watch(ordenacaoVei, () => { paginaAtualVei.value = 1 }, { deep: true })

  // ── Ações ──────────────────────────────────────────────────
  const abrirVeiculos = async (usuario) => {
    proprietarioVeiculos.value = usuario
    panelVeiculos.value        = true
    filtroTextoVei.value       = ''
    filtroTipoVei.value        = ''
    paginaAtualVei.value       = 1
    carregandoVei.value        = true
    try {
      const { data } = await api.get(`veiculos/proprietario/${usuario.id}/`)
      veiculosDoProprietario.value = data
    } catch {
      exibirMensagemVei('Erro ao carregar veículos.', 'erro')
    } finally {
      carregandoVei.value = false
    }
  }

  const fecharVeiculos = () => {
    panelVeiculos.value          = false
    proprietarioVeiculos.value   = null
    veiculosDoProprietario.value = []
    panelVeiculoForm.value       = false
    modalDetalhesVei.value       = false
    modalDeletarVei.value        = false
  }

  const irParaPaginaVei = (n) => {
    if (n >= 1 && n <= totalPaginasVei.value) paginaAtualVei.value = n
  }

  const limparFiltrosVei = () => {
    filtroTextoVei.value = ''
    filtroTipoVei.value  = ''
  }

  const abrirModalDetalhesVei = (v) => {
    veiculoDetalhes.value  = v
    modalDetalhesVei.value = true
  }

  const abrirModalCriarVeiculo = () => {
    modoEdicaoVei.value = false
    formVei.value = { ...FORM_VEI_VAZIO, proprietario: proprietarioVeiculos.value.id }
    erroFormVei.value = erroPlacaVei.value = null
    panelVeiculoForm.value = true
  }

  const abrirModalEditarVeiculo = (v) => {
    modoEdicaoVei.value      = true
    veiculoSelecionadoVei.value = v
    formVei.value = {
      ...FORM_VEI_VAZIO,
      proprietario: v.proprietario, placa: v.placa,
      marca: v.marca, modelo: v.modelo, ano: v.ano,
      tipo: v.tipo?.toLowerCase().replace('ã', 'a') || ''
    }
    erroFormVei.value = erroPlacaVei.value = null
    panelVeiculoForm.value = true
  }

  const fecharModalVeiculo = () => {
    panelVeiculoForm.value = false
    erroFormVei.value = erroPlacaVei.value = null
  }

  const confirmarDeletarVei = (v) => {
    veiculoSelecionadoVei.value = v
    modalDeletarVei.value = true
  }

  const montarPayloadVeiculo = () => {
    const base = {
      proprietario: formVei.value.proprietario, placa: formVei.value.placa,
      marca: formVei.value.marca, modelo: formVei.value.modelo,
      ano: formVei.value.ano, tipo: formVei.value.tipo
    }
    const extras = {
      carro:    { numero_portas: formVei.value.numero_portas, tipo_combustivel: formVei.value.tipo_combustivel, ar_condicionado: formVei.value.ar_condicionado },
      moto:     { cilindradas: formVei.value.cilindradas, tipo_partida: formVei.value.tipo_partida, refrigeracao: formVei.value.refrigeracao },
      triciclo: { tipo_tracao: formVei.value.tipo_tracao, capacidade_carga: formVei.value.capacidade_carga },
      caminhao: { quantidade_eixos: formVei.value.quantidade_eixos, capacidade_toneladas: formVei.value.capacidade_toneladas, tipo_carroceria: formVei.value.tipo_carroceria },
    }
    return { ...base, ...(extras[formVei.value.tipo] || {}) }
  }

  const salvarVeiculo = async () => {
    if (!validarPlaca()) return
    salvandoVei.value = true
    erroFormVei.value = null
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
    } finally {
      salvandoVei.value = false
    }
  }

  const deletarVei = async () => {
    salvandoVei.value = true
    try {
      await api.delete(`veiculos/${veiculoSelecionadoVei.value.id}/delete/`)
      veiculosDoProprietario.value = veiculosDoProprietario.value.filter(
        v => v.id !== veiculoSelecionadoVei.value.id
      )
      const prop = usuarios.value.find(u => u.id === proprietarioVeiculos.value.id)
      if (prop && prop.total_veiculos > 0) prop.total_veiculos -= 1
      modalDeletarVei.value = false
      exibirMensagemVei(`Veículo ${veiculoSelecionadoVei.value.placa} excluído.`, 'sucesso')
    } catch {
      exibirMensagemVei('Erro ao excluir veículo.', 'erro')
    } finally {
      salvandoVei.value = false
    }
  }

  // ── Validações ─────────────────────────────────────────────
  const bloquearPlacaInvalida = (e) => {
    const permitidas = ['Backspace','Delete','Tab','ArrowLeft','ArrowRight','Home','End']
    if (e.ctrlKey || e.metaKey || permitidas.includes(e.key)) return
    if (!/^[a-zA-Z0-9]$/.test(e.key)) e.preventDefault()
  }

  const aplicarMascaraPlaca = () => {
    let v = formVei.value.placa.toUpperCase().replace(/[^A-Z0-9-]/g, '')
    const limpo = v.replace(/-/g, '').slice(0, 7)
    v = limpo.length > 3 ? limpo.slice(0, 3) + '-' + limpo.slice(3) : limpo
    formVei.value.placa = v
    erroPlacaVei.value  = null
  }

  const validarPlaca = () => {
    const placa = formVei.value.placa.toUpperCase()
    if (!/^[A-Z]{3}-\d{4}$/.test(placa) && !/^[A-Z]{3}-\d[A-Z]\d{2}$/.test(placa)) {
      erroPlacaVei.value = 'Placa inválida. Use ABC-1234 ou ABC-1D23.'; return false
    }
    erroPlacaVei.value = null; return true
  }

  return {
    // estado
    panelVeiculos, proprietarioVeiculos, veiculosDoProprietario,
    carregandoVei, salvandoVei, mensagemVei, erroFormVei, erroPlacaVei,
    panelVeiculoForm, modalDetalhesVei, modalDeletarVei,
    modoEdicaoVei, veiculoSelecionadoVei, veiculoDetalhes,
    filtroTextoVei, filtroTipoVei, paginaAtualVei, anoAtual,
    formVei, ordenacaoVei,
    // computeds
    modelosDisponiveisVei, veiculosFiltradosVei,
    totalPaginasVei, veiculosPaginadosVei, paginasVisiveisVei,
    // ações
    abrirVeiculos, fecharVeiculos, irParaPaginaVei, limparFiltrosVei,
    abrirModalDetalhesVei, abrirModalCriarVeiculo, abrirModalEditarVeiculo,
    fecharModalVeiculo, confirmarDeletarVei, salvarVeiculo, deletarVei,
    // validações
    bloquearPlacaInvalida, aplicarMascaraPlaca, validarPlaca,
  }
}