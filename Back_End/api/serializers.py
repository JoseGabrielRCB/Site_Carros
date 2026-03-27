# api/serializers.py
from rest_framework import serializers
from datetime import date
from apps.core.models import Usuario, Veiculo, Carro, Moto, Triciclo, Caminhao, Revisao


# ================================================================
# USUARIO
# Serializer principal do model Usuario.
# Além dos campos do banco, calcula 'idade' e 'genero_display'
# dinamicamente via SerializerMethodField (não existem no banco).
# ================================================================

class UsuarioSerializer(serializers.ModelSerializer):

    # Campos calculados — somente leitura, não são salvos no banco
    idade          = serializers.SerializerMethodField()
    genero_display = serializers.SerializerMethodField()
    total_veiculos = serializers.SerializerMethodField()

    class Meta:
        model  = Usuario
        fields = [
            'id',
            'cpf',
            'nome',
            'genero',
            'genero_display',   # ex: "Masculino" em vez de "M"
            'data_nascimento',
            'endereco',
            'idade',            # calculada a partir de data_nascimento
            'total_veiculos',   # conta via related_name='veiculos'
        ]

    def get_idade(self, obj):
        """
        Calcula a idade exata em anos considerando
        se o aniversário já ocorreu no ano atual.
        """
        hoje = date.today()
        return hoje.year - obj.data_nascimento.year - (
            (hoje.month, hoje.day) < (obj.data_nascimento.month, obj.data_nascimento.day)
        )

    def get_genero_display(self, obj):
        """Converte o código 'M'/'F' para texto legível."""
        return 'Masculino' if obj.genero == 'M' else 'Feminino'

    def get_total_veiculos(self, obj):
        """
        Conta os veículos do usuário usando o related_name='veiculos'
        definido na FK de Veiculo → Usuario.
        """
        return obj.veiculos.count()


# ================================================================
# VEICULO (base)
# Usado em listagens gerais onde não importa o tipo específico.
# O campo 'tipo' identifica a especialização (Carro, Moto etc.)
# verificando se o objeto possui o atributo da tabela filha.
# ================================================================

class VeiculoSerializer(serializers.ModelSerializer):

    # Campos do proprietário — lidos via FK, não editáveis aqui
    proprietario_nome   = serializers.CharField(
        source='proprietario.nome',
        read_only=True
    )
    proprietario_genero = serializers.CharField(
        source='proprietario.genero',
        read_only=True
    )

    # Tipo identificado dinamicamente pela herança multi-tabela
    tipo = serializers.SerializerMethodField()

    class Meta:
        model  = Veiculo
        fields = [
            'id',
            'proprietario',         # ID do proprietário (gravável)
            'proprietario_nome',    # nome do proprietário (leitura)
            'proprietario_genero',  # gênero do proprietário (leitura)
            'placa',
            'marca',
            'modelo',
            'ano',
            'tipo',                 # 'Carro', 'Moto', 'Triciclo' ou 'Caminhão'
        ]

    def get_tipo(self, obj):
        """
        Identifica o tipo do veículo verificando se o objeto possui
        o atributo da tabela filha gerado pela herança multi-tabela
        do Django (OneToOneField reverso automático).
        """
        if hasattr(obj, 'carro'):    return 'Carro'
        if hasattr(obj, 'moto'):     return 'Moto'
        if hasattr(obj, 'triciclo'): return 'Triciclo'
        if hasattr(obj, 'caminhao'): return 'Caminhão'
        return 'Veículo'


# ================================================================
# ESPECIALIZAÇÕES DE VEÍCULO
# Cada serializer inclui os campos base de Veiculo (herdados)
# mais os campos específicos do tipo.
# Todos expõem proprietario_nome como campo de leitura para
# facilitar a exibição no frontend sem precisar de join manual.
# ================================================================

class CarroSerializer(serializers.ModelSerializer):

    proprietario_nome = serializers.CharField(
        source='proprietario.nome',
        read_only=True
    )

    class Meta:
        model  = Carro
        fields = [
            'id',
            'proprietario',
            'proprietario_nome',
            'placa',
            'marca',
            'modelo',
            'ano',
            # Campos específicos de Carro
            'ar_condicionado',   # BooleanField
            'numero_portas',     # IntegerField
            'tipo_combustivel',  # ex: 'Flex', 'Gasolina', 'Diesel'
        ]


class MotoSerializer(serializers.ModelSerializer):

    proprietario_nome = serializers.CharField(
        source='proprietario.nome',
        read_only=True
    )

    class Meta:
        model  = Moto
        fields = [
            'id',
            'proprietario',
            'proprietario_nome',
            'placa',
            'marca',
            'modelo',
            'ano',
            # Campos específicos de Moto
            'refrigeracao',  # ex: 'Ar', 'Água', 'Óleo'
            'tipo_partida',  # ex: 'Elétrica', 'Pedal', 'Ambos'
            'cilindradas',   # ex: 150, 300, 600
        ]


class TricicloSerializer(serializers.ModelSerializer):

    proprietario_nome = serializers.CharField(
        source='proprietario.nome',
        read_only=True
    )

    class Meta:
        model  = Triciclo
        fields = [
            'id',
            'proprietario',
            'proprietario_nome',
            'placa',
            'marca',
            'modelo',
            'ano',
            # Campos específicos de Triciclo
            'tipo_tracao',      # ex: 'Dianteira', 'Traseira'
            'capacidade_carga', # em kg — DecimalField
        ]


class CaminhaoSerializer(serializers.ModelSerializer):

    proprietario_nome = serializers.CharField(
        source='proprietario.nome',
        read_only=True
    )

    class Meta:
        model  = Caminhao
        fields = [
            'id',
            'proprietario',
            'proprietario_nome',
            'placa',
            'marca',
            'modelo',
            'ano',
            # Campos específicos de Caminhao
            'quantidade_eixos',      # ex: 2, 3, 4
            'capacidade_toneladas',  # ex: 5.0, 10.5
            'tipo_carroceria',       # ex: 'Baú', 'Graneleiro', 'Tanque'
        ]


# ================================================================
# REVISAO
# Serializer principal de revisão.
# Inclui campos extras de leitura para exibir informações do
# veículo e do proprietário sem precisar de requisições adicionais
# no frontend (evita múltiplas chamadas à API).
# ================================================================

class RevisaoSerializer(serializers.ModelSerializer):

    # Dados do veículo — leitura via FK aninhada
    veiculo_placa  = serializers.CharField(source='veiculo.placa',  read_only=True)
    veiculo_marca  = serializers.CharField(source='veiculo.marca',  read_only=True)
    veiculo_modelo = serializers.CharField(source='veiculo.modelo', read_only=True)

    # Dado do proprietário — leitura via FK duplamente aninhada
    proprietario_nome = serializers.CharField(
        source='veiculo.proprietario.nome',
        read_only=True
    )

    class Meta:
        model  = Revisao
        fields = [
            'id',
            'veiculo',           # ID do veículo (gravável)
            'veiculo_placa',     # placa do veículo (leitura)
            'veiculo_marca',     # marca do veículo (leitura)
            'veiculo_modelo',    # modelo do veículo (leitura)
            'proprietario_nome', # nome do dono (leitura)
            'data_revisao',      # formato: YYYY-MM-DD
            'quilometragem',     # KM no momento da revisão
            'descricao',         # serviços realizados
            'custo',             # valor total em R$
            'responsavel',       # oficina ou mecânico
        ]


# ================================================================
# SERIALIZERS ANINHADOS
# Usados na tela de detalhe do usuário (GET /api/users/<pk>/).
# Retornam o usuário com todos os veículos e, dentro de cada
# veículo, todas as revisões — tudo em uma única requisição.
#
# Hierarquia:
#   UsuarioDetalheSerializer
#     └── VeiculoComRevisoesSerializer  (lista de veículos)
#           └── RevisaoResumidaSerializer  (lista de revisões)
# ================================================================

class RevisaoResumidaSerializer(serializers.ModelSerializer):
    """
    Versão simplificada de RevisaoSerializer.
    Usada dentro de VeiculoComRevisoesSerializer para evitar
    dados redundantes (marca e modelo já estão no veículo pai).
    """

    veiculo_placa = serializers.CharField(
        source='veiculo.placa',
        read_only=True
    )

    class Meta:
        model  = Revisao
        fields = [
            'id',
            'veiculo_placa',
            'data_revisao',
            'custo',
            'responsavel',
        ]


class VeiculoComRevisoesSerializer(serializers.ModelSerializer):
    """
    Serializer de veículo com revisões aninhadas.
    O campo 'revisoes' usa many=True e read_only=True para
    listar automaticamente via related_name='revisoes' da FK
    de Revisao → Veiculo.
    """

    # Lista de revisões aninhadas — lidas via related_name
    revisoes = RevisaoResumidaSerializer(many=True, read_only=True)

    # Tipo identificado pela herança multi-tabela
    tipo = serializers.SerializerMethodField()

    class Meta:
        model  = Veiculo
        fields = ['id', 'placa', 'marca', 'modelo', 'ano', 'tipo', 'revisoes']

    def get_tipo(self, obj):
        if hasattr(obj, 'carro'):    return 'Carro'
        if hasattr(obj, 'moto'):     return 'Moto'
        if hasattr(obj, 'triciclo'): return 'Triciclo'
        if hasattr(obj, 'caminhao'): return 'Caminhão'
        return 'Veículo'


class UsuarioDetalheSerializer(serializers.ModelSerializer):
    """
    Serializer completo de usuário com veículos e revisões aninhados.
    Usado exclusivamente na view de detalhe: GET /api/users/<pk>/

    Retorna toda a árvore de dados em uma única requisição,
    eliminando o problema N+1 quando combinado com prefetch_related
    na view:
        Usuario.objects.prefetch_related('veiculos__revisoes')
    """

    idade          = serializers.SerializerMethodField()
    genero_display = serializers.SerializerMethodField()

    # Lista de veículos com revisões aninhadas
    veiculos = VeiculoComRevisoesSerializer(many=True, read_only=True)

    class Meta:
        model  = Usuario
        fields = [
            'id',
            'cpf',
            'nome',
            'genero',
            'genero_display',
            'data_nascimento',
            'endereco',
            'idade',
            'veiculos',  # inclui revisoes aninhadas dentro de cada veículo
        ]

    def get_idade(self, obj):
        hoje = date.today()
        return hoje.year - obj.data_nascimento.year - (
            (hoje.month, hoje.day) < (obj.data_nascimento.month, obj.data_nascimento.day)
        )

    def get_genero_display(self, obj):
        return 'Masculino' if obj.genero == 'M' else 'Feminino'