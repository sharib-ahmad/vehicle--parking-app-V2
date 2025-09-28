<template>
  <div id="app" class="d-flex flex-column min-vh-100">
    <Navbar />
    <FlashMessage />
    <main class="flex-grow-1 pt-5">
      <router-view />
    </main>
    <Footer />
  </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue';
import Footer from './components/Footer.vue';
import FlashMessage from './components/common/FlashMessage.vue';
</script>

