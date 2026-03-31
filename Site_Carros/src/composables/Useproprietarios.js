import { ref, computed, watch } from 'vue'
import api from '@/services/api'
import { criarOrdenacao } from './useOrdenacao'
import { useMensagem } from './useFormatters'

const FORM_VAZIO = {
  nome: '', cpf: '', genero: '', data_nascimento: '', endereco: '', cep: ''
}

export function useProprietarios() {
  // ── Estado ─────────────────────────────────────────────────
  const usuarios             = ref([])
  const carregando           = ref(true)
  const salvando             = ref(false)
  const mensagem             = ref(null)
  const erroForm             = ref(null)
  const erroCpf              = ref(null)
  const erroData             = ref(null)
  const panelAberto          = ref(false)
  const modalDeletar         = ref(false)
  const modoEdicao           = ref(false)
  const usuarioSelecionado   = ref(null)
  const termoBusca           = ref('')
  const paginaAtual          = ref(1)
  const totalRegistros       = ref(0)
  const totalPaginasServidor = ref(1)
  const form                 = ref({ ...FORM_VAZIO })
  const ordenacaoProp        = criarOrdenacao('nome', 'asc')

  // ── CEP ────────────────────────────────────────────────────
  const buscandoCep   = ref(false)
  const erroCep       = ref(null)
  const cepEncontrado = ref(false)

  const { exibir: exibirMensagem } = useMensagem(mensagem)

  // ── Computeds ──────────────────────────────────────────────
  const dataMaxima = computed(() => {
    const d = new Date()
    d.setFullYear(d.getFullYear() - 18)
    return d.toISOString().split('T')[0]
  })

  const COLUNAS_NUMERICAS = new Set(['idade', 'total_veiculos'])

  const usuariosPaginados = computed(() => {
    const { coluna, direcao } = ordenacaoProp.value
    if (!coluna) return usuarios.value

    return [...usuarios.value].sort((a, b) => {
      let vA = a[coluna], vB = b[coluna]
      if (COLUNAS_NUMERICAS.has(coluna)) {
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

  const totalPaginas = computed(() => totalPaginasServidor.value)

  const paginasVisiveis = computed(() => {
    const total = totalPaginas.value, atual = paginaAtual.value
    let inicio = Math.max(1, atual - 2)
    let fim    = Math.min(total, inicio + 4)
    if (fim - inicio < 4) inicio = Math.max(1, fim - 4)
    const p = []
    for (let i = inicio; i <= fim; i++) p.push(i)
    return p
  })


  // ── Ações ──────────────────────────────────────────────────

  // Remove tudo que não for dígito — permite buscar CPF com ou sem máscara
  const soDigitos = (v) => String(v ?? '').replace(/\D/g, '')

  const buscar = async () => {
    carregando.value = true
    try {
      const { coluna, direcao } = ordenacaoProp.value
      const ordering = coluna ? (direcao === 'desc' ? `-${coluna}` : coluna) : 'nome'

      const termoRaw     = termoBusca.value.trim()
      const termoDigitos = soDigitos(termoRaw)
      // Se o termo for composto só de dígitos/separadores, envia sem máscara para a API
      const searchParam  = termoRaw
        ? (/^[\d\W]+$/.test(termoRaw) ? termoDigitos : termoRaw)
        : undefined

      const { data } = await api.get('users/', {
        params: { page: paginaAtual.value, search: searchParam, ordering }
      })

      if (Array.isArray(data)) {
        const ITENS  = 10
        const inicio = (paginaAtual.value - 1) * ITENS
        const termo  = termoRaw.toLowerCase()

        const filtrado = termo
          ? data.filter(u => {
              if (u.nome.toLowerCase().includes(termo)) return true
              // Compara só os dígitos: cobre "07833371165", "078.333.711-65", "078-333-711.65"
              if (termoDigitos.length > 0 && soDigitos(u.cpf).includes(termoDigitos)) return true
              // Mantém busca por CPF formatado colado pelo usuário
              if (u.cpf.includes(termo)) return true
              return false
            })
          : data

        totalRegistros.value       = filtrado.length
        totalPaginasServidor.value = Math.max(1, Math.ceil(filtrado.length / ITENS))
        usuarios.value             = filtrado.slice(inicio, inicio + ITENS)
      } else {
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

  // debounce: aguarda 350ms após o usuário parar de digitar
  let debounceTimer = null
  watch(termoBusca, () => {
    paginaAtual.value = 1
    clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => buscar(), 350)
  })

  const irParaPagina = (n) => {
    if (n >= 1 && n <= totalPaginas.value && n !== paginaAtual.value) {
      paginaAtual.value = n
      buscar()
    }
  }

  const abrirModalCriar = () => {
    modoEdicao.value = false
    form.value = { ...FORM_VAZIO }
    erroForm.value = erroCpf.value = erroData.value = erroCep.value = null
    cepEncontrado.value = false
    panelAberto.value = true
  }

  const abrirModalEditar = (u) => {
    modoEdicao.value = true
    usuarioSelecionado.value = u
    form.value = {
      nome: u.nome, cpf: u.cpf, genero: u.genero,
      data_nascimento: u.data_nascimento,
      endereco: u.endereco || '',
      cep: u.cep || ''
    }
    erroForm.value = erroCpf.value = erroData.value = erroCep.value = null
    cepEncontrado.value = !!u.cep
    panelAberto.value = true
  }

  const fecharModal = () => {
    panelAberto.value = false
    erroForm.value = erroCpf.value = erroData.value = erroCep.value = null
    cepEncontrado.value = false
  }

  const salvar = async () => {
    if (!validarCpf() || !validarIdade()) return
    salvando.value = true
    erroForm.value = null
    try {
      if (modoEdicao.value) {
        const { data } = await api.put(`users/${usuarioSelecionado.value.id}/update/`, form.value)
        exibirMensagem(`Proprietário ${data.nome} atualizado.`, 'sucesso')
      } else {
        const { data } = await api.post('users/creat/', form.value)
        exibirMensagem(`Proprietário ${data.nome} criado.`, 'sucesso')
      }
      fecharModal()
      await buscar()
    } catch (e) {
      const erros = e.response?.data
      erroForm.value = erros ? Object.values(erros).flat().join(' ') : 'Erro ao salvar.'
    } finally {
      salvando.value = false
    }
  }

  const confirmarDeletar = (u) => {
    usuarioSelecionado.value = u
    modalDeletar.value = true
  }

  const deletar = async () => {
    salvando.value = true
    try {
      const nome = usuarioSelecionado.value.nome
      await api.delete(`users/${usuarioSelecionado.value.id}/delete/`)
      modalDeletar.value = false
      exibirMensagem(`Proprietário ${nome} excluído.`, 'sucesso')
      if (usuarios.value.length === 1 && paginaAtual.value > 1) paginaAtual.value -= 1
      await buscar()
    } catch {
      exibirMensagem('Erro ao excluir.', 'erro')
    } finally {
      salvando.value = false
    }
  }

  // ── Validações ─────────────────────────────────────────────
  const bloquearCpfInvalido = (e) => {
    const permitidas = ['Backspace','Delete','Tab','ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Home','End']
    if (e.ctrlKey || e.metaKey || permitidas.includes(e.key)) return
    if (!/^\d$/.test(e.key)) e.preventDefault()
  }

  const aplicarMascaraCpf = () => {
    let v = form.value.cpf.replace(/\D/g, '').slice(0, 11)
    if (v.length > 9)      v = v.replace(/(\d{3})(\d{3})(\d{3})(\d{0,2})/, '$1.$2.$3-$4')
    else if (v.length > 6) v = v.replace(/(\d{3})(\d{3})(\d{0,3})/, '$1.$2.$3')
    else if (v.length > 3) v = v.replace(/(\d{3})(\d{0,3})/, '$1.$2')
    form.value.cpf = v
    erroCpf.value = null
  }

  const validarCpf = () => {
    const cpf = form.value.cpf.replace(/\D/g, '')
    if (cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) {
      erroCpf.value = 'CPF inválido.'; return false
    }
    const calc  = (f) => cpf.slice(0, f - 1).split('').reduce((a, d, i) => a + Number(d) * (f - i), 0)
    const resto = (s) => { const r = (s * 10) % 11; return r >= 10 ? 0 : r }
    if (resto(calc(10)) !== Number(cpf[9]) || resto(calc(11)) !== Number(cpf[10])) {
      erroCpf.value = 'CPF inválido.'; return false
    }
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

  // ── CEP / ViaCEP ───────────────────────────────────────────
  const bloquearCepInvalido = (e) => {
    const permitidas = ['Backspace','Delete','Tab','ArrowLeft','ArrowRight','Home','End']
    if (e.ctrlKey || e.metaKey || permitidas.includes(e.key)) return
    if (!/^\d$/.test(e.key)) e.preventDefault()
  }

  const aplicarMascaraCep = () => {
    let v = form.value.cep.replace(/\D/g, '').slice(0, 8)
    if (v.length > 5) v = v.replace(/(\d{5})(\d{0,3})/, '$1-$2')
    form.value.cep = v
    erroCep.value = null
    cepEncontrado.value = false
    form.value.endereco = ''
  }

  const buscarCep = async () => {
    const cepLimpo = form.value.cep.replace(/\D/g, '')
    if (cepLimpo.length !== 8) {
      if (cepLimpo.length > 0) erroCep.value = 'CEP deve conter 8 dígitos.'
      return
    }
    buscandoCep.value   = true
    erroCep.value       = null
    cepEncontrado.value = false
    form.value.endereco = ''
    try {
      const res  = await fetch(`https://viacep.com.br/ws/${cepLimpo}/json/`)
      const data = await res.json()
      if (data.erro) { erroCep.value = 'CEP não encontrado.'; return }
      const partes = [data.logradouro, data.bairro, data.localidade, data.uf].filter(Boolean)
      form.value.endereco = partes.join(', ')
      cepEncontrado.value = true
    } catch {
      erroCep.value = 'Erro ao consultar o CEP. Verifique sua conexão.'
    } finally {
      buscandoCep.value = false
    }
  }

  return {
    // estado
    usuarios, carregando, salvando, mensagem, erroForm,
    erroCpf, erroData, panelAberto, modalDeletar,
    modoEdicao, usuarioSelecionado, termoBusca,
    paginaAtual, totalRegistros, form, ordenacaoProp,
    // CEP
    buscandoCep, erroCep, cepEncontrado,
    // computeds
    dataMaxima, usuariosPaginados, totalPaginas, paginasVisiveis,
    // ações
    buscar, irParaPagina,
    abrirModalCriar, abrirModalEditar, fecharModal,
    salvar, confirmarDeletar, deletar,
    // validações
    bloquearCpfInvalido, aplicarMascaraCpf, validarCpf, validarIdade,
    // CEP
    bloquearCepInvalido, aplicarMascaraCep, buscarCep,
  }
}