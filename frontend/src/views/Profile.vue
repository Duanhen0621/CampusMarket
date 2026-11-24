<template>
  <div class="page">
    <el-card shadow="never">
      <div class="profile-head">
        <div>
          <h2 class="panel-title" style="margin-bottom: 6px">个人中心</h2>
          <div class="muted">学号：{{ auth.user?.student_id || '-' }}</div>
        </div>
        <el-tag :type="auth.isAdmin ? 'danger' : 'info'">
          {{ auth.isAdmin ? '平台管理员' : '普通学生' }}
        </el-tag>
      </div>
    </el-card>

    <el-card shadow="never" style="margin-top: 16px">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="我的发布" name="items">
          <el-table v-loading="loading" :data="myItems" border>
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column prop="title" label="标题" />
            <el-table-column label="价格" width="110">
              <template #default="{ row }">
                {{ row.price !== null ? `¥ ${row.price}` : '面议' }}
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="statusMap[row.status]?.type || 'info'">
                  {{ statusMap[row.status]?.text || '未知' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="reject_reason" label="驳回原因" width="180" />
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button
                  v-if="row.status !== 3"
                  size="small"
                  @click="offShelf(row)"
                >
                  下架
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty
            v-if="!loading && !myItems.length"
            description="暂无发布记录"
            :image-size="80"
          />
        </el-tab-pane>

        <el-tab-pane label="我的收藏" name="favorites">
          <el-table v-loading="favLoading" :data="favorites" border>
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column label="标题">
              <template #default="{ row }">
                <el-link type="primary" @click="$router.push(`/items/${row.id}`)">
                  {{ row.title }}
                </el-link>
              </template>
            </el-table-column>
            <el-table-column label="价格" width="110">
              <template #default="{ row }">
                {{ row.price !== null ? `¥ ${row.price}` : '面议' }}
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="statusMap[row.status]?.type || 'info'">
                  {{ statusMap[row.status]?.text || '未知' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button size="small" @click="removeFavorite(row)">
                  取消收藏
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty
            v-if="!favLoading && !favorites.length"
            description="暂无收藏"
            :image-size="80"
          />
        </el-tab-pane>

        <el-tab-pane label="我的订单" name="orders">
          <el-empty description="订单功能将在 Order 模块实现" />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import http from '@/api/http'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const activeTab = ref('items')
const loading = ref(false)
const myItems = ref([])
const favLoading = ref(false)
const favorites = ref([])

const statusMap = {
  0: { text: '待审核', type: 'warning' },
  1: { text: '展示中', type: 'success' },
  2: { text: '已驳回', type: 'danger' },
  3: { text: '已下架', type: 'info' },
}

async function loadMyItems() {
  loading.value = true
  try {
    const { data } = await http.get('/items/my', { params: { page: 1, size: 50 } })
    myItems.value = data.data.list
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '加载发布记录失败')
  } finally {
    loading.value = false
  }
}

async function offShelf(row) {
  try {
    await ElMessageBox.confirm(`确定下架「${row.title}」吗？`, '提示', {
      type: 'warning',
    })
    await http.delete(`/items/${row.id}`)
    ElMessage.success('已下架')
    loadMyItems()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '下架失败')
    }
  }
}

async function loadFavorites() {
  favLoading.value = true
  try {
    const { data } = await http.get('/favorites/my', {
      params: { page: 1, size: 50 },
    })
    favorites.value = data.data.list
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '加载收藏失败')
  } finally {
    favLoading.value = false
  }
}

async function removeFavorite(row) {
  try {
    await http.delete(`/items/${row.id}/favorite`)
    ElMessage.success('已取消收藏')
    loadFavorites()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '取消收藏失败')
  }
}

onMounted(() => {
  loadMyItems()
  loadFavorites()
})
</script>

<style scoped>
.profile-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
