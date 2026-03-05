<template>
  <div class="home">
    <el-container>
      <el-header class="header">
        <h1>rPPG实时心率监测系统</h1>
        <p>基于深度学习的非接触式心率监测解决方案</p>
      </el-header>
      
      <el-main class="main">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card class="feature-card">
              <div class="card-icon">
                <el-icon size="48" color="#409eff">
                  <VideoCamera />
                </el-icon>
              </div>
              <h3>实时监测</h3>
              <p>通过摄像头实时监测心率变化，无需接触设备</p>
              <el-button type="primary" @click="$router.push('/monitoring')">
                开始监测
              </el-button>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card class="feature-card">
              <div class="card-icon">
                <el-icon size="48" color="#67c23a">
                  <DataAnalysis />
                </el-icon>
              </div>
              <h3>数据分析</h3>
              <p>提供详细的心率趋势分析和BVP信号可视化</p>
              <el-button type="success" @click="$router.push('/history')">
                查看历史
              </el-button>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card class="feature-card">
              <div class="card-icon">
                <el-icon size="48" color="#e6a23c">
                  <Setting />
                </el-icon>
              </div>
              <h3>系统设置</h3>
              <p>灵活配置监测参数和系统选项</p>
              <el-button type="warning" @click="$router.push('/settings')">
                系统设置
              </el-button>
            </el-card>
          </el-col>
        </el-row>
        
        <el-row :gutter="20" class="mt-20">
          <el-col :span="12">
            <el-card>
              <template #header>
                <span>系统状态</span>
              </template>
              <div class="status-list">
                <div class="status-item">
                  <span class="status-label">后端服务:</span>
                  <span class="status-value" :class="{ 'status-online': systemStatus.backend, 'status-offline': !systemStatus.backend }">
                    {{ systemStatus.backend ? '在线' : '离线' }}
                  </span>
                </div>
                <div class="status-item">
                  <span class="status-label">模型加载:</span>
                  <span class="status-value" :class="{ 'status-online': systemStatus.model, 'status-offline': !systemStatus.model }">
                    {{ systemStatus.model ? '就绪' : '未加载' }}
                  </span>
                </div>
                <div class="status-item">
                  <span class="status-label">活跃会话:</span>
                  <span class="status-value">{{ systemStatus.activeSessions || 0 }}</span>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="12">
            <el-card>
              <template #header>
                <span>快速开始</span>
              </template>
              <div class="quick-start">
                <ol>
                  <li>确保摄像头可用且光线充足</li>
                  <li>点击"开始监测"进入监测页面</li>
                  <li>允许浏览器访问摄像头</li>
                  <li>将面部对准摄像头中心</li>
                  <li>等待系统稳定显示心率数据</li>
                </ol>
                <el-button type="primary" @click="$router.push('/monitoring')" class="mt-10">
                  立即开始
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
        
        <!-- HTTPS安全提示 -->
        <el-row :gutter="20" class="mt-20">
          <el-col :span="24">
            <el-alert
              title="⚠️ 重要提示：摄像头访问要求"
              type="warning"
              :closable="false"
              show-icon
            >
              <template #default>
                <div class="security-notice">
                  <p><strong>为了保护用户隐私，现代浏览器要求在安全环境下才能访问摄像头：</strong></p>
                  <ul>
                    <li>✅ <strong>本地访问</strong>：localhost 或 127.0.0.1 可以直接使用</li>
                    <li>⚠️ <strong>网络访问</strong>：需要使用 HTTPS 协议</li>
                    <li>🔒 <strong>解决方案</strong>：如果无法访问摄像头，请联系管理员配置 HTTPS 证书</li>
                  </ul>
                  <p class="mt-10">
                    <el-tag type="info" size="small">当前访问地址：{{ currentUrl }}</el-tag>
                    <el-tag :type="isSecureAccess ? 'success' : 'warning'" size="small" class="ml-10">
                      {{ isSecureAccess ? '✅ 安全访问' : '⚠️ 需要HTTPS' }}
                    </el-tag>
                  </p>
                </div>
              </template>
            </el-alert>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import { VideoCamera, DataAnalysis, Setting } from '@element-plus/icons-vue'

export default {
  name: 'Home',
  components: {
    VideoCamera,
    DataAnalysis,
    Setting
  },
  setup() {
    const store = useStore()
    const systemStatus = ref({
      backend: false,
      model: false,
      activeSessions: 0
    })

    const checkSystemStatus = async () => {
      try {
        const status = await store.dispatch('system/getSystemStatus')
        systemStatus.value = {
          backend: true,
          model: status.model_loaded,
          activeSessions: status.active_sessions
        }
      } catch (error) {
        systemStatus.value = {
          backend: false,
          model: false,
          activeSessions: 0
        }
      }
    }

    onMounted(() => {
      checkSystemStatus()
      // 每30秒检查一次系统状态
      setInterval(checkSystemStatus, 30000)
    })

    // 安全访问检查
    const currentUrl = ref(window.location.href)
    const isSecureAccess = ref(
      window.isSecureContext || 
      location.hostname === 'localhost' || 
      location.hostname === '127.0.0.1'
    )

    return {
      systemStatus,
      currentUrl,
      isSecureAccess
    }
  }
}
</script>

<style lang="scss" scoped>
.home {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  text-align: center;
  color: white;
  padding: 40px 20px;
  
  h1 {
    font-size: 2.5rem;
    margin-bottom: 10px;
    font-weight: 300;
  }
  
  p {
    font-size: 1.2rem;
    opacity: 0.9;
  }
}

.main {
  padding: 40px;
  background: white;
  border-radius: 20px 20px 0 0;
  margin-top: -20px;
  position: relative;
  z-index: 1;
}

.feature-card {
  text-align: center;
  padding: 30px 20px;
  height: 300px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  
  .card-icon {
    margin-bottom: 20px;
  }
  
  h3 {
    font-size: 1.5rem;
    margin-bottom: 15px;
    color: $text-primary;
  }
  
  p {
    color: $text-regular;
    line-height: 1.6;
    margin-bottom: 20px;
    flex-grow: 1;
  }
}

.status-list {
  .status-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid $border-color-lighter;
    
    &:last-child {
      border-bottom: none;
    }
    
    .status-label {
      font-weight: 500;
      color: $text-primary;
    }
    
    .status-value {
      font-weight: 600;
      
      &.status-online {
        color: $success-color;
      }
      
      &.status-offline {
        color: $danger-color;
      }
    }
  }
}

.quick-start {
  ol {
    padding-left: 20px;
    margin-bottom: 20px;
    
    li {
      margin-bottom: 8px;
      color: $text-regular;
      line-height: 1.5;
    }
  }
}

.mt-20 {
  margin-top: 20px;
}

.mt-10 {
  margin-top: 10px;
}
</style>
