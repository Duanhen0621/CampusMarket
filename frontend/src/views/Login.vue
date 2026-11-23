<template>
  <el-card class="form-card" shadow="never">
    <el-tabs v-model="mode">
      <el-tab-pane label="登录" name="login">
        <el-form :model="loginForm" label-width="70px" @submit.prevent="submitLogin">
          <el-form-item label="学号">
            <el-input v-model="loginForm.student_id" placeholder="请输入学号" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input
              v-model="loginForm.password"
              type="password"
              show-password
              placeholder="请输入密码"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="loading" @click="submitLogin">
              登录
            </el-button>
            <el-button link @click="$router.push('/')">先去逛逛</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="注册" name="register">
        <el-form
          :model="registerForm"
          label-width="70px"
          @submit.prevent="submitRegister"
        >
          <el-form-item label="学号">
            <el-input v-model="registerForm.student_id" placeholder="4-20 位学号" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input
              v-model="registerForm.password"
              type="password"
              show-password
              placeholder="至少 6 位"
            />
          </el-form-item>
          <el-form-item label="手机号">
            <el-input v-model="registerForm.phone" placeholder="选填" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="loading" @click="submitRegister">
              注册并登录
            </el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>

    <div class="muted">登录后可发布商品、留言、收藏与发起交易订单。</div>
  </el-card>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import http from '@/api/http'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const mode = ref('login')
const loading = ref(false)

const loginForm = reactive({ student_id: '', password: '' })
const registerForm = reactive({ student_id: '', password: '', phone: '' })

function goAfterLogin() {
  router.push(route.query.redirect || '/')
}

async function submitLogin() {
  if (!loginForm.student_id || !loginForm.password) {
    ElMessage.warning('请输入学号和密码')
    return
  }
  loading.value = true
  try {
    await auth.login({ ...loginForm })
    ElMessage.success('登录成功')
    goAfterLogin()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}

async function submitRegister() {
  if (!registerForm.student_id || !registerForm.password) {
    ElMessage.warning('请填写学号和密码')
    return
  }
  if (registerForm.password.length < 6) {
    ElMessage.warning('密码至少 6 位')
    return
  }
  loading.value = true
  try {
    await http.post('/auth/register', {
      student_id: registerForm.student_id,
      password: registerForm.password,
      phone: registerForm.phone || null,
    })
    await auth.login({
      student_id: registerForm.student_id,
      password: registerForm.password,
    })
    ElMessage.success('注册成功')
    goAfterLogin()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>
