<template>
  <el-card class="form-card" shadow="never">
    <h2 class="panel-title">发布闲置</h2>
    <el-form :model="form" label-width="80px">
      <el-form-item label="标题" required>
        <el-input v-model="form.title" maxlength="100" show-word-limit />
      </el-form-item>
      <el-form-item label="类型" required>
        <el-radio-group v-model="form.type">
          <el-radio :value="1">出售</el-radio>
          <el-radio :value="2">求购</el-radio>
          <el-radio :value="3">交换</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="价格">
        <el-input-number
          v-model="form.price"
          :min="0"
          :precision="2"
          :disabled="form.type !== 1"
        />
        <span class="muted" style="margin-left: 8px">
          {{ form.type === 1 ? '元' : '求购 / 交换可不填' }}
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
      <el-form-item label="图片">
        <ImageUploader v-model="form.files" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="loading" @click="submit">
          提交审核
        </el-button>
      </el-form-item>
    </el-form>
    <div class="muted">
      骨架阶段：发布接口尚未实现（POST /api/v1/items），图片上传接口随后接入。
    </div>
  </el-card>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'

import http from '@/api/http'
import ImageUploader from '@/components/ImageUploader.vue'

const loading = ref(false)
const form = reactive({
  title: '',
  type: 1,
  price: null,
  description: '',
  files: [],
})

async function submit() {
  if (!form.title.trim()) {
    ElMessage.warning('请填写标题')
    return
  }
  loading.value = true
  try {
    await http.post('/items', {
      title: form.title,
      description: form.description || null,
      type: form.type,
      price: form.price,
      image_urls: [],
    })
    ElMessage.success('发布成功，等待审核')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '发布失败')
  } finally {
    loading.value = false
  }
}
</script>
