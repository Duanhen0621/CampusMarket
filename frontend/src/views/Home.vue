<template>
  <div class="page">
    <div class="search-bar">
      <el-input
        v-model="keyword"
        placeholder="搜索标题、描述..."
        clearable
        @keyup.enter="load"
      />
      <el-select v-model="type" placeholder="全部类型" clearable style="width: 150px">
        <el-option label="出售" :value="1" />
        <el-option label="求购" :value="2" />
        <el-option label="交换" :value="3" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
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

    <el-empty v-if="!items.length" description="暂无商品" />

    <Pagination v-model:page="page" :size="size" :total="total" @change="load" />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'

import Pagination from '@/components/Pagination.vue'
import ProductCard from '@/components/ProductCard.vue'

const keyword = ref('')
const type = ref(null)
const page = ref(1)
const size = ref(12)
const total = ref(0)
const items = ref([])

// 骨架阶段使用本地 mock；接口接通后替换为 GET /items
const mockItems = [
  { id: 1, title: '九成新山地自行车', type: 1, price: 150 },
  { id: 2, title: '高数教材（第七版）', type: 1, price: 20 },
  { id: 3, title: '求购：宿舍小冰箱', type: 2, price: null },
  { id: 4, title: '交换：台灯换插线板', type: 3, price: null },
  { id: 5, title: '机械键盘 87 键', type: 1, price: 120 },
  { id: 6, title: '求购：考研英语真题', type: 2, price: 15 },
  { id: 7, title: '交换：露营帐篷', type: 3, price: null },
  { id: 8, title: '篮球（斯伯丁）', type: 1, price: 60 },
]

function load() {
  let list = mockItems
  if (keyword.value) {
    list = list.filter((item) => item.title.includes(keyword.value))
  }
  if (type.value) {
    list = list.filter((item) => item.type === type.value)
  }
  total.value = list.length
  const start = (page.value - 1) * size.value
  items.value = list.slice(start, start + size.value)
}

onMounted(load)
</script>
