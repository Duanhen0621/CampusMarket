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
                #{{ item.user_id }}
              </el-descriptions-item>
              <el-descriptions-item label="发布时间">
                {{ item.created_at }}
              </el-descriptions-item>
              <el-descriptions-item label="描述">
                {{ item.description || '暂无描述' }}
              </el-descriptions-item>
            </el-descriptions>
            <div class="detail-actions">
              <el-button type="primary" @click="createOrder">我想要</el-button>
              <el-button @click="toggleFavorite">
                {{ favorited ? '取消收藏' : '收藏' }}
              </el-button>
              <el-button @click="$router.back()">返回</el-button>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <el-card shadow="never" style="margin-top: 16px">
        <h3 class="panel-title">留言</h3>
        <div v-for="message in messages" :key="message.id" class="message">
          <span class="message-user">{{ message.user }}</span>
          <span>{{ message.content }}</span>
        </div>
        <el-empty v-if="!messages.length" description="还没有留言" :image-size="80" />
        <div class="message-form">
          <el-input
            v-model="messageInput"
            placeholder="同学你好，商品还在吗？"
            maxlength="500"
            show-word-limit
          />
          <el-button type="primary" @click="sendMessage">发送</el-button>
        </div>
      </el-card>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

import http from '@/api/http'

const route = useRoute()

const item = ref(null)
const loading = ref(true)
const error = ref('')
const activeCover = ref('')
const messages = ref([])
const messageInput = ref('')
const favorited = ref(false)

const typeText = computed(
  () => ({ 1: '出售', 2: '求购', 3: '交换' })[item.value?.type] || '闲置',
)

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

function sendMessage() {
  if (!messageInput.value.trim()) {
    ElMessage.warning('请输入留言内容')
    return
  }
  ElMessage.info('留言功能将在 Interaction 模块实现')
}

function toggleFavorite() {
  ElMessage.info('收藏功能将在 Interaction 模块实现')
}

function createOrder() {
  ElMessage.info('订单功能将在 Order 模块实现')
}

onMounted(load)
</script>

<style scoped>
.detail-cover {
  height: 320px;
  background: #eef2f7;
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
  border-color: #2f6fb2;
}

.detail-price {
  font-size: 26px;
  font-weight: 700;
  color: #e06c3c;
}

.detail-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

.message {
  padding: 8px 0;
  border-bottom: 1px dashed #ebeef5;
  font-size: 14px;
}

.message-user {
  color: #2f6fb2;
  margin-right: 8px;
}

.message-form {
  display: flex;
  gap: 10px;
  margin-top: 14px;
}
</style>
