import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';

import LoginForm from './components/LoginForm.vue';
import KitPage from './components/KitPage.vue';
import RegistrationForm from './components/RegistrationForm.vue';
import AdminPanel from './components/AdminPanel.vue';
import ResearchPage from './components/ResearchPage.vue';


const routes: RouteRecordRaw[] = [

  {
    path: '/kits/:id',
    name: 'kit',
    component: KitPage
  },
  {
    path: '/researches/:id',
    name: 'research',
    component: ResearchPage
  },
  { 
    path: '/login', 
    component: LoginForm 
  },
  { 
    path: '/register', 
    component: RegistrationForm 
  },
  {
    path: '/panel',
    component: AdminPanel
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
