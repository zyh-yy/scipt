import Vue from 'vue';
import VueRouter from 'vue-router';

Vue.use(VueRouter);

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/scripts',
    name: 'Scripts',
    component: () => import('../views/Scripts.vue')
  },
  {
    path: '/scripts/add',
    name: 'ScriptAdd',
    component: () => import('../views/ScriptForm.vue')
  },
  {
    path: '/scripts/:id',
    name: 'ScriptDetail',
    component: () => import('../views/ScriptDetail.vue')
  },
  {
    path: '/scripts/:id/edit',
    name: 'ScriptEdit',
    component: () => import('../views/ScriptForm.vue')
  },
  {
    path: '/chains',
    name: 'Chains',
    component: () => import('../views/Chains.vue')
  },
  {
    path: '/chains/add',
    name: 'ChainAdd',
    component: () => import('../views/ChainForm.vue')
  },
  {
    path: '/chains/:id',
    name: 'ChainDetail',
    component: () => import('../views/ChainDetail.vue')
  },
  {
    path: '/chains/:id/edit',
    name: 'ChainEdit',
    component: () => import('../views/ChainForm.vue')
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/History.vue')
  },
  {
    path: '/history/:id',
    name: 'HistoryDetail',
    component: () => import('../views/HistoryDetail.vue')
  },
  {
    path: '/alerts',
    name: 'Alerts',
    component: () => import('../views/Alerts.vue')
  },
  {
    path: '/alert/history',
    name: 'AlertHistory',
    component: () => import('../views/AlertHistory.vue')
  },
  {
    path: '/scheduled-tasks',
    name: 'ScheduledTasks',
    component: () => import('../views/ScheduledTasks.vue')
  },
  {
    path: '*',
    name: '404',
    component: () => import('../views/NotFound.vue')
  }
];

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
});

export default router;
