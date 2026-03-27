<template>
  <div class="dashboard-layout">

    <aside class="sidebar" :class="{ 'sidebar-fechada': sidebarFechada }">

      <div class="sidebar-logo">
        <span class="sidebar-logo-icone">🚗</span>
        <span class="sidebar-logo-texto" v-show="!sidebarFechada">Revisões</span>
      </div>

      <button class="sidebar-toggle" @click="sidebarFechada = !sidebarFechada" title="Recolher menu">
        {{ sidebarFechada ? '→' : '←' }}
      </button>

      <nav class="sidebar-nav">

        <router-link to="/" class="sidebar-item" active-class="sidebar-item-ativo" exact>
          <span class="sidebar-icone">🏠</span>
          <span class="sidebar-texto" v-show="!sidebarFechada">Home</span>
        </router-link>

        <router-link to="/proprietarios" class="sidebar-item" active-class="sidebar-item-ativo">
          <span class="sidebar-icone">👤</span>
          <span class="sidebar-texto" v-show="!sidebarFechada">Proprietários</span>
        </router-link>

        <router-link to="/veiculos" class="sidebar-item" active-class="sidebar-item-ativo">
          <span class="sidebar-icone">🚗</span>
          <span class="sidebar-texto" v-show="!sidebarFechada">Veículos</span>
        </router-link>

        <router-link to="/revisoes" class="sidebar-item" active-class="sidebar-item-ativo">
          <span class="sidebar-icone">🔧</span>
          <span class="sidebar-texto" v-show="!sidebarFechada">Revisões</span>
        </router-link>

        <!-- NOVO — Relatórios -->
        <router-link to="/relatorios" class="sidebar-item" active-class="sidebar-item-ativo">
          <span class="sidebar-icone">📊</span>
          <span class="sidebar-texto" v-show="!sidebarFechada">Relatórios</span>
        </router-link>

      </nav>
    </aside>

    <div class="dashboard-main">
      <header class="topbar">
        <h2 class="topbar-titulo">{{ tituloAtual }}</h2>
        <div class="topbar-usuario">
          <span class="topbar-avatar">👤</span>
          <span class="topbar-nome">Admin</span>
        </div>
      </header>

      <main class="dashboard-conteudo">
        <router-view />
      </main>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute }      from 'vue-router'

const route          = useRoute()
const sidebarFechada = ref(false)

const titulos = {
  home:          'Início',
  proprietarios: 'Proprietários',
  veiculos:      'Veículos',
  revisoes:      'Revisões',
  relatorios:    'Relatórios',      // NOVO
  funcionarios:  'Funcionários',
}

const tituloAtual = computed(() => titulos[route.name] ?? 'Dashboard')
</script>

<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Segoe UI', sans-serif;
  background: #f0f2f5;
  color: #1a1a2e;
}

.dashboard-layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 220px;
  min-height: 100vh;
  background: #1a1a2e;
  color: #fff;
  display: flex;
  flex-direction: column;
  transition: width 0.25s ease;
  flex-shrink: 0;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow: hidden;
}
.sidebar-fechada { width: 64px; }

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 16px 12px;
  font-size: 1.1rem;
  font-weight: 700;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  white-space: nowrap;
}
.sidebar-logo-icone { font-size: 1.4rem; }

.sidebar-toggle {
  background: none;
  border: none;
  color: rgba(255,255,255,0.5);
  cursor: pointer;
  font-size: 1rem;
  padding: 8px 16px;
  text-align: right;
  transition: color 0.2s;
}
.sidebar-toggle:hover { color: #fff; }

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px 8px;
  flex: 1;
}

.sidebar-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  color: rgba(255,255,255,0.75);
  text-decoration: none;
  font-size: 0.9rem;
  transition: background 0.2s, color 0.2s;
  white-space: nowrap;
}
.sidebar-item:hover { background: rgba(255,255,255,0.1); color: #fff; }
.sidebar-item-ativo { background: #2563eb; color: #fff; font-weight: 600; }
.sidebar-icone { font-size: 1.1rem; flex-shrink: 0; }

.dashboard-main { flex: 1; display: flex; flex-direction: column; min-width: 0; }

.topbar {
  height: 60px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  position: sticky;
  top: 0;
  z-index: 10;
}
.topbar-titulo { font-size: 1.1rem; font-weight: 600; color: #1a1a2e; }
.topbar-usuario { display: flex; align-items: center; gap: 8px; font-size: 0.875rem; color: #555; }
.topbar-avatar { font-size: 1.2rem; }

.dashboard-conteudo { padding: 28px; flex: 1; }

/* Paginacao global */
.paginacao { display:flex; align-items:center; justify-content:center; gap:16px; margin-top:20px; padding:12px 0; }
.paginacao-info { font-size:.9rem; color:#666; }
.btn-paginacao { padding:6px 16px; border:1px solid #ccc; border-radius:6px; background:#fff; color:#333; cursor:pointer; font-size:.875rem; transition:background .2s,opacity .2s; }
.btn-paginacao:hover:not(:disabled) { background:#2563eb; color:#fff; border-color:#2563eb; }
.btn-paginacao:disabled { opacity:.4; cursor:not-allowed; }
.btn-paginacao-ativo { background:#2563eb !important; color:#fff !important; border-color:#2563eb !important; font-weight:600; }
</style>