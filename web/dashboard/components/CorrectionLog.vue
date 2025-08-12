<template>
  <div>
    <input v-model="filter" placeholder="Filter logs" />
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
import { startCorrectionsListener } from '../../../dashboard/static/js/corrections_ws_listener.js';
export default {
  name: 'CorrectionLog',
  data() {
    return {
      logs: [],
      page: 1,
      pageSize: 5,
      filter: '',
    };
  },
  computed: {
    filteredLogs() {
      if (!this.filter) return this.logs;
      const term = this.filter.toLowerCase();
      return this.logs.filter(
        (l) =>
          l.entity.toLowerCase().includes(term) ||
          l.resolution.toLowerCase().includes(term)
      );
    },
    totalPages() {
      return Math.ceil(this.filteredLogs.length / this.pageSize) || 1;
    },
    pagedLogs() {
      const start = (this.page - 1) * this.pageSize;
      return this.filteredLogs.slice(start, start + this.pageSize);
    },
  },
  methods: {
    nextPage() {
      if (this.page < this.totalPages) this.page += 1;
    },
    prevPage() {
      if (this.page > 1) this.page -= 1;
    },
    fetchLogs() {
      fetch('/corrections/logs?limit=50')
        .then((r) => r.json())
        .then((d) => {
          this.logs = d;
        });
    },
  },
  created() {
    this.fetchLogs();
    startCorrectionsListener((data) => {
      this.logs = this.logs.concat(data);
      this.page = this.totalPages;
    });
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
