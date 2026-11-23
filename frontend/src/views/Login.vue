<template>
  <el-card class="form-card" shadow="never">
    <h2 class="panel-title">登录</h2>
    <el-form :model="form" label-width="70px" @submit.prevent="submit">
      <el-form-item label="学号">
        <el-input v-model="form.student_id" placeholder="请输入学号" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input
          v-model="form.password"
          type="password"
          show-password
          placeholder="请输入密码"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="loading" @click="submit">
          登录
        </el-button>
        <el-button link @click="$router.push('/')">先去逛逛</el-button>
      </el-form-item>
    </el-form>
    <div class="muted">
      当前为骨架阶段，登录接口尚未实现（POST /api/v1/auth/login）。
    </div>
  </el-card>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const loading = ref(false)
const form = reactive({ student_id: '', password: '' })

async function submit() {
  if (!form.student_id || !form.password) {
    ElMessage.warning('请输入学号和密码')
    return
  }
  loading.value = true
  try {
    await auth.login({ ...form })
    ElMessage.success('登录成功')
    router.push(route.query.redirect || '/')
  } catch (error) {
    const detail = error.response?.data?.detail
    ElMessage.error(detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>
