<template>
  <div class="config-container">
    <el-row :gutter="20">
      <!-- 淘宝/天猫配置 -->
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>淘宝/天猫 API配置</span>
              <el-tag v-if="configs.taobao?.is_valid" type="success">已验证</el-tag>
              <el-tag v-else type="info">未配置</el-tag>
            </div>
          </template>
          
          <el-form :model="taobaoForm" label-width="100px">
            <el-form-item label="App Key">
              <el-input v-model="taobaoForm.app_key" placeholder="请输入App Key" />
            </el-form-item>
            
            <el-form-item label="App Secret">
              <el-input v-model="taobaoForm.app_secret" type="password" placeholder="请输入App Secret" show-password />
            </el-form-item>
            
            <el-form-item label="PID">
              <el-input v-model="taobaoForm.pid" placeholder="推广位ID（可选）" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveConfig('taobao')" :loading="saving.taobao">
                保存配置
              </el-button>
              <el-button @click="testConfig('taobao')" :loading="testing.taobao" :disabled="!configs.taobao">
                测试连接
              </el-button>
            </el-form-item>
          </el-form>
          
          <el-divider />
          
          <div class="help-text">
            <p><strong>如何获取API凭证：</strong></p>
            <ol>
              <li>访问 <a href="https://open.taobao.com/" target="_blank">淘宝开放平台</a></li>
              <li>注册并创建应用</li>
              <li>获取App Key和App Secret</li>
              <li>开通淘宝客API权限</li>
            </ol>
          </div>
        </el-card>
      </el-col>
      
      <!-- 京东配置 -->
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>京东 API配置</span>
              <el-tag v-if="configs.jd?.is_valid" type="success">已验证</el-tag>
              <el-tag v-else type="info">未配置</el-tag>
            </div>
          </template>
          
          <el-form :model="jdForm" label-width="100px">
            <el-form-item label="App Key">
              <el-input v-model="jdForm.app_key" placeholder="请输入App Key" />
            </el-form-item>
            
            <el-form-item label="App Secret">
              <el-input v-model="jdForm.app_secret" type="password" placeholder="请输入App Secret" show-password />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveConfig('jd')" :loading="saving.jd">
                保存配置
              </el-button>
              <el-button @click="testConfig('jd')" :loading="testing.jd" :disabled="!configs.jd">
                测试连接
              </el-button>
            </el-form-item>
          </el-form>
          
          <el-divider />
          
          <div class="help-text">
            <p><strong>如何获取API凭证：</strong></p>
            <ol>
              <li>访问 <a href="https://union.jd.com/" target="_blank">京东联盟</a></li>
              <li>注册并创建应用</li>
              <li>获取App Key和App Secret</li>
              <li>开通商品查询API权限</li>
            </ol>
          </div>
        </el-card>
      </el-col>
      
      <!-- 拼多多配置 -->
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>拼多多 API配置</span>
              <el-tag v-if="configs.pdd?.is_valid" type="success">已验证</el-tag>
              <el-tag v-else type="info">未配置</el-tag>
            </div>
          </template>
          
          <el-form :model="pddForm" label-width="100px">
            <el-form-item label="Client ID">
              <el-input v-model="pddForm.app_key" placeholder="请输入Client ID" />
            </el-form-item>
            
            <el-form-item label="Client Secret">
              <el-input v-model="pddForm.app_secret" type="password" placeholder="请输入Client Secret" show-password />
            </el-form-item>
            
            <el-form-item label="PID">
              <el-input v-model="pddForm.pid" placeholder="推广位ID（可选）" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveConfig('pdd')" :loading="saving.pdd">
                保存配置
              </el-button>
              <el-button @click="testConfig('pdd')" :loading="testing.pdd" :disabled="!configs.pdd">
                测试连接
              </el-button>
            </el-form-item>
          </el-form>
          
          <el-divider />
          
          <div class="help-text">
            <p><strong>如何获取API凭证：</strong></p>
            <ol>
              <li>访问 <a href="https://jinbao.pinduoduo.com/" target="_blank">多多进宝</a></li>
              <li>注册并创建应用</li>
              <li>获取Client ID和Client Secret</li>
              <li>开通商品查询API权限</li>
            </ol>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- API配额使用情况 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>API配额使用情况</span>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="quota-card">
                <h3>淘宝/天猫</h3>
                <el-progress :percentage="getQuotaPercentage('taobao')" :color="getQuotaColor('taobao')" />
                <p>今日已用: {{ quota.taobao.used }} / {{ quota.taobao.limit }}</p>
              </div>
            </el-col>
            
            <el-col :span="8">
              <div class="quota-card">
                <h3>京东</h3>
                <el-progress :percentage="getQuotaPercentage('jd')" :color="getQuotaColor('jd')" />
                <p>今日已用: {{ quota.jd.used }} / {{ quota.jd.limit }}</p>
              </div>
            </el-col>
            
            <el-col :span="8">
              <div class="quota-card">
                <h3>拼多多</h3>
                <el-progress :percentage="getQuotaPercentage('pdd')" :color="getQuotaColor('pdd')" />
                <p>今日已用: {{ quota.pdd.used }} / {{ quota.pdd.limit }}</p>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const configs = reactive<any>({
  taobao: null,
  jd: null,
  pdd: null
})

const taobaoForm = reactive({
  app_key: '',
  app_secret: '',
  pid: ''
})

const jdForm = reactive({
  app_key: '',
  app_secret: ''
})

const pddForm = reactive({
  app_key: '',
  app_secret: '',
  pid: ''
})

const saving = reactive({
  taobao: false,
  jd: false,
  pdd: false
})

const testing = reactive({
  taobao: false,
  jd: false,
  pdd: false
})

const quota = reactive({
  taobao: { used: 0, limit: 10000 },
  jd: { used: 0, limit: 20000 },
  pdd: { used: 0, limit: 10000 }
})

// 加载配置
const loadConfigs = async () => {
  const platforms = ['taobao', 'jd', 'pdd']
  
  for (const platform of platforms) {
    try {
      const data: any = await request.get(`/config/platforms/${platform}`)
      configs[platform] = data
    } catch (error) {
      // 未配置时会返回404，这是正常的
    }
  }
}

// 加载配额
const loadQuota = async () => {
  try {
    const data: any = await request.get('/config/quota')
    Object.assign(quota, data)
  } catch (error) {
    console.error('加载配额失败', error)
  }
}

// 保存配置
const saveConfig = async (platform: string) => {
  saving[platform] = true
  
  try {
    let formData: any
    if (platform === 'taobao') {
      formData = { ...taobaoForm, platform }
    } else if (platform === 'jd') {
      formData = { ...jdForm, platform }
    } else {
      formData = { ...pddForm, platform }
    }
    
    const data: any = await request.post(`/config/platforms/${platform}`, formData)
    configs[platform] = data
    ElMessage.success('配置保存成功')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving[platform] = false
  }
}

// 测试连接
const testConfig = async (platform: string) => {
  testing[platform] = true
  
  try {
    const data: any = await request.post(`/config/platforms/${platform}/test`)
    if (data.success) {
      ElMessage.success('API连接测试成功')
      configs[platform].is_valid = true
    } else {
      ElMessage.error(data.message || 'API连接测试失败')
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '测试失败')
  } finally {
    testing[platform] = false
  }
}

// 计算配额百分比
const getQuotaPercentage = (platform: string) => {
  const { used, limit } = quota[platform]
  return limit > 0 ? Math.round((used / limit) * 100) : 0
}

// 获取配额颜色
const getQuotaColor = (platform: string) => {
  const percentage = getQuotaPercentage(platform)
  if (percentage < 50) return '#67c23a'
  if (percentage < 80) return '#e6a23c'
  return '#f56c6c'
}

onMounted(() => {
  loadConfigs()
  loadQuota()
})
</script>

<style scoped>
.config-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.help-text {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
}

.help-text ol {
  margin: 10px 0;
  padding-left: 20px;
}

.help-text a {
  color: #409eff;
  text-decoration: none;
}

.help-text a:hover {
  text-decoration: underline;
}

.quota-card {
  text-align: center;
}

.quota-card h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #303133;
}

.quota-card p {
  margin: 10px 0 0 0;
  font-size: 14px;
  color: #606266;
}
</style>
