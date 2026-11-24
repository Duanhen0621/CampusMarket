<template>
  <el-card
    class="product-card"
    shadow="hover"
    :body-style="{ padding: '0' }"
    @click="$emit('click')"
  >
    <div class="cover">
      <img v-if="coverUrl" :src="coverUrl" :alt="item.title" />
      <span v-else class="cover-placeholder">闲置</span>
      <el-tag class="type-tag" size="small" :type="typeTag">{{ typeText }}</el-tag>
    </div>
    <div class="info">
      <div class="title">{{ item.title }}</div>
      <div class="price">¥ {{ item.price ?? '面议' }}</div>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  item: { type: Object, required: true },
})

defineEmits(['click'])

const coverUrl = computed(() => {
  if (props.item.cover_url) return props.item.cover_url
  const urls = props.item.image_urls
  if (Array.isArray(urls)) return urls[0] || ''
  return urls || ''
})

const typeText = computed(
  () => ({ 1: '出售', 2: '求购', 3: '交换' })[props.item.type] || '闲置',
)

const typeTag = computed(
  () => ({ 1: 'success', 2: 'warning', 3: 'info' })[props.item.type] || '',
)
</script>
