export const formatarData = (d) => {
  if (!d) return '—'
  const [a, m, dia] = d.split('-')
  return `${dia}/${m}/${a}`
}

export const formatarMoeda = (v) =>
  Number(v).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })

export const formatarKm = (k) =>
  Number(k).toLocaleString('pt-BR') + ' km'

export const badgeTipo = (tipo) => {
  const mapa = {
    'Carro':    'badge badge-carro',
    'Moto':     'badge badge-moto',
    'Triciclo': 'badge badge-masculino',
    'Caminhão': 'badge badge-feminino',
  }
  return mapa[tipo] || 'badge'
}

export const useMensagem = (ref) => {
  const exibir = (texto, tipo) => {
    ref.value = { texto, tipo }
    setTimeout(() => { ref.value = null }, 4000)
  }
  return { exibir }
}