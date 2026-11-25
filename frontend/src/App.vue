<template>
  <el-container class="app-shell">
    <el-header class="app-header">
      <div class="brand" @click="router.push('/')">
        <span class="brand-mark">闲</span>
        <span>校园闲置集市</span>
      </div>

      <nav class="nav">
        <router-link to="/" :class="{ active: isActive('/') }">首页</router-link>
        <router-link to="/publish" :class="{ active: isActive('/publish') }">
          发布
        </router-link>
        <router-link to="/profile" :class="{ active: isActive('/profile') }">
          我的
        </router-link>
        <router-link
          v-if="auth.isAdmin"
          to="/admin"
          :class="{ active: isActive('/admin') }"
        >
          管理后台
        </router-link>
      </nav>

      <div class="header-right">
        <template v-if="auth.isLoggedIn">
          <span class="student">{{ auth.displayName }}</span>
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
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

function isActive(path) {
  if (path === '/') {
    return (
      route.path === '/' ||
      (route.path.startsWith('/items/') && !route.path.endsWith('/edit'))
    )
  }
  if (path === '/profile') {
    return route.path.startsWith('/profile') || route.path.endsWith('/edit')
  }
  return route.path.startsWith(path)
}

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
