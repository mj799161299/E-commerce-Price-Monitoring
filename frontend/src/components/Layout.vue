<template>
  <el-container class="layout-container">
    <el-header>
      <div class="header-content">
        <h2>电商价格监控系统</h2>
        <div class="user-info">
          <el-dropdown @command="handleCommand">
            <span class="el-dropdown-link">
              {{ userStore.userInfo?.username }}
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </el-header>
    
    <el-container>
      <el-aside width="200px">
        <el-menu
          :default-active="activeMenu"
          router
          class="el-menu-vertical"
        >
          <el-menu-item index="/dashboard">
            <el-icon><DataLine /></el-icon>
            <span>仪表盘</span>
          </el-menu-item>
          
          <el-menu-item index="/monitor">
            <el-icon><ShoppingCart /></el-icon>
            <span>商品监控</span>
          </el-menu-item>
          
          <el-menu-item index="/config">
            <el-icon><Setting /></el-icon>
            <span>API配置</span>
          </el-menu-item>
          
          <el-menu-item index="/profile">
            <el-icon><User /></el-icon>
            <span>个人中心</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { ArrowDown, DataLine, ShoppingCart, Setting, User } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)

const handleCommand = (command: string) => {
  if (command === 'logout') {
    userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  } else if (command === 'profile') {
    router.push('/profile')
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.el-header {
  background-color: #409eff;
  color: white;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h2 {
  margin: 0;
  font-size: 20px;
}

.user-info {
  cursor: pointer;
}

.el-dropdown-link {
  color: white;
  display: flex;
  align-items: center;
  gap: 5px;
}

.el-aside {
  background-color: #f5f7fa;
  border-right: 1px solid #e4e7ed;
}

.el-menu-vertical {
  border-right: none;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>
