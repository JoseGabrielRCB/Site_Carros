import os
import django
import random
from faker import Faker
from datetime import date, timedelta

# 1. Configurar o ambiente do Django
# Substitua 'seu_projeto.settings' pelo caminho correto do seu arquivo settings.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Back_End.settings')
django.setup()

from apps.core.models import Usuario, Veiculo, Carro, Moto, Triciclo, Caminhao, Revisao

fake = Faker('pt_BR')

def povoar_sistema(n_usuarios=50):
    print(f"Iniciando o povoamento com {n_usuarios} usuários...")

    tipos_combustivel = ['Gasolina', 'Álcool', 'Diesel', 'Flex', 'Elétrico']
    tipos_partida = ['Elétrica', 'Pedal', 'Remota']
    modelos_veiculos = {
        'Carro': [('Toyota', 'Corolla'), ('Honda', 'Civic'), ('VW', 'Gol'), ('Fiat', 'Uno')],
        'Moto': [('Honda', 'CB 500'), ('Yamaha', 'MT-07'), ('BMW', 'R1250')],
        'Caminhao': [('Volvo', 'FH 540'), ('Scania', 'R450'), ('Mercedes', 'Actros')],
        'Triciclo': [('Tuk-tuk', 'Standard'), ('Shineray', 'Carga')]
    }

    for _ in range(n_usuarios):
        # Criar Usuário
        genero_cod = random.choice(['M', 'F'])
        usuario = Usuario.objects.create(
            cpf=fake.unique.cpf(),
            nome=fake.name_male() if genero_cod == 'M' else fake.name_female(),
            genero=genero_cod,
            data_nascimento=fake.date_of_birth(minimum_age=18, maximum_age=80),
            endereco=fake.address().replace('\n', ', ')
        )

        # Criar de 1 a 2 veículos para cada usuário
        for _ in range(random.randint(1, 2)):
            tipo_v = random.choice(['Carro', 'Moto', 'Caminhao', 'Triciclo'])
            marca, modelo = random.choice(modelos_veiculos[tipo_v])
            
            dados_base = {
                'proprietario': usuario,
                'placa': fake.unique.license_plate(),
                'marca': marca,
                'modelo': modelo,
                'ano': random.randint(2010, 2024)
            }

            if tipo_v == 'Carro':
                veiculo = Carro.objects.create(
                    **dados_base,
                    ar_condicionado=random.choice([True, False]),
                    numero_portas=random.choice([2, 4]),
                    tipo_combustivel=random.choice(tipos_combustivel)
                )
            elif tipo_v == 'Moto':
                veiculo = Moto.objects.create(
                    **dados_base,
                    refrigeracao=random.choice(['Ar', 'Líquida']),
                    tipo_partida=random.choice(tipos_partida),
                    cilindradas=random.choice([125, 250, 600, 1000])
                )
            elif tipo_v == 'Caminhao':
                veiculo = Caminhao.objects.create(
                    **dados_base,
                    quantidade_eixos=random.randint(2, 6),
                    capacidade_toneladas=random.uniform(5, 40),
                    tipo_carroceria=random.choice(['Baú', 'Sider', 'Caçamba', 'Tanque'])
                )
            else: # Triciclo
                veiculo = Triciclo.objects.create(
                    **dados_base,
                    tipo_tracao=random.choice(['Traseira', 'Integral']),
                    capacidade_carga=random.uniform(200, 800)
                )

            # Criar 1 a 3 revisões para cada veículo
            for i in range(random.randint(1, 3)):
                Revisao.objects.create(
                    veiculo=veiculo,
                    data_revisao=date.today() - timedelta(days=random.randint(30, 730)),
                    quilometragem=random.uniform(5000, 100000),
                    descricao=f"Revisão periódica de {i+1} ano(s). Troca de óleo e filtros.",
                    custo=random.uniform(200, 2500),
                    responsavel=fake.name()
                )

    print("Povoamento concluído com sucesso!")

if __name__ == '__main__':
    povoar_sistema()