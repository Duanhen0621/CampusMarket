<template>
  <div v-loading="loading" class="page">
    <el-result
      v-if="error"
      icon="warning"
      :title="error"
      sub-title="商品可能已下架或尚未通过审核"
    >
      <template #extra>
        <el-button @click="$router.push('/')">返回首页</el-button>
      </template>
    </el-result>

    <template v-else-if="item">
      <el-card shadow="never">
        <el-row :gutter="24">
          <el-col :xs="24" :md="10">
            <div class="detail-cover">
              <img v-if="activeCover" :src="activeCover" :alt="item.title" />
              <span v-else class="muted">暂无图片</span>
            </div>
            <div v-if="item.image_urls.length > 1" class="thumbs">
              <img
                v-for="url in item.image_urls"
                :key="url"
                :src="url"
                :class="{ active: url === activeCover }"
                @click="activeCover = url"
              />
            </div>
          </el-col>
          <el-col :xs="24" :md="14">
            <h2 class="panel-title">{{ item.title }}</h2>
            <div class="detail-price">
              {{ item.price !== null ? `¥ ${item.price}` : '面议' }}
            </div>
            <el-descriptions :column="1" border style="margin-top: 16px">
              <el-descriptions-item label="类型">{{ typeText }}</el-descriptions-item>
              <el-descriptions-item label="发布者">
                {{ item.publisher_display_name || '#' + item.user_id }}
              </el-descriptions-item>
              <el-descriptions-item label="发布时间">
                {{ formatTime(item.created_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="描述">
                {{ item.description || '暂无描述' }}
              </el-descriptions-item>
            </el-descriptions>
            <div class="detail-actions">
              <el-button type="primary" @click="createOrder">{{ actionText }}</el-button>
              <el-button :loading="favoriting" @click="toggleFavorite">
                {{ favorited ? '取消收藏' : '收藏' }}
              </el-button>
              <el-button @click="reportItem">举报商品</el-button>
              <el-button @click="reportSeller">举报卖家</el-button>
              <el-button @click="$router.back()">返回</el-button>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <el-card shadow="never" style="margin-top: 16px">
        <h3 class="panel-title">留言</h3>
        <div v-for="message in messages" :key="message.id" class="message">
          <span class="message-user">
            {{
              message.display_name ||
              message.student_id ||
              `#${message.user_id}`
            }}
          </span>
          <span>{{ message.content }}</span>
          <span class="message-time">{{ formatTime(message.created_at) }}</span>
        </div>
        <el-empty v-if="!messages.length" description="还没有留言" :image-size="80" />
        <div class="message-form">
          <el-input
            v-model="messageInput"
            placeholder="同学你好，商品还在吗？"
            maxlength="500"
            show-word-limit
          />
          <el-button type="primary" :loading="sending" @click="sendMessage">发送</el-button>
        </div>
      </el-card>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

import http from '@/api/http'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const item = ref(null)
const loading = ref(true)
const error = ref('')
const activeCover = ref('')
const messages = ref([])
const messageInput = ref('')
const favorited = ref(false)
const sending = ref(false)
const favoriting = ref(false)

const typeText = computed(
  () => ({ 1: '出售', 2: '求购', 3: '交换' })[item.value?.type] || '闲置',
)

const actionText = computed(
  () => ({ 1: '我想要', 2: '我要出售', 3: '我想交换' })[item.value?.type] || '联系卖家',
)

function formatTime(value) {
  if (!value) return ''
  return value.replace('T', ' ').slice(0, 16)
}

async function load() {
  loading.value = true
  try {
    const { data } = await http.get(`/items/${route.params.id}`)
    item.value = data.data
    activeCover.value = data.data.cover_url || ''
  } catch (err) {
    error.value = err.response?.data?.detail || '商品加载失败'
  } finally {
    loading.value = false
  }
}

async function loadMessages() {
  try {
    const { data } = await http.get(`/items/${route.params.id}/messages`, {
      params: { page: 1, size: 100 },
    })
    messages.value = data.data.list
  } catch {
    messages.value = []
  }
}

async function checkFavorite() {
  if (!auth.isLoggedIn) return
  try {
    const { data } = await http.get(`/favorites/check/${route.params.id}`)
    favorited.value = data.data.favorited
  } catch {
    favorited.value = false
  }
}

function requireLogin() {
  if (auth.isLoggedIn) return true
  ElMessage.warning('请先登录')
  router.push({ name: 'login', query: { redirect: route.fullPath } })
  return false
}

async function sendMessage() {
  if (!requireLogin()) return
  const content = messageInput.value.trim()
  if (!content) {
    ElMessage.warning('请输入留言内容')
    return
  }
  sending.value = true
  try {
    const { data } = await http.post(`/items/${route.params.id}/messages`, {
      content,
    })
    messages.value.push(data.data)
    messageInput.value = ''
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '留言失败')
  } finally {
    sending.value = false
  }
}

async function toggleFavorite() {
  if (!requireLogin()) return
  favoriting.value = true
  try {
    if (favorited.value) {
      await http.delete(`/items/${route.params.id}/favorite`)
      favorited.value = false
      ElMessage.success('已取消收藏')
    } else {
      await http.post(`/items/${route.params.id}/favorite`)
      favorited.value = true
      ElMessage.success('收藏成功')
    }
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '操作失败')
  } finally {
    favoriting.value = false
  }
}

async function createOrder() {
  if (!requireLogin()) return
  try {
    await http.post('/orders', { item_id: Number(route.params.id) })
    ElMessage.success('订单已发起，请等待卖家确认')
    router.push({ name: 'profile' })
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '发起订单失败')
  }
}

async function reportItem() {
  if (!requireLogin()) return
  try {
    const { value } = await ElMessageBox.prompt('请描述举报原因', '举报商品', {
      inputPattern: /\S+/,
      inputErrorMessage: '请填写举报原因',
    })
    await http.post('/reports', {
      target_type: 1,
      target_id: Number(route.params.id),
      reason: value,
    })
    ElMessage.success('举报已提交，等待管理员处理')
  } catch (err) {
    if (err !== 'cancel' && err !== 'close') {
      ElMessage.error(err.response?.data?.detail || '举报失败')
    }
  }
}


async function reportSeller() {
  if (!requireLogin()) return
  try {
    const { value } = await ElMessageBox.prompt('请描述举报原因', '举报卖家', {
      inputPattern: /\S+/,
      inputErrorMessage: '请填写举报原因',
    })
    await http.post('/reports', {
      target_type: 2,
      target_id: item.value.user_id,
      reason: value,
    })
    ElMessage.success('举报已提交，等待管理员处理')
  } catch (err) {
    if (err !== 'cancel' && err !== 'close') {
      ElMessage.error(err.response?.data?.detail || '举报失败')
    }
  }
}
onMounted(async () => {
  await load()
  if (item.value) {
    loadMessages()
    checkFavorite()
  }
})
</script>

<style scoped>
.detail-cover {
  height: 320px;
  background: #eef6f3;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.detail-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumbs {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}

.thumbs img {
  width: 64px;
  height: 64px;
  object-fit: cover;
  border-radius: 6px;
  border: 2px solid transparent;
  cursor: pointer;
}

.thumbs img.active {
  border-color: var(--cm-primary);
}

.detail-price {
  font-size: 26px;
  font-weight: 700;
  color: var(--cm-primary);
}

.detail-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

.message {
  padding: 8px 0;
  border-bottom: 1px dashed var(--cm-border);
  font-size: 14px;
}

.message-user {
  color: var(--cm-primary);
  margin-right: 8px;
}

.message-time {
  color: #a8abb2;
  font-size: 12px;
  margin-left: 8px;
}

.message-form {
  display: flex;
  gap: 10px;
  margin-top: 14px;
}
</style>
