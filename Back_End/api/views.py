# api/views.py
from rest_framework.decorators import api_view
from rest_framework.request    import Request
from rest_framework.response   import Response
from rest_framework            import status
from django.shortcuts          import get_object_or_404
from django.db.models          import Count, Avg, F, ExpressionWrapper, FloatField, Q
from django.db                 import connection
from django.core.cache         import cache
from datetime                  import date
from apps.core.models          import Usuario, Veiculo, Carro, Moto, Triciclo, Caminhao, Revisao
from .serializers              import (
    UsuarioSerializer,
    UsuarioDetalheSerializer,
    VeiculoSerializer,
    RevisaoSerializer,
)
from .cache_keys import (
    TTL_RELATORIO, TTL_LISTAGEM, TTL_DETALHE,
    KEY_USUARIOS_GENERO,
    KEY_MARCAS_RANKING,
    KEY_MARCAS_GENERO,
    KEY_GENERO_VEICULOS,
    KEY_VEICULOS_PROPRIETARIO_REL,
    KEY_MARCAS_REVISOES,
    KEY_PESSOAS_REVISOES,
    KEY_MEDIA_TEMPO,
    KEY_PROXIMAS_REVISOES,
    KEY_USUARIOS_LIST,
    KEY_VEICULOS_DE_PROPRIETARIO,
    KEY_REVISOES_DE_VEICULO,
    KEY_REVISOES_PERIODO,
    KEY_VERSAO_USUARIOS,
)
from .cache_invalidation import (
    invalidar_cache_usuario,
    invalidar_cache_veiculo,
    invalidar_cache_revisao,
)


# ================================================================
# HELPERS — Herança MTI
# ================================================================

# Mapeamento tipo (string do frontend) → subclasse concreta do model
TIPO_MODELO = {
    'carro':    Carro,
    'moto':     Moto,
    'triciclo': Triciclo,
    'caminhao': Caminhao,
}

def _inferir_tipo(veiculo: Veiculo) -> str:
    """
    Recebe um objeto Veiculo (tabela base) e retorna a string do tipo
    verificando qual subclasse concreta existe para ele.
    Usa hasattr + try/except para evitar queries desnecessárias.
    Retorna 'desconhecido' se nenhuma subclasse for encontrada.
    """
    for tipo, modelo in TIPO_MODELO.items():
        if hasattr(veiculo, tipo):
            try:
                getattr(veiculo, tipo)
                return tipo
            except modelo.DoesNotExist:
                pass
    return 'desconhecido'


# ================================================================
# USUARIOS
# Model: cpf, nome, genero, data_nascimento, endereco
# NÃO existem: cep, total_veiculos, idade (estes são derivados)
# ================================================================

@api_view(['GET'])
def get_Usuarios(request: Request):
    """
    Lista usuários com paginação server-side (10 por página).

    Query params:
      page     — página desejada (padrão: 1)
      search   — filtra por nome ou CPF
      ordering — campo de ordenação, prefixado com '-' para desc

    Campos de ordenação suportados:
      nome, cpf, genero, data_nascimento, endereco  → diretos no model
      total_veiculos → anotação Count('veiculos')
      idade          → derivado de data_nascimento (ordem invertida)

    Cache: versão + página + busca + ordering.
    A versão é incrementada em toda mutação de usuário ou veículo.
    """
    ITENS_POR_PAGINA = 10

    search   = request.query_params.get('search', '').strip()
    ordering = request.query_params.get('ordering', 'nome')
    try:
        page = max(1, int(request.query_params.get('page', 1)))
    except (ValueError, TypeError):
        page = 1

    # ── Cache lookup ──────────────────────────────────────────
    versao    = cache.get(KEY_VERSAO_USUARIOS, 1)
    cache_key = KEY_USUARIOS_LIST.format(
        v=versao, page=page, search=search, ordering=ordering
    )
    cached = cache.get(cache_key)
    if cached is not None:
        return Response(cached, status=status.HTTP_200_OK)

    # ── Filtro ────────────────────────────────────────────────
    qs = Usuario.objects.all()
    if search:
        qs = qs.filter(
            Q(nome__icontains=search) | Q(cpf__icontains=search)
        )

    # ── Ordenação ─────────────────────────────────────────────
    CAMPOS_VALIDOS = {'nome', 'cpf', 'genero', 'data_nascimento', 'endereco'}
    desc  = ordering.startswith('-')
    campo = ordering.lstrip('-')

    if campo == 'total_veiculos':
        qs       = qs.annotate(_total_veiculos=Count('veiculos'))
        db_field = '_total_veiculos'
    elif campo == 'idade':
        db_field = 'data_nascimento'
        desc     = not desc   # mais velho = data menor → inverte
    elif campo in CAMPOS_VALIDOS:
        db_field = campo
    else:
        db_field = 'nome'

    qs = qs.order_by(f"-{db_field}" if desc else db_field)

    # ── Paginação ─────────────────────────────────────────────
    total       = qs.count()
    total_pages = max(1, -(-total // ITENS_POR_PAGINA))
    page        = min(page, total_pages)
    inicio      = (page - 1) * ITENS_POR_PAGINA
    fim         = inicio + ITENS_POR_PAGINA

    serializer = UsuarioSerializer(qs[inicio:fim], many=True)
    resultado  = {
        'count':       total,
        'total_pages': total_pages,
        'page':        page,
        'results':     serializer.data,
    }
    cache.set(cache_key, resultado, TTL_LISTAGEM)
    return Response(resultado, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_Usuario(request: Request, pk: int):
    """
    Detalhe de um usuário com veículos e revisões aninhados.
    prefetch_related('veiculos__revisoes') evita N+1 queries.
    Sem cache: dados aninhados mudam com frequência.
    """
    usuario = get_object_or_404(
        Usuario.objects.prefetch_related('veiculos__revisoes'),
        pk=pk
    )
    serializer = UsuarioDetalheSerializer(usuario)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def creat_Usuario(request: Request):
    """
    Cria um novo usuário.
    Campos aceitos: nome, cpf, genero, data_nascimento, endereco.
    Invalida: listagem de usuários e relatório de gênero.
    """
    serializer = UsuarioSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        invalidar_cache_usuario()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_Usuario(request: Request, pk: int):
    """
    Atualiza um usuário existente (aceita campos parciais).
    Invalida: listagem de usuários e relatório de gênero.
    """
    usuario    = get_object_or_404(Usuario, pk=pk)
    serializer = UsuarioSerializer(usuario, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        invalidar_cache_usuario()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_Usuario(request: Request, pk: int):
    """
    Remove um usuário e em cascata seus veículos e revisões.
    Invalida: listagem de usuários e relatório de gênero.
    """
    usuario = get_object_or_404(Usuario, pk=pk)
    nome    = usuario.nome
    usuario.delete()
    invalidar_cache_usuario()
    return Response(
        {"message": f"Usuario {nome} deletado com sucesso."},
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
def usuarios_por_genero(request: Request):
    """
    Relatório: total de usuários e média de idade por gênero.
    Cache: chave fixa, TTL de 10 min.
    """
    cached = cache.get(KEY_USUARIOS_GENERO)
    if cached is not None:
        return Response(cached, status=status.HTTP_200_OK)

    resultado = Usuario.objects.values('genero').annotate(
        total       = Count('id'),
        idade_media = Avg(
            ExpressionWrapper(
                date.today().year - F('data_nascimento__year'),
                output_field=FloatField()
            )
        )
    )
    data = [
        {
            'genero':      'Masculino' if r['genero'] == 'M' else 'Feminino',
            'total':       r['total'],
            'idade_media': round(r['idade_media'] or 0, 1),
        }
        for r in resultado
    ]
    cache.set(KEY_USUARIOS_GENERO, data, TTL_RELATORIO)
    return Response(data, status=status.HTTP_200_OK)


# ================================================================
# VEICULOS
# Herança MTI: Veiculo é a tabela base.
# Subclasses: Carro, Moto, Triciclo, Caminhao — cada uma com tabela própria.
# O campo "tipo" NÃO existe no model — é inferido pela subclasse presente.
# ================================================================

@api_view(['GET'])
def get_Veiculos(request: Request):
    """
    Lista todos os veículos (tabela base). Sem cache: uso interno/admin.
    """
    veiculos   = Veiculo.objects.select_related('proprietario').all()
    serializer = VeiculoSerializer(veiculos, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_Veiculos_de_proprietario(request: Request, pk: int):
    """
    Lista todos os veículos de um proprietário específico.
    Cache: chave por ID do proprietário, TTL de 5 min.
    """
    cache_key = KEY_VEICULOS_DE_PROPRIETARIO.format(pk=pk)
    cached    = cache.get(cache_key)
    if cached is not None:
        return Response(cached, status=status.HTTP_200_OK)

    veiculos   = Veiculo.objects.filter(proprietario_id=pk).select_related('proprietario')
    serializer = VeiculoSerializer(veiculos, many=True)
    cache.set(cache_key, serializer.data, TTL_DETALHE)
    return Response(serializer.data)


@api_view(['POST'])
def creat_Veiculo(request: Request):
    """
    Cria um veículo na subclasse correta conforme o campo 'tipo' enviado.

    Payload base (todos os tipos):
      proprietario, placa, marca, modelo, ano, tipo

    Campos extras por tipo:
      carro    → numero_portas, tipo_combustivel, ar_condicionado
      moto     → cilindradas, tipo_partida, refrigeracao
      triciclo → tipo_tracao, capacidade_carga
      caminhao → quantidade_eixos, capacidade_toneladas, tipo_carroceria

    Retorna 400 se 'tipo' estiver ausente ou inválido.
    Invalida: cache do proprietário e relatórios de marcas/gênero.
    """
    # cast explícito: request.data pode ser QueryDict ou dict —
    # o Pylance não consegue inferir .get() sem a anotação abaixo
    data: dict = request.data  # type: ignore[assignment]
    tipo_raw       = str(data.get('tipo', ''))
    tipo           = tipo_raw.lower().replace('ã', 'a').strip()
    ModeloConcreto = TIPO_MODELO.get(tipo)

    if ModeloConcreto is None:
        return Response(
            {"tipo": f"Tipo inválido. Valores aceitos: {', '.join(TIPO_MODELO.keys())}."},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = VeiculoSerializer(
        data=request.data,
        context={'modelo': ModeloConcreto}
    )
    if serializer.is_valid():
        obj: Veiculo = serializer.save()  # save() retorna o modelo salvo
        invalidar_cache_veiculo(obj.proprietario_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_Veiculo(request: Request, pk: int):
    """
    Atualiza campos da tabela base do veículo: placa, marca, modelo, ano.
    Campos específicos da subclasse (ex: cilindradas) não são alterados aqui —
    mudar de subclasse exigiria deletar e recriar o registro.
    Invalida: cache do proprietário e relatórios de marcas/gênero.
    """
    veiculo: Veiculo = get_object_or_404(Veiculo, pk=pk)
    serializer = VeiculoSerializer(veiculo, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        invalidar_cache_veiculo(veiculo.proprietario_id)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_Veiculo(request: Request, pk: int):
    """
    Remove o veículo e em cascata suas revisões.
    proprietario_id é salvo antes do delete para invalidar o cache correto.
    Invalida: cache do proprietário e relatórios de marcas/gênero.
    """
    veiculo: Veiculo = get_object_or_404(Veiculo, pk=pk)
    placa           = veiculo.placa
    proprietario_id = veiculo.proprietario_id   # salva antes do delete
    veiculo.delete()
    invalidar_cache_veiculo(proprietario_id)
    return Response(
        {"message": f"Veiculo {placa} deletado com sucesso."},
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
def veiculos_por_proprietario(request: Request):
    """
    Relatório: todos os veículos ordenados pelo nome do proprietário.
    Cache: chave fixa, TTL de 10 min.
    """
    cached = cache.get(KEY_VEICULOS_PROPRIETARIO_REL)
    if cached is not None:
        return Response(cached, status=status.HTTP_200_OK)

    veiculos = (
        Veiculo.objects
        .select_related('proprietario')
        .order_by('proprietario__nome', 'marca')
    )
    data = [
        {
            'proprietario': v.proprietario.nome,
            'genero':       v.proprietario.genero,
            'placa':        v.placa,
            'marca':        v.marca,
            'modelo':       v.modelo,
            'ano':          v.ano,
        }
        for v in veiculos
    ]
    cache.set(KEY_VEICULOS_PROPRIETARIO_REL, data, TTL_RELATORIO)
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def marcas_ranking(request: Request):
    """
    Relatório: ranking de marcas por quantidade de veículos.
    Cache: chave fixa, TTL de 10 min.
    """
    cached = cache.get(KEY_MARCAS_RANKING)
    if cached is not None:
        return Response(cached, status=status.HTTP_200_OK)

    resultado = (
        Veiculo.objects
        .values('marca')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    data = [{'marca': r['marca'], 'total': r['total']} for r in resultado]
    cache.set(KEY_MARCAS_RANKING, data, TTL_RELATORIO)
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def marcas_por_genero(request: Request):
    """
    Relatório: marcas segmentadas por gênero do proprietário.
    Cache: chave fixa, TTL de 10 min.
    """
    cached = cache.get(KEY_MARCAS_GENERO)
    if cached is not None:
        return Response(cached, status=status.HTTP_200_OK)

    resultado = (
        Veiculo.objects
        .select_related('proprietario')
        .values('marca', 'proprietario__genero')
        .annotate(total=Count('id'))
        .order_by('marca', 'proprietario__genero')
    )
    data = [
        {
            'marca':  r['marca'],
            'genero': 'Masculino' if r['proprietario__genero'] == 'M' else 'Feminino',
            'total':  r['total'],
        }
        for r in resultado
    ]
    cache.set(KEY_MARCAS_GENERO, data, TTL_RELATORIO)
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def genero_mais_veiculos(request: Request):
    """
    Relatório: gênero com mais veículos cadastrados.
    Cache: chave fixa, TTL de 10 min.
    """
    cached = cache.get(KEY_GENERO_VEICULOS)
    if cached is not None:
        return Response(cached, status=status.HTTP_200_OK)

    resultado = (
        Veiculo.objects
        .select_related('proprietario')
        .values('proprietario__genero')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    data = [
        {
            'genero': 'Masculino' if r['proprietario__genero'] == 'M' else 'Feminino',
            'total':  r['total'],
        }
        for r in resultado
    ]
    cache.set(KEY_GENERO_VEICULOS, data, TTL_RELATORIO)
    return Response(data, status=status.HTTP_200_OK)


# ================================================================
# REVISOES
# FK: Revisao.veiculo → Veiculo (tabela base)
# Campos: data_revisao, quilometragem, descricao, custo, responsavel
# ================================================================

@api_view(['GET'])
def get_Revisoes(request: Request):
    """
    Lista todas as revisões. Sem cache: volume alto, uso interno.
    """
    revisoes   = Revisao.objects.select_related('veiculo', 'veiculo__proprietario').all()
    serializer = RevisaoSerializer(revisoes, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_revisoes_veiculo(request: Request, pk: int):
    """
    Lista todas as revisões de um veículo específico.
    Cache: chave por ID do veículo, TTL de 5 min.
    """
    cache_key = KEY_REVISOES_DE_VEICULO.format(pk=pk)
    cached    = cache.get(cache_key)
    if cached is not None:
        return Response(cached, status=status.HTTP_200_OK)

    revisoes   = Revisao.objects.filter(veiculo_id=pk).select_related('veiculo')
    serializer = RevisaoSerializer(revisoes, many=True)
    cache.set(cache_key, serializer.data, TTL_DETALHE)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def creat_Revisao(request: Request):
    """
    Cria uma revisão para um veículo existente.
    Campos: veiculo, data_revisao, quilometragem, descricao, custo, responsavel.
    Invalida: cache de revisões do veículo e todos os relatórios de revisão.
    """
    serializer = RevisaoSerializer(data=request.data)
    if serializer.is_valid():
        obj: Revisao = serializer.save()  # save() retorna o modelo salvo
        invalidar_cache_revisao(obj.veiculo_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_Revisao(request: Request, pk: int):
    """
    Atualiza uma revisão existente (aceita campos parciais).
    Invalida: cache de revisões do veículo e todos os relatórios de revisão.
    """
    revisao: Revisao = get_object_or_404(Revisao, pk=pk)
    serializer = RevisaoSerializer(revisao, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        invalidar_cache_revisao(revisao.veiculo_id)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_Revisao(request: Request, pk: int):
    """
    Remove uma revisão pelo ID.
    veiculo_id é salvo antes do delete para invalidar o cache correto.
    Invalida: cache de revisões do veículo e todos os relatórios de revisão.
    """
    revisao: Revisao = get_object_or_404(Revisao, pk=pk)
    veiculo_id = revisao.veiculo_id   # salva antes do delete
    revisao.delete()
    invalidar_cache_revisao(veiculo_id)
    return Response(
        {"message": "Revisao deletada com sucesso."},
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
def revisoes_por_periodo(request: Request):
    """
    Relatório: revisões dentro de um intervalo de datas.
    Cache: chave dinâmica com início e fim, TTL de 10 min.
    Uso: /api/revisoes/relatorio/periodo/?inicio=2024-01-01&fim=2024-12-31
    """
    inicio = request.query_params.get('inicio')
    fim    = request.query_params.get('fim')

    if not inicio or not fim:
        return Response(
            {"error": "Informe os parametros 'inicio' e 'fim' no formato YYYY-MM-DD."},
            status=status.HTTP_400_BAD_REQUEST
        )

    cache_key = KEY_REVISOES_PERIODO.format(inicio=inicio, fim=fim)
    cached    = cache.get(cache_key)
    if cached is not None:
        return Response(cached, status=status.HTTP_200_OK)

    revisoes = (
        Revisao.objects
        .select_related('veiculo', 'veiculo__proprietario')
        .filter(data_revisao__range=[inicio, fim])
        .order_by('data_revisao')
    )
    serializer = RevisaoSerializer(revisoes, many=True)
    cache.set(cache_key, serializer.data, TTL_RELATORIO)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def marcas_mais_revisoes(request: Request):
    """
    Relatório: marcas com mais revisões registradas.
    Cache: chave fixa, TTL de 10 min.
    """
    cached = cache.get(KEY_MARCAS_REVISOES)
    if cached is not None:
        return Response(cached, status=status.HTTP_200_OK)

    resultado = (
        Revisao.objects
        .values('veiculo__marca')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    data = [{'marca': r['veiculo__marca'], 'total': r['total']} for r in resultado]
    cache.set(KEY_MARCAS_REVISOES, data, TTL_RELATORIO)
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def pessoas_mais_revisoes(request: Request):
    """
    Relatório: proprietários com mais revisões.
    Cache: chave fixa, TTL de 10 min.
    """
    cached = cache.get(KEY_PESSOAS_REVISOES)
    if cached is not None:
        return Response(cached, status=status.HTTP_200_OK)

    resultado = (
        Revisao.objects
        .values('veiculo__proprietario__nome', 'veiculo__proprietario__genero')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    data = [
        {
            'nome':   r['veiculo__proprietario__nome'],
            'genero': 'Masculino' if r['veiculo__proprietario__genero'] == 'M' else 'Feminino',
            'total':  r['total'],
        }
        for r in resultado
    ]
    cache.set(KEY_PESSOAS_REVISOES, data, TTL_RELATORIO)
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def media_tempo_revisoes(request: Request):
    """
    Relatório: média de dias entre revisões por proprietário (Raw SQL).
    Requer ao menos 2 revisões por usuário para entrar no resultado.
    Cache: chave fixa, TTL de 10 min.
    """
    cached = cache.get(KEY_MEDIA_TEMPO)
    if cached is not None:
        return Response(cached, status=status.HTTP_200_OK)

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    u.nome,
                    ROUND(
                        AVG(
                            r.data_revisao - LAG(r.data_revisao) OVER (
                                PARTITION BY u.id ORDER BY r.data_revisao
                            )
                        )::numeric, 1
                    ) AS media_dias
                FROM jose_gabriel.revisao r
                JOIN jose_gabriel.veiculo v ON v.id = r.veiculo_id
                JOIN jose_gabriel.usuario u ON u.id = v.proprietario_id
                GROUP BY u.id, u.nome
                HAVING COUNT(r.id) >= 2
                ORDER BY media_dias ASC NULLS LAST
            """)
            if cursor.description is None:
                return Response([], status=status.HTTP_200_OK)
            colunas = [col[0] for col in cursor.description]
            data    = [dict(zip(colunas, row)) for row in cursor.fetchall()]

        cache.set(KEY_MEDIA_TEMPO, data, TTL_RELATORIO)
        return Response(data, status=status.HTTP_200_OK)
    except Exception:
        return Response([], status=status.HTTP_200_OK)


@api_view(['GET'])
def proximas_revisoes(request: Request):
    """
    Relatório: previsão das próximas revisões por pessoa (Raw SQL com 3 CTEs).
    Lógica: última revisão + média do intervalo entre revisões anteriores.
    Cache: chave fixa, TTL de 10 min.
    """
    cached = cache.get(KEY_PROXIMAS_REVISOES)
    if cached is not None:
        return Response(cached, status=status.HTTP_200_OK)

    with connection.cursor() as cursor:
        cursor.execute("""
            WITH intervalos AS (
                SELECT
                    u.id          AS usuario_id,
                    u.nome,
                    r.data_revisao,
                    LAG(r.data_revisao) OVER (
                        PARTITION BY u.id ORDER BY r.data_revisao
                    ) AS revisao_anterior
                FROM jose_gabriel.revisao r
                JOIN jose_gabriel.veiculo v ON v.id = r.veiculo_id
                JOIN jose_gabriel.usuario u ON u.id = v.proprietario_id
            ),
            media_por_usuario AS (
                SELECT
                    usuario_id,
                    nome,
                    AVG(data_revisao - revisao_anterior) AS media_dias
                FROM intervalos
                WHERE revisao_anterior IS NOT NULL
                GROUP BY usuario_id, nome
            ),
            ultima_revisao AS (
                SELECT DISTINCT ON (v.proprietario_id)
                    v.proprietario_id AS usuario_id,
                    r.data_revisao    AS ultima
                FROM jose_gabriel.revisao r
                JOIN jose_gabriel.veiculo v ON v.id = r.veiculo_id
                ORDER BY v.proprietario_id, r.data_revisao DESC
            )
            SELECT
                m.nome,
                ROUND(m.media_dias::numeric, 0)  AS media_dias,
                u.ultima                         AS ultima_revisao,
                (u.ultima + (ROUND(m.media_dias::numeric, 0)
                    || ' days')::interval)::date AS proxima_revisao
            FROM media_por_usuario m
            JOIN ultima_revisao u ON u.usuario_id = m.usuario_id
            ORDER BY proxima_revisao ASC
        """)

        if cursor.description is None:
            return Response([], status=status.HTTP_200_OK)

        colunas = [col[0] for col in cursor.description]
        data    = [dict(zip(colunas, row)) for row in cursor.fetchall()]

    cache.set(KEY_PROXIMAS_REVISOES, data, TTL_RELATORIO)
    return Response(data, status=status.HTTP_200_OK)