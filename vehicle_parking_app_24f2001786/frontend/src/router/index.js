import { createRouter, createWebHistory } from 'vue-router'
import Registration from '@/components/auth/Registration.vue'
import Login from '@/components/auth/Login.vue'
import Home from '@/components/Home.vue'
import AdminDashboard from '@/components/admin/AdminDashboard.vue'
import AdminSearch from '@/components/admin/AdminSearch.vue'
import AdminSummary from '@/components/admin/AdminSummary.vue'
import UserManagement from '@/components/admin/UserManagement.vue'
import UserDashboard from '@/components/user/UserDashboard.vue'
import UserSummary from '@/components/user/UserSummary.vue'
import PaymentPage from '@/components/user/PaymentPage.vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
  },
  {
    path: '/register',
    name: 'Registration',
    component: Registration,
    meta: { guestOnly: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { guestOnly: true }
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/search',
    name: 'AdminSearch',
    component: AdminSearch,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/users',
    name: 'UserManagement',
    component: UserManagement,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/summary',
    name: 'AdminSummary',
    component: AdminSummary,
    meta: { requiresAuth: true, requiresAdmin: true } 
  },
  {
    path: '/user/dashboard',
    name: 'UserDashboard',
    component: UserDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/user/summary',
    name: 'UserSummary',
    component: UserSummary,
    meta: { requiresAuth: true }
  },
    {
    path: '/payment/:reservationId',
    name: 'PaymentPage',
    component: PaymentPage,
    props: true,
    meta: { requiresAuth: true }
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// Enhanced Navigation Guard
router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore();
  const notification = useNotificationStore();

  // On the initial app load, wait for the session check to complete.
  if (!auth.authReady) {
    await auth.checkSession();
  }

  // Rule 1: Protect routes that require authentication
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    notification.showNotification({ type: 'warning', text: '⚠️ Please login to access this page.' });
    return next({ name: 'Login' });
  }

  // Rule 2: Protect admin-only routes
  if (to.meta.requiresAdmin && !auth.isAdmin) {
    notification.showNotification({ type: 'error', text: '🚫 You are not authorized to access this page.' });
    return next(from) ; // Redirect non-admins away
  }

  // Rule 3: Redirect authenticated users from guest-only pages
  if (to.meta.guestOnly && auth.isAuthenticated) {
    return next({ name: 'Home' });
  }

  // If no rules match, allow navigation
  next();
});

export default router
