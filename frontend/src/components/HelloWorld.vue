<script setup lang="ts">
defineProps<{
  msg: string
}>()
</script>

<template>
  <div class="greetings">
    <h1 class="green">{{ msg }}</h1>
    <h3>
      You’ve successfully created a project with
      <a href="https://vite.dev/" target="_blank" rel="noopener">Vite</a> +
      <a href="https://vuejs.org/" target="_blank" rel="noopener">Vue 3</a>. What's next?
    </h3>
  </div>
</template>

<style scoped>
h1 {
  font-weight: 700;
  font-size: clamp(2.25rem, 5vw, 3rem);
  position: relative;
  top: -10px;
  color: #18181B;
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  letter-spacing: -0.025em;
  line-height: 1.1;
}

h3 {
  font-size: 1.125rem;
  color: #71717A;
  line-height: 1.65;
}

a {
  color: #3B82F6;
  text-decoration: none;
  transition: color 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

a:hover {
  color: #2563EB;
  text-decoration: underline;
}

.greetings h1,
.greetings h3 {
  text-align: center;
}

@media (min-width: 1024px) {
  .greetings h1,
  .greetings h3 {
    text-align: left;
  }
}
</style>
