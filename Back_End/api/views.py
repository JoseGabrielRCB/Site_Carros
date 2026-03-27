# api/views.py
from rest_framework.decorators import api_view
from rest_framework.request    import Request
from rest_framework.response   import Response
from rest_framework            import status
from django.shortcuts          import get_object_or_404
from django.db.models          import Count, Avg, F, ExpressionWrapper, FloatField, Q
from django.db                 import connection
from datetime                  import date
from apps.core.models          import Usuario, Veiculo, Revisao
from .serializers              import (
    UsuarioSerializer,
    UsuarioDetalheSerializer,
    VeiculoSerializer,
    RevisaoSerializer,
)


# ================================================================
# USUARIOS
# Endpoints para gerenciamento de proprietarios de veiculos.
# Todos os endpoints seguem o padrao REST:
#   GET    → leitura  (sem efeitos colaterais)
#   POST   → criacao  (retorna 201 Created)
#   PUT    → edicao   (partial=True aceita campos parciais)
#   DELETE → remocao  (cascata remove veiculos e revisoes)
# ================================================================

@api_view(['GET'])
def get_Usuarios(request: Request):
    """
    Lista usuarios com paginacao server-side (10 por pagina).

    Query params aceitos:
      page    — numero da pagina desejada (padrao: 1)
      search  — filtra por nome ou CPF (case-insensitive, parcial)

    Retorna envelope JSON:
      {
        "count":    <total de registros que batem o filtro>,
        "total_pages": <total de paginas>,
        "page":     <pagina atual>,
        "results":  [ ...usuarios... ]
      }

    Dessa forma o frontend sabe quantas paginas existem sem precisar
    carregar todos os registros de uma vez.
    """
    ITENS_POR_PAGINA = 10

    # --- Filtro de busca opcional ---
    search = request.query_params.get('search', '').strip()
    qs = Usuario.objects.all()
    if search:
        qs = qs.filter(
            Q(nome__icontains=search) | Q(cpf__icontains=search)
        )

    # --- Ordenacao pelo campo e direcao enviados pelo frontend ---
    # Campos permitidos para ordenacao (evita SQL injection via ORM)
    CAMPOS_VALIDOS = {
        'nome', 'cpf', 'genero', 'data_nascimento', 'endereco',
        # idade e total_veiculos sao campos calculados — tratados abaixo
    }
    ordering     = request.query_params.get('ordering', 'nome')
    desc         = ordering.startswith('-')
    campo        = ordering.lstrip('-')

    if campo == 'total_veiculos':
        # Campo calculado: anota contagem de veiculos para ordenar no banco
        qs = qs.annotate(_total_veiculos=Count('veiculos'))
        db_field = '_total_veiculos'
    elif campo == 'idade':
        # Idade inversa a data_nascimento: mais velho = data menor
        db_field = 'data_nascimento'
        desc = not desc   # inverte: "idade asc" = "nascimento desc"
    elif campo in CAMPOS_VALIDOS:
        db_field = campo
    else:
        db_field = 'nome'

    qs = qs.order_by(f"-{db_field}" if desc else db_field)

    # --- Paginacao ---
    try:
        page = max(1, int(request.query_params.get('page', 1)))
    except (ValueError, TypeError):
        page = 1

    total        = qs.count()
    total_pages  = max(1, -(-total // ITENS_POR_PAGINA))   # ceil sem math
    page         = min(page, total_pages)

    inicio  = (page - 1) * ITENS_POR_PAGINA
    fim     = inicio + ITENS_POR_PAGINA
    usuarios_pag = qs[inicio:fim]

    serializer = UsuarioSerializer(usuarios_pag, many=True)
    return Response({
        'count':       total,
        'total_pages': total_pages,
        'page':        page,
        'results':     serializer.data,
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_Usuario(request: Request, pk: int):
    """
    Retorna o detalhe de um usuario com veiculos e revisoes aninhados.
    prefetch_related('veiculos__revisoes') evita o problema N+1:
    em vez de 1 query por veiculo, traz tudo em 2 queries totais.
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
    Cria um novo usuario.
    Valida os dados via UsuarioSerializer antes de salvar.
    Retorna 400 com detalhes dos erros se a validacao falhar.
    """
    serializer = UsuarioSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_Usuario(request: Request, pk: int):
    """
    Atualiza um usuario existente.
    partial=True permite enviar apenas os campos alterados,
    sem precisar reenviar todos os campos obrigatorios.
    """
    usuario    = get_object_or_404(Usuario, pk=pk)
    serializer = UsuarioSerializer(usuario, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_Usuario(request: Request, pk: int):
    """
    Remove um usuario pelo ID.
    get_object_or_404 retorna 404 automaticamente se nao existir,
    evitando o erro 500 que ocorreria com .get() sem tratamento.
    A remocao em cascata (CASCADE na FK) apaga veiculos e revisoes.
    """
    usuario = get_object_or_404(Usuario, pk=pk)
    nome    = usuario.nome
    usuario.delete()
    return Response(
        {"message": f"Usuario {nome} deletado com sucesso."},
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
def usuarios_por_genero(request: Request):
    """
    Relatorio: pessoas separadas por genero com idade media.

    SQL equivalente:
        SELECT genero, COUNT(*) as total, AVG(idade) as idade_media
        FROM jose_gabriel.usuario
        GROUP BY genero

    A idade e calculada via anotacao no ORM subtraindo o ano de
    nascimento do ano atual — aproximacao suficiente para relatorio.
    """
    resultado = Usuario.objects.values('genero').annotate(
        total      = Count('id'),
        idade_media = Avg(
            ExpressionWrapper(
                date.today().year - F('data_nascimento__year'),
                output_field=FloatField()
            )
        )
    )

    # Substitui o codigo 'M'/'F' por label legivel para o frontend
    data = [
        {
            'genero':      'Masculino' if r['genero'] == 'M' else 'Feminino',
            'total':       r['total'],
            'idade_media': round(r['idade_media'] or 0, 1),
        }
        for r in resultado
    ]
    return Response(data, status=status.HTTP_200_OK)


# ================================================================
# VEICULOS
# Endpoints para gerenciamento de veiculos.
# select_related('proprietario') faz JOIN automatico evitando
# queries extras ao acessar veiculo.proprietario.nome.
# ================================================================

@api_view(['GET'])
def get_Veiculos(request: Request):
    """
    Lista todos os veiculos com dados do proprietario inclusos.
    select_related faz um SQL JOIN — evita query extra por veiculo.
    """
    veiculos   = Veiculo.objects.select_related('proprietario').all()
    serializer = VeiculoSerializer(veiculos, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_Veiculos_de_proprietario(request: Request,pk: int):
    "Lista todos os veiculos de um unicco proprietario"
    veiculos = Veiculo.objects.filter(proprietario_id=pk)
    serializer = VeiculoSerializer(veiculos,many=True)
    return Response(serializer.data)



@api_view(['POST'])
def creat_Veiculo(request: Request):
    """Cria um novo veiculo vinculado a um proprietario existente."""
    serializer = VeiculoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_Veiculo(request: Request, pk: int):
    """Atualiza campos do veiculo. Aceita atualizacao parcial."""
    veiculo    = get_object_or_404(Veiculo, pk=pk)
    serializer = VeiculoSerializer(veiculo, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_Veiculo(request: Request, pk: int):
    """
    Remove um veiculo pelo ID.
    A remocao em cascata apaga todas as revisoes vinculadas.
    """
    veiculo = get_object_or_404(Veiculo, pk=pk)
    placa   = veiculo.placa
    veiculo.delete()
    return Response(
        {"message": f"Veiculo {placa} deletado com sucesso."},
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
def veiculos_por_proprietario(request: Request):
    """
    Relatorio: todos os veiculos ordenados pelo nome do proprietario.

    SQL equivalente:
        SELECT u.nome, v.marca, v.modelo, v.placa, v.ano
        FROM jose_gabriel.veiculo v
        JOIN jose_gabriel.usuario u ON u.id = v.proprietario_id
        ORDER BY u.nome, v.marca
    """
    veiculos = (
        Veiculo.objects
        .select_related('proprietario')
        .order_by('proprietario__nome', 'marca')
    )

    # Monta dicionario manualmente para controlar exatamente
    # quais campos sao retornados ao frontend
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
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def marcas_ranking(request: Request):
    resultado = (
        Veiculo.objects
        .values('marca')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    data = [{'marca': r['marca'], 'total': r['total']} for r in resultado]
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def marcas_por_genero(request: Request):
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
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def genero_mais_veiculos(request: Request):
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
    return Response(data, status=status.HTTP_200_OK)


# ================================================================
# REVISOES
# ================================================================

@api_view(['GET'])
def get_Revisoes(request: Request):
    """Lista todas as revisoes com dados do veiculo e proprietario."""
    revisoes   = Revisao.objects.select_related('veiculo', 'veiculo__proprietario').all()
    serializer = RevisaoSerializer(revisoes, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_revisoes_veiculo(request: Request, pk: int):
    """Lista todas as revisoes de um unico veiculo."""
    revisoes   = Revisao.objects.filter(veiculo_id=pk).select_related('veiculo')
    serializer = RevisaoSerializer(revisoes, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def creat_Revisao(request: Request):
    """Lanca uma nova revisao para um veiculo existente."""
    serializer = RevisaoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_Revisao(request: Request, pk: int):
    """Atualiza uma revisao existente. Aceita atualizacao parcial."""
    revisao    = get_object_or_404(Revisao, pk=pk)
    serializer = RevisaoSerializer(revisao, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_Revisao(request: Request, pk: int):
    """Remove uma revisao pelo ID."""
    revisao = get_object_or_404(Revisao, pk=pk)
    revisao.delete()
    return Response(
        {"message": "Revisao deletada com sucesso."},
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
def revisoes_por_periodo(request: Request):
    """
    Relatorio: revisoes dentro de um intervalo de datas.
    Uso: /api/revisoes/relatorio/periodo/?inicio=2024-01-01&fim=2024-12-31
    """
    inicio = request.query_params.get('inicio')
    fim    = request.query_params.get('fim')

    if not inicio or not fim:
        return Response(
            {"error": "Informe os parametros 'inicio' e 'fim' no formato YYYY-MM-DD."},
            status=status.HTTP_400_BAD_REQUEST
        )

    revisoes = (
        Revisao.objects
        .select_related('veiculo', 'veiculo__proprietario')
        .filter(data_revisao__range=[inicio, fim])
        .order_by('data_revisao')
    )
    serializer = RevisaoSerializer(revisoes, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def marcas_mais_revisoes(request: Request):
    resultado = (
        Revisao.objects
        .values('veiculo__marca')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    data = [{'marca': r['veiculo__marca'], 'total': r['total']} for r in resultado]
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def pessoas_mais_revisoes(request: Request):
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
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def media_tempo_revisoes(request: Request):
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
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response([], status=status.HTTP_200_OK)


@api_view(['GET'])
def proximas_revisoes(request: Request):
    """
    Relatorio: previsao das proximas revisoes por pessoa.
    Usa Raw SQL com 3 CTEs encadeadas.
    """
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

    return Response(data, status=status.HTTP_200_OK)