<template>
  <el-container class="app-shell">
    <el-header class="app-header">
      <div class="brand" @click="router.push('/')">校园闲置集市</div>

      <el-menu
        mode="horizontal"
        :default-active="activeMenu"
        :ellipsis="false"
        router
        class="nav"
      >
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/publish">发布</el-menu-item>
        <el-menu-item index="/profile">我的</el-menu-item>
        <el-menu-item v-if="auth.isAdmin" index="/admin">管理后台</el-menu-item>
      </el-menu>

      <div class="header-right">
        <template v-if="auth.isLoggedIn">
          <span class="student">{{ auth.user?.student_id }}</span>
          <el-button link @click="handleLogout">退出</el-button>
        </template>
        <el-button v-else type="primary" @click="router.push('/login')">
          登录
        </el-button>
      </div>
    </el-header>

    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const activeMenu = computed(() => {
  if (route.path.startsWith('/items/')) return '/'
  return route.path
})

function handleLogout() {
  auth.logout()
  router.push('/')
}

onMounted(() => {
  if (auth.isLoggedIn) {
    auth.fetchMe().catch(() => {})
  }
})
</script>
