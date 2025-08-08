<template>
  <div>
    <ul class="correction-log">
      <li v-for="log in pagedLogs" :key="log.timestamp">
        <span class="timestamp">{{ log.timestamp }}</span>
        <span class="entity">{{ log.entity }}</span>
        <span class="resolution">{{ log.resolution }}</span>
      </li>
    </ul>
    <div class="pagination">
      <button @click="prevPage" :disabled="page === 1">Prev</button>
      <button @click="nextPage" :disabled="page === totalPages">Next</button>
    </div>
  </div>
 </template>

<script>
export default {
  name: 'CorrectionLog',
  props: {
    logs: {
      type: Array,
      default: () => [],
    },
    pageSize: {
      type: Number,
      default: 5,
    },
  },
  data() {
    return { page: 1 };
  },
  computed: {
    totalPages() {
      return Math.ceil(this.logs.length / this.pageSize) || 1;
    },
    pagedLogs() {
      const start = (this.page - 1) * this.pageSize;
      return this.logs.slice(start, start + this.pageSize);
    },
  },
  methods: {
    nextPage() {
      if (this.page < this.totalPages) this.page += 1;
    },
    prevPage() {
      if (this.page > 1) this.page -= 1;
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
.pagination {
  margin-top: 0.5rem;
  display: flex;
  gap: 0.5rem;
}
</style>
