<template>
  <footer class="bg-dark text-light py-3 mt-2 shadow-lg">
    <div class="container text-center">
      <p class="mb-1">&copy; {{ new Date().getFullYear() }} Vehicle Parking App</p>
      <div>
        <a href="https://github.com" target="_blank" class="text-light me-3">
          <i class="bi bi-github"></i>
        </a>
        <a href="https://linkedin.com" target="_blank" class="text-light">
          <i class="bi bi-linkedin"></i>
        </a>
      </div>
    </div>
  </footer>
</template>

<style scoped>
footer a {
  transition: transform 0.2s ease;
}
footer a:hover {
  transform: scale(1.2);
  color: #0d6efd !important; /* bootstrap primary blue */
}
</style>
