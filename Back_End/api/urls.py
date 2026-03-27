# api/urls.py
from django.urls import path
from .views import (
    get_Usuarios, get_Usuario, creat_Usuario, update_Usuario, delete_Usuario,
    usuarios_por_genero,
    get_Veiculos, creat_Veiculo, update_Veiculo, delete_Veiculo,
    veiculos_por_proprietario, marcas_ranking, marcas_por_genero, genero_mais_veiculos,
    get_Revisoes, creat_Revisao, update_Revisao, delete_Revisao,
    revisoes_por_periodo, marcas_mais_revisoes, pessoas_mais_revisoes,
    media_tempo_revisoes, proximas_revisoes,get_revisoes_veiculo,get_Veiculos_de_proprietario
)

urlpatterns = [
    # Usuarios
    path('users/',                       get_Usuarios,             name='get_usuarios'),
    path('users/<int:pk>/',              get_Usuario,              name='get_usuario'),
    path('users/creat/',                 creat_Usuario,            name='creat_usuario'),
    path('users/<int:pk>/update/',       update_Usuario,           name='update_usuario'),
    path('users/<int:pk>/delete/',       delete_Usuario,           name='delete_usuario'),
    path('users/relatorio/genero/',      usuarios_por_genero,      name='usuarios_por_genero'),

    # Veiculos
    path('veiculos/',                          get_Veiculos,             name='get_veiculos'), 
    path('veiculos/creat/',                    creat_Veiculo,            name='creat_veiculo'),
    path('veiculos/<int:pk>/update/',          update_Veiculo,           name='update_veiculo'),
    path('veiculos/<int:pk>/delete/',          delete_Veiculo,           name='delete_veiculo'),
    path('veiculos/relatorio/proprietario/',   veiculos_por_proprietario, name='veiculos_proprietario'),
    path('veiculos/relatorio/marcas/',         marcas_ranking,           name='marcas_ranking'),
    path('veiculos/relatorio/marcas_genero/',  marcas_por_genero,        name='marcas_por_genero'),
    path('veiculos/relatorio/genero/',         genero_mais_veiculos,     name='genero_mais_veiculos'),
    path('veiculos/proprietario/<int:pk>/', get_Veiculos_de_proprietario, name = "veiculos_de_proprietario"),

    # Revisoes
    path('revisoes/',                          get_Revisoes,             name='get_revisoes'),
    path('revisoes/creat/',                    creat_Revisao,            name='creat_revisao'),
    path('revisoes/<int:pk>/update/',          update_Revisao,           name='update_revisao'),
    path('revisoes/<int:pk>/delete/',          delete_Revisao,           name='delete_revisao'),
    path('revisoes/relatorio/periodo/',        revisoes_por_periodo,     name='revisoes_periodo'),
    path('revisoes/relatorio/marcas/',         marcas_mais_revisoes,     name='marcas_mais_revisoes'),
    path('revisoes/relatorio/pessoas/',        pessoas_mais_revisoes,    name='pessoas_mais_revisoes'),
    path('revisoes/relatorio/media_tempo/',    media_tempo_revisoes,     name='media_tempo_revisoes'),
    path('revisoes/relatorio/proximas/',       proximas_revisoes,        name='proximas_revisoes'),

    path('revisoes/veiculo/<int:pk>/', get_revisoes_veiculo, name='get_revisoes_veiculo'),
]