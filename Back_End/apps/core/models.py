from django.db import models


class Usuario(models.Model):
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
    ]
    
    cpf = models.CharField(max_length=14, unique=True)
    nome = models.CharField(max_length=255)
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES)
    data_nascimento = models.DateField()
    endereco = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        # Força a criação da tabela dentro do schema com seu nome
        db_table = '"jose_gabriel"."usuario"'

    def __str__(self):
        return self.nome


class Veiculo(models.Model):
    # O related_name='veiculos' permite fazer buscas inversas facilmente
    # Ex: usuario.veiculos.all()
    proprietario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='veiculos')
    placa = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    ano = models.IntegerField()

    class Meta:
        db_table = '"jose_gabriel"."veiculo"'

    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.placa})"


# --- ESPECIALIZAÇÕES DE VEÍCULOS ---

class Carro(Veiculo):
    ar_condicionado = models.BooleanField(default=False)
    numero_portas = models.IntegerField()
    tipo_combustivel = models.CharField(max_length=50)

    class Meta:
        db_table = '"jose_gabriel"."carro"'


class Moto(Veiculo):
    refrigeracao = models.CharField(max_length=50)
    tipo_partida = models.CharField(max_length=50)
    cilindradas = models.IntegerField()

    class Meta:
        db_table = '"jose_gabriel"."moto"'


class Triciclo(Veiculo):
    tipo_tracao = models.CharField(max_length=50)
    capacidade_carga = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = '"jose_gabriel"."triciclo"'


class Caminhao(Veiculo):
    quantidade_eixos = models.IntegerField()
    capacidade_toneladas = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_carroceria = models.CharField(max_length=100)

    class Meta:
        db_table = '"jose_gabriel"."caminhao"'




# --- TABELA DE REVISÕES ---

class Revisao(models.Model):
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE, related_name='revisoes')
    #funcionario = models.ForeignKey(Funcionario,on_delete=models.PROTECT,related_name='responsavel')
    data_revisao = models.DateField()
    quilometragem = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.TextField()
    custo = models.DecimalField(max_digits=10, decimal_places=2)
    responsavel = models.CharField(max_length=100)

    class Meta:
        db_table = '"jose_gabriel"."revisao"'

    def __str__(self):
        return f"Revisão {self.veiculo.placa} - {self.data_revisao}"

