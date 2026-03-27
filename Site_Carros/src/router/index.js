import { createRouter, createWebHistory } from 'vue-router'

import HomeView          from '../views/HomeView.vue'
import ProprietariosView from '../views/ProprietariosView.vue'
import VeiculosView      from '../views/VeiculosView.vue'
import RevisoesView      from '../views/RevisoesView.vue'
import FuncionariosView  from '../views/FuncionariosView.vue'
import RelatoriosView    from '../views/RelatoriosView.vue'  // NOVO

const routes = [
  { path: '/',              name: 'home',          component: HomeView },
  { path: '/proprietarios', name: 'proprietarios', component: ProprietariosView },
  { path: '/veiculos',      name: 'veiculos',      component: VeiculosView },
  { path: '/revisoes',      name: 'revisoes',      component: RevisoesView },
  { path: '/relatorios',    name: 'relatorios',    component: RelatoriosView },   // NOVO
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router