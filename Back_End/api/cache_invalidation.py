# api/cache_invalidation.py
from django.core.cache import cache
from .cache_keys import (
    KEY_USUARIOS_GENERO,
    KEY_MARCAS_RANKING,
    KEY_MARCAS_GENERO,
    KEY_GENERO_VEICULOS,
    KEY_VEICULOS_PROPRIETARIO_REL,
    KEY_MARCAS_REVISOES,
    KEY_PESSOAS_REVISOES,
    KEY_MEDIA_TEMPO,
    KEY_PROXIMAS_REVISOES,
    KEY_VEICULOS_DE_PROPRIETARIO,
    KEY_REVISOES_DE_VEICULO,
    KEY_VERSAO_USUARIOS,
)


def _incrementar_versao_usuarios():
    """
    Incrementa a versão das listagens de usuários.
    Como KEY_USUARIOS_LIST inclui {v} no nome, todas as chaves
    antigas ficam órfãs e o cache passa a errar (miss), forçando
    nova consulta ao banco. Funciona sem delete_pattern (sem Redis).
    """
    versao_atual = cache.get(KEY_VERSAO_USUARIOS, 1)
    cache.set(KEY_VERSAO_USUARIOS, versao_atual + 1, timeout=None)


def invalidar_cache_usuario():
    """
    Chamado ao criar, editar ou deletar um usuário.
    Afeta: relatório de gênero, relatório de veículos por gênero
    e todas as páginas da listagem de usuários.
    """
    cache.delete(KEY_USUARIOS_GENERO)
    cache.delete(KEY_GENERO_VEICULOS)
    _incrementar_versao_usuarios()


def invalidar_cache_veiculo(proprietario_id: int):
    """
    Chamado ao criar, editar ou deletar um veículo.
    Afeta: veículos daquele proprietário, relatórios de marcas,
    relatório de gênero e listagem de usuários (total_veiculos muda).

    :param proprietario_id: ID do proprietário do veículo alterado.
    """
    cache.delete(KEY_VEICULOS_DE_PROPRIETARIO.format(pk=proprietario_id))
    cache.delete(KEY_MARCAS_RANKING)
    cache.delete(KEY_MARCAS_GENERO)
    cache.delete(KEY_GENERO_VEICULOS)
    cache.delete(KEY_VEICULOS_PROPRIETARIO_REL)
    _incrementar_versao_usuarios()   # total_veiculos aparece na listagem


def invalidar_cache_revisao(veiculo_id: int):
    """
    Chamado ao criar, editar ou deletar uma revisão.
    Afeta: revisões daquele veículo e todos os relatórios de revisão.

    :param veiculo_id: ID do veículo cuja revisão foi alterada.
    """
    cache.delete(KEY_REVISOES_DE_VEICULO.format(pk=veiculo_id))
    cache.delete(KEY_MARCAS_REVISOES)
    cache.delete(KEY_PESSOAS_REVISOES)
    cache.delete(KEY_MEDIA_TEMPO)
    cache.delete(KEY_PROXIMAS_REVISOES)
    # revisoes_por_periodo usa chaves dinâmicas (inicio+fim);
    # como podem existir muitas combinações, usamos versão ou
    # deixamos expirar pelo TTL — já são dados históricos.