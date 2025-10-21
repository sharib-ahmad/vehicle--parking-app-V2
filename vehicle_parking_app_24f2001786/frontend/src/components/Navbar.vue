<template>
  <nav 
    class="navbar navbar-expand-lg navbar-light bg-light fixed-top shadow-sm"
    :class="{ 'navbar-scrolled': isScrolled }"
  >
    <div class="container">
      <!-- Brand/Logo -->
       <div class="navbar-logo">
      <router-link to="/" class="navbar-brand d-flex align-items-center">
        <img src="@/assets/logo.webp"  alt="Car" class="logo-img">
        <span class="fw-bold">ParkEase</span>
      </router-link>
      </div>

      <!-- Mobile Toggler -->
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>

      <!-- Navbar Links -->
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto align-items-center">
          <li class="nav-item">
            <router-link to="/" class="nav-link" @click="closeMobileMenu">Home</router-link>
          </li>

          <!-- Authenticated Links -->
          <template v-if="auth.isAuthenticated">
            <template v-if="auth.isAdmin">
            <li class="nav-item">
              <router-link :to="{ name: 'AdminDashboard' }" class="nav-link" @click="closeMobileMenu">Dashboard</router-link>
            </li>
            <li class="nav-item">
              <router-link :to="{ name: 'AdminSearch' }" class="nav-link" @click="closeMobileMenu">Search</router-link>
            </li>
            <li class="nav-item">
              <router-link :to="{ name: 'UserManagement' }" class="nav-link" @click="closeMobileMenu">User Management</router-link>
            </li>
            <li class="nav-item">
              <router-link :to="{ name: 'AdminSummary'}" class="nav-link" @click="closeMobileMenu">Summary</router-link>
              </li>
            </template>
            <template v-else>
              <li class="nav-item">
                <router-link :to="{ name: 'UserDashboard' }" class="nav-link" @click="closeMobileMenu">Dashboard</router-link>
              </li>
              <li class="nav-item">
                <router-link :to="{ name: 'UserSummary' }" class="nav-link" @click="closeMobileMenu">Summary</router-link>
              </li>
            </template>
            <li class="nav-item dropdown" ref="profileDropdown">
              <div 
                class="nav-link dropdown-toggle d-flex align-items-center" 
                id="navbarDropdown" 
                role="button" 
                @click.prevent="toggleProfileDropdown"
              >
                <div class="profile-avatar me-2">
                  <span>{{ getUserInitials }}</span>
                </div>
                {{ getUserName }}
              </div>
              <ul 
                class="dropdown-menu dropdown-menu-end" 
                :class="{ show: isProfileDropdownOpen }" 
                aria-labelledby="navbarDropdown"
              >
                <li>
                  <div class="dropdown-header px-3 pb-2">
                    <h6 class="fw-bold mb-0">{{ getUserName }}</h6>
                    <small class="text-muted">{{ getUserEmail }}</small>
                  </div>
                </li>
                <li><hr class="dropdown-divider"></li>
                <li><router-link class="dropdown-item" to="/profile" @click="closeDropdowns">My Profile</router-link></li>
                <li><hr class="dropdown-divider"></li>
                <li>
                  <button @click="handleLogout" class="dropdown-item logout-btn">
                    Logout
                  </button>
                </li>
              </ul>
            </li>
          </template>

          <!-- Unauthenticated Links -->
          <template v-else>
            <li class="nav-item">
              <router-link to="/login" class="nav-link" @click="closeMobileMenu">Login</router-link>
            </li>
            <li class="nav-item">
              <router-link to="/register" class="btn btn-primary ms-lg-2 rounded-pill" @click="closeMobileMenu">
                Get Started
              </router-link>
            </li>
          </template>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';


const auth = useAuthStore();
const router = useRouter();


// Reactive State
const isScrolled = ref(false);
const isProfileDropdownOpen = ref(false);
const profileDropdown = ref(null);

// User Data Helpers

const getUserName = computed(() => auth.user?.username || 'User');
const getUserEmail = computed(() => auth.user?.email || 'user@example.com');
const getUserInitials = computed(() => {
  const email = getUserEmail.value;
  if (!email) return 'U';
  return email.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
});

// This function closes the mobile menu when a link is clicked
const closeMobileMenu = () => {
    const toggler = document.querySelector('.navbar-toggler');
    const collapseElement = document.getElementById('navbarNav');
    if (collapseElement && collapseElement.classList.contains('show')) {
        toggler.click();
    }
}

// Dropdown Logic
const toggleProfileDropdown = () => {
  isProfileDropdownOpen.value = !isProfileDropdownOpen.value;
};

const closeDropdowns = () => {
  isProfileDropdownOpen.value = false;
  closeMobileMenu(); // Also close the mobile menu if open
};

const handleClickOutside = (event) => {
  if (profileDropdown.value && !profileDropdown.value.contains(event.target)) {
    isProfileDropdownOpen.value = false;
  }
};

watch(isProfileDropdownOpen, (isOpen) => {
  if (isOpen) {
    setTimeout(() => document.addEventListener('click', handleClickOutside), 0);
  } else {
    document.removeEventListener('click', handleClickOutside);
  }
});

// Logout
const handleLogout = async () => {
  closeDropdowns();
  await auth.logout();
  router.push({ name: 'Login' });
};

// Navbar Scroll Effect
const handleScroll = () => {
  isScrolled.value = window.scrollY > 10;
};

// Lifecycle Hooks
onMounted(() => {
  window.addEventListener('scroll', handleScroll);
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
/* Custom Navbar Styling */
.navbar {
  transition: background-color 0.3s ease, box-shadow 0.3s ease;
  padding-top: 1rem;
  padding-bottom: 1rem;
}

.navbar-scrolled {
  background-color: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(10px);
}

/* Logo container */
.navbar-logo {
  display: flex;
  align-items: center;
}

/* Image */
.logo-img {
  height: 60px;       
  width: auto;       
  margin-right: 10px; 
  background-color: #0d6efd;
  border-radius: 50%;
  padding: 5px;
  transition: transform 0.3s ease, opacity 0.3s ease;
}

/* Hover effect */
.logo-img:hover {
  transform: scale(1.1);  
  opacity: 0.9;           
}

/* Brand text */
.navbar-brand span {
  font-size: 1.25rem;   
  color: #0d6efd;       
  letter-spacing: 1px;  
  transition: color 0.3s ease;
}

/* Hover effect for text */
.navbar-brand:hover span {
  color: #0b5ed7; /* darker Bootstrap blue */
}


.nav-link {
  font-weight: 500;
  transition: color 0.2s ease;
}

.nav-link.router-link-exact-active {
  color: var(--bs-primary) !important;
  font-weight: 600;
}

/* Profile Avatar */
.profile-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: var(--bs-primary);
  color: white;
  display: flex;
  align-items:center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
}

/* Dropdown Menu */
.dropdown-menu {
  border-radius: 0.75rem;
  border: 1px solid #eee;
  box-shadow: 0 0.5rem 1.5rem rgba(0, 0, 0, 0.1);
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
}

.dropdown-item {
  padding: 0.6rem 1.25rem;
}

.dropdown-item:active {
  background-color: var(--bs-primary);
}

/* Logout Button */
.logout-btn {
  color: var(--bs-danger);
  width: 100%;
  text-align: left;
}

.logout-btn:hover {
  background-color: var(--bs-danger);
  color: white;
}

/* Register Button */
.btn-primary {
  padding: 0.6rem 1.25rem;
  font-weight: 500;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(var(--bs-primary-rgb), 0.3);
}
</style>

