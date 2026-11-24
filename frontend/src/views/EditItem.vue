<template>
  <el-card v-loading="loading" class="form-card" shadow="never">
    <h2 class="panel-title">编辑商品</h2>
    <el-form v-if="item" :model="form" label-width="80px">
      <el-form-item label="标题" required>
        <el-input v-model="form.title" maxlength="100" show-word-limit />
      </el-form-item>
      <el-form-item label="类型">
        <el-tag>{{ typeText }}</el-tag>
      </el-form-item>
      <el-form-item label="价格">
        <el-input-number
          v-model="form.price"
          :min="0"
          :precision="2"
          :disabled="item.type !== 1"
        />
        <span class="muted" style="margin-left: 8px">
          {{ item.type === 1 ? '元' : '求购 / 交换可不填' }}
        </span>
      </el-form-item>
      <el-form-item label="描述">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="4"
          maxlength="1000"
          show-word-limit
        />
      </el-form-item>
      <el-form-item label="现有图片">
        <div v-if="existingImages.length" class="existing-images">
          <div v-for="(url, index) in existingImages" :key="url" class="image-item">
            <img :src="url" alt="商品图片" />
            <el-button
              circle
              size="small"
              type="danger"
              class="remove-btn"
              @click="removeImage(index)"
            >
              ×
            </el-button>
          </div>
        </div>
        <span v-else class="muted">暂无图片</span>
      </el-form-item>
      <el-form-item label="新增图片">
        <ImageUploader v-model="newFiles" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="saving" @click="submit">
          保存并重新提交审核
        </el-button>
        <el-button @click="$router.back()">取消</el-button>
      </el-form-item>
    </el-form>
    <div class="muted">修改后会清空原审核结果，重新进入待审核状态。</div>
  </el-card>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import http from '@/api/http'
import ImageUploader from '@/components/ImageUploader.vue'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const saving = ref(false)
const item = ref(null)
const existingImages = ref([])
const newFiles = ref([])

const form = reactive({ title: '', description: '', price: null })

const typeText = computed(
  () => ({ 1: '出售', 2: '求购', 3: '交换' })[item.value?.type] || '闲置',
)

async function load() {
  loading.value = true
  try {
    const { data } = await http.get(`/items/${route.params.id}/edit`)
    item.value = data.data
    form.title = data.data.title
    form.description = data.data.description || ''
    form.price = data.data.price !== null ? Number(data.data.price) : null
    existingImages.value = [...(data.data.image_urls || [])]
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '加载商品失败')
    router.push('/profile')
  } finally {
    loading.value = false
  }
}

function removeImage(index) {
  existingImages.value.splice(index, 1)
}

async function submit() {
  if (!form.title.trim()) {
    ElMessage.warning('请填写标题')
    return
  }
  saving.value = true
  try {
    const uploaded = []
    for (const file of newFiles.value) {
      if (!file.raw) continue
      const formData = new FormData()
      formData.append('file', file.raw)
      const { data } = await http.post('/uploads/image', formData)
      uploaded.push(data.data.url)
    }
    await http.put(`/items/${route.params.id}`, {
      title: form.title,
      description: form.description || null,
      price: item.value.type === 1 ? form.price : null,
      image_urls: [...existingImages.value, ...uploaded],
    })
    ElMessage.success('已保存，重新进入审核')
    router.push('/profile')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.existing-images {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.image-item {
  position: relative;
}

.image-item img {
  width: 110px;
  height: 110px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.remove-btn {
  position: absolute;
  top: -8px;
  right: -8px;
}
</style>
