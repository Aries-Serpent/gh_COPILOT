<template>
  <ul class="correction-log">
    <li v-for="log in logs" :key="log.timestamp">
      <span class="timestamp">{{ log.timestamp }}</span>
      <span class="entity">{{ log.entity }}</span>
      <span class="resolution">{{ log.resolution }}</span>
    </li>
  </ul>
</template>

<script>
export default {
  name: 'CorrectionLog',
  props: {
    logs: {
      type: Array,
      default: () => [],
    },
  },
};
</script>

<style scoped>
.correction-log {
  list-style: none;
  padding: 0;
}
.correction-log li {
  display: flex;
  gap: 0.5rem;
}
.timestamp {
  font-weight: bold;
}
</style>
