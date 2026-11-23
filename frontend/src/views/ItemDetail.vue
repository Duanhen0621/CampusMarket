<template>
  <div class="page">
    <el-card shadow="never">
      <el-row :gutter="24">
        <el-col :xs="24" :md="10">
          <div class="detail-cover">
            <img v-if="item.cover_url" :src="item.cover_url" :alt="item.title" />
            <span v-else class="muted">暂无图片</span>
          </div>
        </el-col>
        <el-col :xs="24" :md="14">
          <h2 class="panel-title">{{ item.title }}</h2>
          <div class="detail-price">¥ {{ item.price ?? '面议' }}</div>
          <el-descriptions :column="1" border style="margin-top: 16px">
            <el-descriptions-item label="类型">
              {{ typeText }}
            </el-descriptions-item>
            <el-descriptions-item label="发布者">
              {{ item.student_id }}
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
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

const route = useRoute()

const item = computed(() => ({
  id: Number(route.params.id),
  title: `商品 #${route.params.id}（骨架示例数据）`,
  type: 1,
  price: 150,
  cover_url: '',
  description: '接口接通后展示商品的真实标题、图片、价格与描述。',
  student_id: '20210001',
}))

const typeText = computed(
  () => ({ 1: '出售', 2: '求购', 3: '交换' })[item.value.type] || '闲置',
)

const messages = ref([])
const messageInput = ref('')
const favorited = ref(false)

function sendMessage() {
  if (!messageInput.value.trim()) {
    ElMessage.warning('请输入留言内容')
    return
  }
  ElMessage.info('留言接口尚未实现（POST /api/v1/items/{id}/messages）')
}

function toggleFavorite() {
  ElMessage.info('收藏接口尚未实现（POST/DELETE /api/v1/items/{id}/favorite）')
}

function createOrder() {
  ElMessage.info('订单接口尚未实现（POST /api/v1/orders）')
}
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
