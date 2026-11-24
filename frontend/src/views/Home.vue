<template>
  <div v-loading="loading" class="page">
    <div class="search-bar">
      <el-input
        v-model="keyword"
        placeholder="搜索标题、描述..."
        clearable
        @keyup.enter="search"
      />
      <el-select v-model="type" placeholder="全部类型" clearable style="width: 150px">
        <el-option label="出售" :value="1" />
        <el-option label="求购" :value="2" />
        <el-option label="交换" :value="3" />
      </el-select>
      <el-button type="primary" @click="search">搜索</el-button>
    </div>

    <el-row :gutter="18">
      <el-col
        v-for="item in items"
        :key="item.id"
        :xs="12"
        :sm="8"
        :md="6"
      >
        <ProductCard :item="item" @click="$router.push(`/items/${item.id}`)" />
      </el-col>
    </el-row>

    <el-empty v-if="!loading && !items.length" description="暂无商品" />

    <Pagination v-model:page="page" :size="size" :total="total" @change="load" />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'

import http from '@/api/http'
import Pagination from '@/components/Pagination.vue'
import ProductCard from '@/components/ProductCard.vue'

const keyword = ref('')
const type = ref(null)
const page = ref(1)
const size = ref(12)
const total = ref(0)
const items = ref([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const { data } = await http.get('/items', {
      params: {
        page: page.value,
        size: size.value,
        keyword: keyword.value || undefined,
        type: type.value || undefined,
      },
    })
    items.value = data.data.list
    total.value = data.data.total
  } catch (error) {
    items.value = []
    total.value = 0
    ElMessage.error(error.response?.data?.detail || '加载商品失败')
  } finally {
    loading.value = false
  }
}

function search() {
  page.value = 1
  load()
}

onMounted(load)
</script>
