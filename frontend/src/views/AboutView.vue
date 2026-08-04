<template>
  <div class="about">
    <div class="glass-card">
      <h1>This is an about page</h1>
      <p>Welcome to our article platform. This is a simple about page to introduce our service.</p>
    </div>
  </div>
</template>

<style scoped>
.about {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  padding: 2rem 0;
}

.glass-card {
  width: 100%;
  max-width: 960px;
  text-align: center;
}

h1 {
  margin-bottom: 1.5rem;
  color: #18181B;
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-weight: 700;
  letter-spacing: -0.025em;
}

p {
  color: #71717A;
  font-size: 1.1rem;
  line-height: 1.65;
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
</style>
