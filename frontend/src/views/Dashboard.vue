<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" color="#409eff"><ShoppingCart /></el-icon>
            <div class="stat-content">
              <div class="stat-value">{{ stats.total }}</div>
              <div class="stat-label">监控商品</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" color="#67c23a"><Check /></el-icon>
            <div class="stat-content">
              <div class="stat-value">{{ stats.active }}</div>
              <div class="stat-label">启用中</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" color="#e6a23c"><Warning /></el-icon>
            <div class="stat-content">
              <div class="stat-value">{{ stats.alerts }}</div>
              <div class="stat-label">今日提醒</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" color="#f56c6c"><TrendCharts /></el-icon>
            <div class="stat-content">
              <div class="stat-value">{{ stats.price_drops }}</div>
              <div class="stat-label">降价商品</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>快速开始</span>
          </template>
          <el-steps :active="currentStep" finish-status="success">
            <el-step title="配置API" description="配置电商平台API凭证" />
            <el-step title="添加商品" description="添加需要监控的商品" />
            <el-step title="设置提醒" description="配置降价提醒渠道" />
            <el-step title="开始监控" description="系统自动监控价格变化" />
          </el-steps>
          
          <div style="margin-top: 30px; text-align: center">
            <el-button type="primary" @click="goToConfig" v-if="currentStep === 0">
              立即配置API
            </el-button>
            <el-button type="primary" @click="goToMonitor" v-else-if="currentStep === 1">
              添加商品
            </el-button>
            <el-button type="primary" @click="goToProfile" v-else-if="currentStep === 2">
              配置提醒
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ShoppingCart, Check, Warning, TrendCharts } from '@element-plus/icons-vue'
import { getMonitorItems } from '@/api/monitor'

const router = useRouter()

const stats = ref({
  total: 0,
  active: 0,
  alerts: 0,
  price_drops: 0
})

const currentStep = ref(0)

const loadStats = async () => {
  try {
    const data: any = await getMonitorItems()
    stats.value.total = data.length
    stats.value.active = data.filter((item: any) => item.is_active).length
    
    // 根据数据判断当前步骤
    if (stats.value.total === 0) {
      currentStep.value = 1
    } else {
      currentStep.value = 3
    }
  } catch (error) {
    console.error('加载统计数据失败', error)
  }
}

const goToConfig = () => {
  router.push('/config')
}

const goToMonitor = () => {
  router.push('/monitor')
}

const goToProfile = () => {
  router.push('/profile')
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  font-size: 48px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}
</style>
