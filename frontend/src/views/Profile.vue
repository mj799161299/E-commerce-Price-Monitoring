<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <!-- 用户信息 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>个人信息</span>
          </template>
          
          <el-form :model="userForm" label-width="100px">
            <el-form-item label="用户名">
              <el-input v-model="userForm.username" disabled />
            </el-form-item>
            
            <el-form-item label="邮箱">
              <el-input v-model="userForm.email" />
            </el-form-item>
            
            <el-form-item label="注册时间">
              <el-input v-model="userForm.create_time" disabled />
            </el-form-item>
            
            <el-form-item label="账号状态">
              <el-tag v-if="userForm.is_active" type="success">正常</el-tag>
              <el-tag v-else type="danger">已禁用</el-tag>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="updateUserInfo" :loading="updating">
                更新信息
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      
      <!-- 修改密码 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>修改密码</span>
          </template>
          
          <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px">
            <el-form-item label="当前密码" prop="old_password">
              <el-input v-model="passwordForm.old_password" type="password" show-password />
            </el-form-item>
            
            <el-form-item label="新密码" prop="new_password">
              <el-input v-model="passwordForm.new_password" type="password" show-password />
            </el-form-item>
            
            <el-form-item label="确认密码" prop="confirm_password">
              <el-input v-model="passwordForm.confirm_password" type="password" show-password />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="changePassword" :loading="changingPassword">
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 推送渠道配置 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>推送渠道配置</span>
              <el-button type="primary" size="small" @click="showAddChannelDialog">
                <el-icon><Plus /></el-icon>
                添加渠道
              </el-button>
            </div>
          </template>
          
          <el-table :data="pushChannels" v-loading="loadingChannels">
            <el-table-column prop="channel_type" label="渠道类型" width="150">
              <template #default="{ row }">
                <el-tag v-if="row.channel_type === 'serverchan'" type="success">Server酱</el-tag>
                <el-tag v-else-if="row.channel_type === 'wecom'" type="primary">企业微信</el-tag>
                <el-tag v-else-if="row.channel_type === 'dingtalk'" type="info">钉钉</el-tag>
                <el-tag v-else-if="row.channel_type === 'feishu'" type="warning">飞书</el-tag>
                <el-tag v-else>邮件</el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="is_active" label="状态" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.is_active" type="success">启用</el-tag>
                <el-tag v-else type="info">禁用</el-tag>
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button size="small" @click="testChannel(row)">测试</el-button>
                <el-button size="small" type="danger" @click="deleteChannel(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 添加推送渠道对话框 -->
    <el-dialog v-model="channelDialogVisible" title="添加推送渠道" width="600px">
      <el-form :model="channelForm" label-width="120px">
        <el-form-item label="渠道类型">
          <el-select v-model="channelForm.channel_type" placeholder="请选择">
            <el-option label="Server酱" value="serverchan" />
            <el-option label="企业微信" value="wecom" />
            <el-option label="钉钉" value="dingtalk" />
            <el-option label="飞书" value="feishu" />
            <el-option label="邮件" value="email" />
          </el-select>
        </el-form-item>
        
        <!-- Server酱配置 -->
        <template v-if="channelForm.channel_type === 'serverchan'">
          <el-form-item label="SendKey">
            <el-input v-model="channelForm.config.sendkey" placeholder="请输入SendKey" />
          </el-form-item>
          <el-alert title="获取SendKey" type="info" :closable="false">
            访问 <a href="https://sct.ftqq.com/" target="_blank">https://sct.ftqq.com/</a> 注册并获取SendKey
          </el-alert>
        </template>
        
        <!-- 企业微信/钉钉/飞书配置 -->
        <template v-else-if="['wecom', 'dingtalk', 'feishu'].includes(channelForm.channel_type)">
          <el-form-item label="Webhook URL">
            <el-input v-model="channelForm.config.webhook" placeholder="请输入Webhook URL" />
          </el-form-item>
          <el-alert title="获取Webhook" type="info" :closable="false">
            在群聊中添加机器人，获取Webhook地址
          </el-alert>
        </template>
        
        <!-- 邮件配置 -->
        <template v-else-if="channelForm.channel_type === 'email'">
          <el-form-item label="SMTP服务器">
            <el-input v-model="channelForm.config.smtp_host" placeholder="smtp.example.com" />
          </el-form-item>
          <el-form-item label="SMTP端口">
            <el-input-number v-model="channelForm.config.smtp_port" :min="1" :max="65535" />
          </el-form-item>
          <el-form-item label="发件邮箱">
            <el-input v-model="channelForm.config.smtp_user" placeholder="user@example.com" />
          </el-form-item>
          <el-form-item label="邮箱密码">
            <el-input v-model="channelForm.config.smtp_password" type="password" show-password />
          </el-form-item>
          <el-form-item label="收件邮箱">
            <el-input v-model="channelForm.config.to_email" placeholder="recipient@example.com" />
          </el-form-item>
        </template>
      </el-form>
      
      <template #footer>
        <el-button @click="channelDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addChannel" :loading="addingChannel">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import request from '@/utils/request'

const userStore = useUserStore()
const updating = ref(false)
const changingPassword = ref(false)
const loadingChannels = ref(false)
const channelDialogVisible = ref(false)
const addingChannel = ref(false)
const passwordFormRef = ref()

const userForm = reactive({
  username: '',
  email: '',
  create_time: '',
  is_active: true
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const passwordRules = {
  old_password: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule: any, value: any, callback: any) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const pushChannels = ref([])

const channelForm = reactive({
  channel_type: 'serverchan',
  config: {} as any
})

// 加载用户信息
const loadUserInfo = async () => {
  try {
    const data: any = await request.get('/auth/me')
    Object.assign(userForm, {
      ...data,
      create_time: new Date(data.create_time).toLocaleString()
    })
  } catch (error) {
    ElMessage.error('加载用户信息失败')
  }
}

// 更新用户信息
const updateUserInfo = async () => {
  updating.value = true
  try {
    await request.put('/auth/me', { email: userForm.email })
    ElMessage.success('更新成功')
  } catch (error) {
    ElMessage.error('更新失败')
  } finally {
    updating.value = false
  }
}

// 修改密码
const changePassword = async () => {
  await passwordFormRef.value.validate()
  changingPassword.value = true
  
  try {
    // TODO: 实现修改密码API
    ElMessage.info('修改密码功能开发中')
  } catch (error) {
    ElMessage.error('修改密码失败')
  } finally {
    changingPassword.value = false
  }
}

// 加载推送渠道
const loadPushChannels = async () => {
  loadingChannels.value = true
  try {
    const data: any = await request.get('/push/channels')
    pushChannels.value = data
  } catch (error) {
    ElMessage.error('加载推送渠道失败')
  } finally {
    loadingChannels.value = false
  }
}

// 显示添加渠道对话框
const showAddChannelDialog = () => {
  channelForm.channel_type = 'serverchan'
  channelForm.config = {}
  channelDialogVisible.value = true
}

// 添加推送渠道
const addChannel = async () => {
  addingChannel.value = true
  try {
    await request.post('/push/channels', {
      channel_type: channelForm.channel_type,
      channel_config: channelForm.config
    })
    ElMessage.success('添加成功')
    channelDialogVisible.value = false
    loadPushChannels()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '添加失败')
  } finally {
    addingChannel.value = false
  }
}

// 测试推送渠道
const testChannel = async (row: any) => {
  try {
    const data: any = await request.post(`/push/channels/${row.id}/test`)
    if (data.success) {
      ElMessage.success('测试推送发送成功，请查收')
    } else {
      ElMessage.error(data.message || '测试推送发送失败')
    }
  } catch (error) {
    ElMessage.error('测试失败')
  }
}

// 删除推送渠道
const deleteChannel = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除该推送渠道吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await request.delete(`/push/channels/${row.id}`)
    ElMessage.success('删除成功')
    loadPushChannels()
  } catch (error) {
    // 用户取消
  }
}

onMounted(() => {
  loadUserInfo()
  loadPushChannels()
})
</script>

<style scoped>
.profile-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-alert {
  margin-top: 10px;
}

.el-alert a {
  color: #409eff;
  text-decoration: none;
}

.el-alert a:hover {
  text-decoration: underline;
}
</style>
