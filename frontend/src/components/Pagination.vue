<template>
  <div class="pagination">
    <el-pagination
      background
      layout="prev, pager, next, total"
      :total="total"
      :current-page="page"
      :page-size="size"
      @current-change="onPageChange"
    />
  </div>
</template>

<script setup>
const props = defineProps({
  total: { type: Number, default: 0 },
  page: { type: Number, default: 1 },
  size: { type: Number, default: 10 },
})

const emit = defineEmits(['update:page', 'change'])

function onPageChange(page) {
  emit('update:page', page)
  emit('change', page)
}
</script>
