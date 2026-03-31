# api/cache_keys.py

# ================================================================
# TTLs (em segundos)
# ================================================================
TTL_RELATORIO = 60 * 10   # 10 min — relatórios são pesados e raramente mudam
TTL_LISTAGEM  = 60 * 2    # 2 min  — listagens mudam ao criar/editar/deletar
TTL_DETALHE   = 60 * 5    # 5 min  — detalhe por ID

# ================================================================
# Chaves fixas — relatórios sem parâmetros variáveis
# ================================================================
KEY_USUARIOS_GENERO      = "relatorio:usuarios_genero"
KEY_MARCAS_RANKING       = "relatorio:marcas_ranking"
KEY_MARCAS_GENERO        = "relatorio:marcas_genero"
KEY_GENERO_VEICULOS      = "relatorio:genero_veiculos"
KEY_VEICULOS_PROPRIETARIO_REL = "relatorio:veiculos_proprietario"
KEY_MARCAS_REVISOES      = "relatorio:marcas_revisoes"
KEY_PESSOAS_REVISOES     = "relatorio:pessoas_revisoes"
KEY_MEDIA_TEMPO          = "relatorio:media_tempo"
KEY_PROXIMAS_REVISOES    = "relatorio:proximas_revisoes"

# ================================================================
# Chaves dinâmicas — incluem parâmetros na chave
# ================================================================

# Listagem de usuários: varia por página, busca e ordenação
KEY_USUARIOS_LIST = "usuarios:list:v{v}:{page}:{search}:{ordering}"

# Veículos de um proprietário específico
KEY_VEICULOS_DE_PROPRIETARIO = "veiculos:prop:{pk}"

# Revisões de um veículo específico
KEY_REVISOES_DE_VEICULO = "revisoes:veiculo:{pk}"

# Relatório de revisões por período: varia por início e fim
KEY_REVISOES_PERIODO = "relatorio:revisoes_periodo:{inicio}:{fim}"

# ================================================================
# Chave de versão — usada para invalidar listagens em massa
# sem precisar do delete_pattern do Redis.
# Ao incrementar esta versão, todas as chaves de listagem
# que a incluem no nome ficam automaticamente obsoletas.
# ================================================================
KEY_VERSAO_USUARIOS = "v:usuarios"