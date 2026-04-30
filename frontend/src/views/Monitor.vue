<template>
  <div class="monitor-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>商品监控管理</span>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>
            添加商品
          </el-button>
        </div>
      </template>

      <!-- 商品列表 -->
      <el-table :data="monitorItems" v-loading="loading" style="width: 100%">
        <el-table-column prop="goods_image" label="商品图片" width="100">
          <template #default="{ row }">
            <el-image 
              :src="row.goods_image || 'https://via.placeholder.com/80'" 
              fit="cover"
              style="width: 60px; height: 60px"
            />
          </template>
        </el-table-column>
        
        <el-table-column prop="goods_title" label="商品名称" min-width="200" show-overflow-tooltip />
        
        <el-table-column prop="platform" label="平台" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.platform === 'taobao'" type="warning">淘宝</el-tag>
            <el-tag v-else-if="row.platform === 'jd'" type="danger">京东</el-tag>
            <el-tag v-else-if="row.platform === 'pdd'" type="success">拼多多</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="current_price" label="当前价格" width="120">
          <template #default="{ row }">
            <span style="color: #f56c6c; font-weight: bold">¥{{ row.current_price }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="threshold_price" label="阈值" width="120">
          <template #default="{ row }">
            ¥{{ row.threshold_price }}
          </template>
        </el-table-column>
        
        <el-table-column prop="monitor_interval" label="监控频率" width="120">
          <template #default="{ row }">
            {{ row.monitor_interval }}分钟
          </template>
        </el-table-column>
        
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.is_active" type="success">启用</el-tag>
            <el-tag v-else type="info">暂停</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewHistory(row)">历史</el-button>
            <el-button size="small" type="primary" @click="editItem(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteItem(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加商品对话框 -->
    <el-dialog v-model="addDialogVisible" title="添加监控商品" width="600px">
      <el-form :model="addForm" :rules="addRules" ref="addFormRef" label-width="120px">
        <el-form-item label="商品链接" prop="goods_url">
          <el-input 
            v-model="addForm.goods_url" 
            placeholder="请输入淘宝/京东/拼多多商品链接"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="阈值类型" prop="threshold_type">
          <el-select v-model="addForm.threshold_type" placeholder="请选择">
            <el-option label="售价低于" value="price" />
            <el-option label="券后价低于" value="coupon_price" />
            <el-option label="降幅超过" value="discount" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="阈值" prop="threshold_price">
          <el-input-number 
            v-model="addForm.threshold_price" 
            :min="0" 
            :precision="2"
            :step="10"
          />
          <span v-if="addForm.threshold_type === 'discount'" style="margin-left: 10px">%</span>
          <span v-else style="margin-left: 10px">元</span>
        </el-form-item>
        
        <el-form-item label="监控频率" prop="monitor_interval">
          <el-input-number 
            v-model="addForm.monitor_interval" 
            :min="10" 
            :max="1440"
            :step="10"
          />
          <span style="margin-left: 10px">分钟</span>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAdd" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 编辑商品对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑监控商品" width="600px">
      <el-form :model="editForm" :rules="addRules" ref="editFormRef" label-width="120px">
        <el-form-item label="阈值类型" prop="threshold_type">
          <el-select v-model="editForm.threshold_type" placeholder="请选择">
            <el-option label="售价低于" value="price" />
            <el-option label="券后价低于" value="coupon_price" />
            <el-option label="降幅超过" value="discount" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="阈值" prop="threshold_price">
          <el-input-number 
            v-model="editForm.threshold_price" 
            :min="0" 
            :precision="2"
            :step="10"
          />
          <span v-if="editForm.threshold_type === 'discount'" style="margin-left: 10px">%</span>
          <span v-else style="margin-left: 10px">元</span>
        </el-form-item>
        
        <el-form-item label="监控频率" prop="monitor_interval">
          <el-input-number 
            v-model="editForm.monitor_interval" 
            :min="10" 
            :max="1440"
            :step="10"
          />
          <span style="margin-left: 10px">分钟</span>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-switch v-model="editForm.is_active" active-text="启用" inactive-text="暂停" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEdit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getMonitorItems, addMonitorItem, updateMonitorItem, deleteMonitorItem } from '@/api/monitor'

const loading = ref(false)
const submitting = ref(false)
const monitorItems = ref([])
const addDialogVisible = ref(false)
const editDialogVisible = ref(false)
const addFormRef = ref()
const editFormRef = ref()

const addForm = ref({
  goods_url: '',
  threshold_type: 'price',
  threshold_price: 100,
  monitor_interval: 60
})

const editForm = ref({
  id: 0,
  threshold_type: 'price',
  threshold_price: 100,
  monitor_interval: 60,
  is_active: true
})

const addRules = {
  goods_url: [{ required: true, message: '请输入商品链接', trigger: 'blur' }],
  threshold_type: [{ required: true, message: '请选择阈值类型', trigger: 'change' }],
  threshold_price: [{ required: true, message: '请输入阈值', trigger: 'blur' }],
  monitor_interval: [{ required: true, message: '请输入监控频率', trigger: 'blur' }]
}

// 加载监控列表
const loadMonitorItems = async () => {
  loading.value = true
  try {
    const data: any = await getMonitorItems()
    monitorItems.value = data
  } catch (error) {
    ElMessage.error('加载监控列表失败')
  } finally {
    loading.value = false
  }
}

// 显示添加对话框
const showAddDialog = () => {
  addForm.value = {
    goods_url: '',
    threshold_type: 'price',
    threshold_price: 100,
    monitor_interval: 60
  }
  addDialogVisible.value = true
}

// 提交添加
const submitAdd = async () => {
  await addFormRef.value.validate()
  submitting.value = true
  
  try {
    await addMonitorItem(addForm.value)
    ElMessage.success('添加成功')
    addDialogVisible.value = false
    loadMonitorItems()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '添加失败')
  } finally {
    submitting.value = false
  }
}

// 编辑商品
const editItem = (row: any) => {
  editForm.value = {
    id: row.id,
    threshold_type: row.threshold_type,
    threshold_price: row.threshold_price,
    monitor_interval: row.monitor_interval,
    is_active: row.is_active
  }
  editDialogVisible.value = true
}

// 提交编辑
const submitEdit = async () => {
  await editFormRef.value.validate()
  submitting.value = true
  
  try {
    await updateMonitorItem(editForm.value.id, {
      threshold_type: editForm.value.threshold_type,
      threshold_price: editForm.value.threshold_price,
      monitor_interval: editForm.value.monitor_interval,
      is_active: editForm.value.is_active
    })
    ElMessage.success('更新成功')
    editDialogVisible.value = false
    loadMonitorItems()
  } catch (error) {
    ElMessage.error('更新失败')
  } finally {
    submitting.value = false
  }
}

// 删除商品
const deleteItem = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除该监控商品吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
  } catch (error) {
    // 用户取消
    return
  }
  
  try {
    await deleteMonitorItem(row.id)
    ElMessage.success('删除成功')
    loadMonitorItems()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

// 查看历史
const viewHistory = (row: any) => {
  ElMessage.info('历史价格功能开发中')
  // TODO: 跳转到历史价格页面
}

onMounted(() => {
  loadMonitorItems()
})
</script>

<style scoped>
.monitor-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
