<template>
  <div class="home-container">
    <!-- Hero Section -->
    <section class="hero-section" :style="{ opacity: isVisible ? 1 : 0, transform: isVisible ? 'translateY(0)' : 'translateY(40px)' }">
      <div class="container">
        <div class="hero-grid">
          <div class="hero-content">
            <div class="badge">
              <span class="zap-icon">⚡</span>
              <span>Smart Parking Solutions</span>
            </div>
            
            <h1 class="hero-title">
              <span class="title-line-1">Find & Book</span>
              <span class="title-line-2">Parking Spots</span>
              <span class="title-line-3">Instantly</span>
            </h1>
            
            <p class="hero-description">
              Skip the hassle of searching for parking. Book secure spots in prime locations 
              with just a few taps. Smart, simple, and always available.
            </p>
            
            <div class="cta-buttons">
              <button class="btn-primary">
                <span>Start Booking</span>
                <span class="arrow">→</span>
              </button>
              <button class="btn-secondary">
                View Demo
              </button>
            </div>
            
            <div class="stats-row">
              <div class="stat-item" v-for="stat in stats.slice(0, 2)" :key="stat.label">
                <div class="stat-number">{{ stat.number }}</div>
                <div class="stat-label">{{ stat.label }}</div>
              </div>
            </div>
          </div>
          
          <div class="hero-visual">
            <div class="parking-card">
              <div class="card-inner">
                <div class="card-header">
                  <h3>Available Spots</h3>
                  <div class="status-dot" :class="{ active: true }"></div>
                </div>
                
                <div class="parking-list">
                  <div v-for="(location, index) in parkingLocations" :key="index" 
                       class="parking-item" :class="{ active: index === currentSlide }">
                    <div class="location-info">
                      <div class="location-icon">📍</div>
                      <div class="location-details">
                        <div class="location-name">{{ location.name }}</div>
                        <div class="location-spots">{{ location.spots }} spots available</div>
                      </div>
                    </div>
                    <div class="location-price">₹{{ location.price }}/hr</div>
                  </div>
                </div>
              </div>
              
              <!-- Floating elements -->
              <div class="floating-dot yellow"></div>
              <div class="floating-dot pink"></div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features-section">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">
            Why Choose <span class="gradient-text">ParkEase</span>
          </h2>
          <p class="section-description">
            Experience the future of parking with our innovative features designed for convenience and efficiency
          </p>
        </div>
        
        <div class="features-grid">
          <div v-for="(feature, index) in features" :key="index" class="feature-card">
            <div class="feature-icon">
              <span>{{ feature.icon }}</span>
            </div>
            <h3 class="feature-title">{{ feature.title }}</h3>
            <p class="feature-description">{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="stats-section">
      <div class="container">
        <div class="stats-grid">
          <div v-for="(stat, index) in stats" :key="index" class="stat-card">
            <div class="stat-number-large">{{ stat.number }}</div>
            <div class="stat-label-large">{{ stat.label }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Testimonials Section -->
    <section class="testimonials-section">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">What Our Users Say</h2>
          <p class="section-description">Join thousands of satisfied customers who trust ParkEase</p>
        </div>
        
        <div class="testimonials-grid">
          <div v-for="(testimonial, index) in testimonials" :key="index" class="testimonial-card">
            <div class="stars">
              <span v-for="star in testimonial.rating" :key="star" class="star">⭐</span>
            </div>
            <p class="testimonial-content">"{{ testimonial.content }}"</p>
            <div class="testimonial-author">
              <div class="author-avatar">
                {{ testimonial.name.charAt(0) }}
              </div>
              <div class="author-info">
                <div class="author-name">{{ testimonial.name }}</div>
                <div class="author-role">{{ testimonial.role }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
      <div class="container">
        <div class="cta-content">
          <h2 class="cta-title">
            Ready to Transform Your Parking Experience?
          </h2>
          <p class="cta-description">
            Join ParkEase today and never worry about finding parking again. 
            Start with a free account and experience the difference.
          </p>
          <div class="cta-buttons">
            <button class="btn-white">
              <span class="check-icon">✓</span>
              <span>Start Free Trial</span>
            </button>
            <button class="btn-outline">
              Contact Sales
            </button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

// Reactive data
const isVisible = ref(false)
const currentSlide = ref(0)
let slideInterval = null

// Static data
const stats = [
  { number: "10,000+", label: "Happy Users" },
  { number: "500+", label: "Parking Lots" },
  { number: "50,000+", label: "Bookings Made" },
  { number: "99.9%", label: "Uptime" }
]

const parkingLocations = [
  { name: 'Downtown Plaza', spots: 15, price: 45 },
  { name: 'City Mall', spots: 23, price: 35 },
  { name: 'Business District', spots: 8, price: 60 }
]

const features = [
  {
    icon: '📍',
    title: "Prime Locations",
    description: "Find parking spots in the best locations across the city"
  },
  {
    icon: '🕒',
    title: "24/7 Availability",
    description: "Book and release parking spots anytime, anywhere"
  },
  {
    icon: '🛡️',
    title: "Secure Parking",
    description: "Safe and monitored parking lots for your peace of mind"
  },
  {
    icon: '👥',
    title: "Easy Management",
    description: "Simple booking process with automatic spot allocation"
  }
]

const testimonials = [
  {
    name: "Sarah Johnson",
    role: "Daily Commuter",
    content: "This app has made my daily parking hassle-free. I can book spots in advance and never worry about finding parking downtown.",
    rating: 5
  },
  {
    name: "Mike Chen",
    role: "Business Owner",
    content: "As a parking lot owner, the admin dashboard gives me complete control over my spaces. Revenue tracking is excellent!",
    rating: 5
  },
  {
    name: "Emily Davis",
    role: "Weekend Shopper",
    content: "Love how I can easily find and book parking near shopping centers. The pricing is transparent and fair.",
    rating: 5
  }
]

// Lifecycle hooks
onMounted(() => {
  setTimeout(() => {
    isVisible.value = true
  }, 100)
  
  slideInterval = setInterval(() => {
    currentSlide.value = (currentSlide.value + 1) % parkingLocations.length
  }, 4000)
})

onUnmounted(() => {
  if (slideInterval) {
    clearInterval(slideInterval)
  }
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #e0f2fe 0%, #ffffff 50%, #f3e5f5 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  overflow-x: hidden;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

/* Hero Section */
.hero-section {
  padding: 80px 0 64px;
  transition: all 1s ease-out;
}

.hero-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
  align-items: center;
}

@media (max-width: 768px) {
  .hero-grid {
    grid-template-columns: 1fr;
    gap: 32px;
    text-align: center;
  }
}

.hero-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #e3f2fd;
  color: #1565c0;
  padding: 8px 16px;
  border-radius: 50px;
  font-size: 14px;
  font-weight: 500;
  width: fit-content;
}

.zap-icon {
  font-size: 16px;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  line-height: 1.1;
  margin: 0;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }
}

.title-line-1, .title-line-3 {
  background: linear-gradient(to right, #1a1a1a, #666666);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: block;
}

.title-line-2 {
  background: linear-gradient(to right, #2563eb, #7c3aed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: block;
}

.hero-description {
  font-size: 1.25rem;
  color: #666666;
  line-height: 1.6;
  margin: 0;
  max-width: 500px;
}

.cta-buttons {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.btn-primary {
  background: linear-gradient(to right, #2563eb, #7c3aed);
  color: white;
  border: none;
  padding: 16px 32px;
  border-radius: 16px;
  font-size: 1.125rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(37, 99, 235, 0.3);
}

.btn-secondary {
  background: transparent;
  color: #374151;
  border: 2px solid #e5e7eb;
  padding: 16px 32px;
  border-radius: 16px;
  font-size: 1.125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: #f9fafb;
}

.arrow {
  font-size: 1.2em;
}

.stats-row {
  display: flex;
  gap: 32px;
  padding-top: 16px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1a1a1a;
}

.stat-label {
  font-size: 0.875rem;
  color: #666666;
}

/* Hero Visual */
.hero-visual {
  position: relative;
}

.parking-card {
  background: linear-gradient(135deg, #60a5fa, #a855f7);
  border-radius: 24px;
  padding: 32px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.1);
  position: relative;
}

.card-inner {
  background: white;
  border-radius: 16px;
  padding: 24px;
}

.card-header {
  display: flex;
  justify-content: between;
  align-items: center;
  margin-bottom: 16px;
}

.card-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
  flex: 1;
}

.status-dot {
  width: 12px;
  height: 12px;
  background: #10b981;
  border-radius: 50%;
}

.status-dot.active {
  animation: pulse 2s infinite;
}

.parking-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.parking-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-radius: 12px;
  background: #f9fafb;
  transition: all 0.3s ease;
}

.parking-item.active {
  background: #dbeafe;
  border: 2px solid #93c5fd;
}

.location-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.location-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.location-name {
  font-weight: 500;
  color: #1a1a1a;
}

.location-spots {
  font-size: 0.875rem;
  color: #666666;
}

.location-price {
  font-size: 1.125rem;
  font-weight: 700;
  color: #10b981;
}

.floating-dot {
  position: absolute;
  border-radius: 50%;
}

.floating-dot.yellow {
  width: 32px;
  height: 32px;
  background: #fbbf24;
  top: -16px;
  right: -16px;
  animation: bounce 2s infinite;
}

.floating-dot.pink {
  width: 24px;
  height: 24px;
  background: #ec4899;
  bottom: -8px;
  left: -8px;
  animation: pulse 2s infinite;
}

/* Features Section */
.features-section {
  padding: 80px 0;
  background: white;
}

.section-header {
  text-align: center;
  margin-bottom: 64px;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 16px 0;
}

.gradient-text {
  background: linear-gradient(to right, #2563eb, #7c3aed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.section-description {
  font-size: 1.25rem;
  color: #666666;
  max-width: 600px;
  margin: 0 auto;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 32px;
}

.feature-card {
  background: linear-gradient(135deg, #f9fafb, white);
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 32px;
  text-align: center;
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border-color: #93c5fd;
}

.feature-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  font-size: 2rem;
  transition: transform 0.3s ease;
}

.feature-card:hover .feature-icon {
  transform: scale(1.1);
}

.feature-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 12px 0;
}

.feature-description {
  color: #666666;
  line-height: 1.6;
  margin: 0;
}

/* Stats Section */
.stats-section {
  padding: 80px 0;
  background: linear-gradient(to right, #2563eb, #7c3aed);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 32px;
  text-align: center;
}

.stat-card {
  color: white;
}

.stat-number-large {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 8px;
}

.stat-label-large {
  color: #bfdbfe;
  font-size: 1.125rem;
}

/* Testimonials Section */
.testimonials-section {
  padding: 80px 0;
  background: #f9fafb;
}

.testimonials-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 32px;
}

.testimonial-card {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  transition: box-shadow 0.3s ease;
}

.testimonial-card:hover {
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.stars {
  margin-bottom: 16px;
}

.star {
  font-size: 1.2rem;
  margin-right: 2px;
}

.testimonial-content {
  color: #666666;
  line-height: 1.6;
  margin: 0 0 24px 0;
  font-style: italic;
}

.testimonial-author {
  display: flex;
  align-items: center;
  gap: 12px;
}

.author-avatar {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
}

.author-name {
  font-weight: 600;
  color: #1a1a1a;
}

.author-role {
  font-size: 0.875rem;
  color: #666666;
}

/* CTA Section */
.cta-section {
  padding: 80px 0;
  background: linear-gradient(135deg, #1e3a8a, #581c87);
}

.cta-content {
  text-align: center;
  max-width: 800px;
  margin: 0 auto;
}

.cta-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  margin: 0 0 24px 0;
}

.cta-description {
  font-size: 1.25rem;
  color: #bfdbfe;
  line-height: 1.6;
  margin: 0 0 32px 0;
}

.btn-white {
  background: white;
  color: #1a1a1a;
  border: none;
  padding: 16px 32px;
  border-radius: 16px;
  font-size: 1.125rem;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-right: 16px;
  transition: all 0.2s ease;
}

.btn-white:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(255, 255, 255, 0.3);
}

.btn-outline {
  background: transparent;
  color: white;
  border: 2px solid white;
  padding: 16px 32px;
  border-radius: 16px;
  font-size: 1.125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-outline:hover {
  background: white;
  color: #1a1a1a;
}

.check-icon {
  font-size: 1.2em;
}

/* Animations */
@keyframes bounce {
  0%, 100% {
    transform: translateY(-25%);
  }
  50% {
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>