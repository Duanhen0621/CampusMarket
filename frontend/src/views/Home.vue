<template>
  <div v-loading="loading" class="page">
    <section class="home-hero">
      <div class="hero-copy">
        <div class="hero-label">CAMPUS MARKET</div>
        <h1>让闲置流动起来</h1>
        <p>校园里的好物，遇见下一位主人</p>
      </div>
      <div class="hero-badge">
        <b>共 {{ total }} 件好物</b>
        <span>持续更新的校园好物</span>
      </div>
    </section>

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


<style scoped>
.home-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 34px 38px;
  margin-bottom: 22px;
  border: 1px solid var(--cm-border);
  border-radius: 26px;
  background: linear-gradient(120deg, #e6f7f1, #e8f1ff);
  overflow: hidden;
  position: relative;
}

.home-hero::after {
  content: "";
  position: absolute;
  right: -70px;
  top: -90px;
  width: 260px;
  height: 260px;
  border-radius: 50%;
  background: rgba(47, 128, 237, 0.08);
}

.hero-copy,
.hero-badge {
  position: relative;
  z-index: 1;
}

.hero-label {
  margin-bottom: 10px;
  color: var(--cm-primary);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 2.2px;
}

.home-hero h1 {
  margin: 0 0 10px;
  font-size: clamp(28px, 4vw, 38px);
  line-height: 1.2;
  letter-spacing: -0.6px;
}

.home-hero p {
  margin: 0;
  color: var(--cm-muted);
  font-size: 14px;
}

.hero-badge {
  padding: 14px 20px;
  border: 1px solid var(--cm-border);
  border-radius: 14px;
  background: #fff;
  box-shadow: var(--cm-shadow);
  white-space: nowrap;
}

.hero-badge b {
  display: block;
  margin-bottom: 2px;
  color: var(--cm-primary);
  font-size: 21px;
}

.hero-badge span {
  color: var(--cm-muted);
  font-size: 12px;
}

@media (max-width: 720px) {
  .home-hero {
    align-items: flex-start;
    flex-direction: column;
    padding: 24px;
  }

  .hero-badge {
    display: none;
  }
}
</style>