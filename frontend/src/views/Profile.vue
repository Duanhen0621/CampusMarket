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
          <el-empty description="暂无发布记录（接口接入后展示）" />
        </el-tab-pane>
        <el-tab-pane label="我的收藏" name="favorites">
          <el-empty description="暂无收藏（接口接入后展示）" />
        </el-tab-pane>
        <el-tab-pane label="我的订单" name="orders">
          <el-empty description="暂无订单（接口接入后展示）" />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'

import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const activeTab = ref('items')
</script>

<style scoped>
.profile-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
