import { ref } from 'vue'

/**
 * Cria o estado de ordenação como um ref reativo.
 * Uso interno (JS): `estado.value.coluna`
 * Uso no template (passado p/ funções): Vue faz unwrap → objeto bruto
 */
export const criarOrdenacao = (colunaInicial = '', direcaoInicial = 'asc') =>
  ref({ coluna: colunaInicial, direcao: direcaoInicial })

/**
 * Chamada pelo template via @click.
 * Recebe o objeto bruto { coluna, direcao } (Vue já fez o unwrap do ref).
 */
export const alternarOrdenacao = (estado, col) => {
  if (estado.coluna === col) {
    estado.direcao = estado.direcao === 'asc' ? 'desc' : 'asc'
  } else {
    estado.coluna  = col
    estado.direcao = 'asc'
  }
}

/**
 * Chamada pelo template via {{ }}.
 * Retorna: ↕ (inativo) | ↑ (asc) | ↓ (desc)
 */
export const iconeOrdenacao = (estado, col) => {
  if (!estado || estado.coluna !== col) return '↕'
  return estado.direcao === 'asc' ? '↑' : '↓'
}

/**
 * Chamada dentro de computed (código JS puro).
 * Suporta strings (localeCompare pt-BR), números e datas ISO.
 * @param {Array}  lista      — array de objetos já filtrado
 * @param {Ref}    estadoRef  — ref({ coluna, direcao })
 * @param {Array}  numericos  — nomes de colunas numéricas
 */
export const aplicarOrdenacao = (lista, estadoRef, numericos = []) => {
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

    valA = valA == null ? '' : String(valA)
    valB = valB == null ? '' : String(valB)
    const cmp = valA.localeCompare(valB, 'pt-BR', { sensitivity: 'base' })
    return direcao === 'asc' ? cmp : -cmp
  })
}