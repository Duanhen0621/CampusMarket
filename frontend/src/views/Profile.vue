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
          <el-table v-loading="orderLoading" :data="orders" border>
            <el-table-column label="商品">
              <template #default="{ row }">
                <el-link type="primary" @click="$router.push(`/items/${row.item_id}`)">
                  {{ row.item_title }}
                </el-link>
              </template>
            </el-table-column>
            <el-table-column label="我的身份" width="90">
              <template #default="{ row }">
                {{ isSeller(row) ? '卖家' : '买家' }}
              </template>
            </el-table-column>
            <el-table-column label="对方" width="130">
              <template #default="{ row }">
                {{ isSeller(row) ? row.buyer_student_id : row.seller_student_id }}
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="orderStatusMap[row.status]?.type || 'info'">
                  {{ orderStatusMap[row.status]?.text || '未知' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="创建时间" width="170">
              <template #default="{ row }">
                {{ row.created_at?.replace('T', ' ').slice(0, 16) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="220">
              <template #default="{ row }">
                <template v-if="row.status === 0">
                  <el-button
                    v-if="isSeller(row)"
                    size="small"
                    type="primary"
                    @click="updateOrder(row, 1)"
                  >
                    确认交易
                  </el-button>
                  <el-button size="small" @click="updateOrder(row, 3)">
                    取消订单
                  </el-button>
                </template>
                <template v-else-if="row.status === 1">
                  <el-button size="small" type="success" @click="updateOrder(row, 2)">
                    完成交易
                  </el-button>
                  <el-button size="small" @click="updateOrder(row, 3)">
                    取消订单
                  </el-button>
                </template>
                <span v-else class="muted">—</span>
              </template>
            </el-table-column>
          </el-table>
          <el-empty
            v-if="!orderLoading && !orders.length"
            description="暂无订单"
            :image-size="80"
          />
        </el-tab-pane>

        <el-tab-pane label="我的举报" name="reports">
          <el-table v-loading="reportLoading" :data="myReports" border>
            <el-table-column prop="target_label" label="举报对象" width="220" />
            <el-table-column prop="reason" label="举报原因" />
            <el-table-column label="状态" width="110">
              <template #default="{ row }">
                <el-tag :type="reportStatusMap[row.status]?.type || 'info'">
                  {{ reportStatusMap[row.status]?.text || '未知' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="handle_note" label="处理结果" width="180" />
            <el-table-column label="提交时间" width="170">
              <template #default="{ row }">
                {{ row.created_at?.replace('T', ' ').slice(0, 16) }}
              </template>
            </el-table-column>
          </el-table>
          <el-empty
            v-if="!reportLoading && !myReports.length"
            description="暂无举报记录"
            :image-size="80"
          />
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
const orderLoading = ref(false)
const orders = ref([])
const reportLoading = ref(false)
const myReports = ref([])

const reportStatusMap = {
  0: { text: '待处理', type: 'warning' },
  1: { text: '已处理', type: 'success' },
  2: { text: '已驳回', type: 'info' },
}

const orderStatusMap = {
  0: { text: '待确认', type: 'warning' },
  1: { text: '交易中', type: 'primary' },
  2: { text: '已完成', type: 'success' },
  3: { text: '已取消', type: 'info' },
}

function isSeller(row) {
  return row.seller_id === auth.user?.id
}

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

async function loadOrders() {
  orderLoading.value = true
  try {
    const { data } = await http.get('/orders/my', { params: { page: 1, size: 50 } })
    orders.value = data.data.list
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '加载订单失败')
  } finally {
    orderLoading.value = false
  }
}

async function updateOrder(row, targetStatus) {
  const labels = { 1: '确认交易', 2: '完成交易', 3: '取消订单' }
  try {
    await ElMessageBox.confirm(`确定${labels[targetStatus]}吗？`, '订单操作', {
      type: 'warning',
    })
    await http.put(`/orders/${row.id}/status`, { status: targetStatus })
    ElMessage.success(`${labels[targetStatus]}成功`)
    loadOrders()
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    }
  }
}

async function loadMyReports() {
  reportLoading.value = true
  try {
    const { data } = await http.get('/reports/my', {
      params: { page: 1, size: 50 },
    })
    myReports.value = data.data.list
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '加载举报记录失败')
  } finally {
    reportLoading.value = false
  }
}

onMounted(() => {
  loadMyItems()
  loadFavorites()
  loadOrders()
  loadMyReports()
})
</script>

<style scoped>
.profile-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
