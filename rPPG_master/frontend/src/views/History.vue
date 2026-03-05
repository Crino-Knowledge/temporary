<template>
  <div class="history">
    <el-container>
      <el-header class="header">
        <h2>历史记录</h2>
        <p>查看历史心率监测数据和趋势分析</p>
      </el-header>
      
      <el-main>
        <el-card>
          <template #header>
            <span>数据筛选</span>
          </template>
          
          <el-form :model="filterForm" inline>
            <el-form-item label="日期范围">
              <el-date-picker
                v-model="filterForm.dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
            
            <el-form-item label="心率范围">
              <el-input-number
                v-model="filterForm.minHR"
                placeholder="最小值"
                :min="40"
                :max="200"
              />
              <span class="mx-2">-</span>
              <el-input-number
                v-model="filterForm.maxHR"
                placeholder="最大值"
                :min="40"
                :max="200"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="loadHistoryData">
                查询
              </el-button>
              <el-button @click="resetFilter">
                重置
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
        
        <el-card class="mt-20">
          <template #header>
            <span>心率趋势图</span>
          </template>
          
          <div class="chart-container">
            <Line
              v-if="chartData.labels.length > 0"
              :data="chartData"
              :options="chartOptions"
              height="300"
            />
            <div v-else class="no-data">
              <el-empty description="暂无数据" />
            </div>
          </div>
        </el-card>
        
        <el-card class="mt-20">
          <template #header>
            <span>详细记录</span>
          </template>
          
          <el-table
            :data="historyData"
            stripe
            height="400"
            v-loading="loading"
          >
            <el-table-column prop="timestamp" label="时间" width="180">
              <template #default="scope">
                {{ formatTime(scope.row.timestamp) }}
              </template>
            </el-table-column>
            
            <el-table-column prop="heart_rate" label="心率(BPM)" width="120">
              <template #default="scope">
                <span :class="getHeartRateClass(scope.row.heart_rate)">
                  {{ scope.row.heart_rate }}
                </span>
              </template>
            </el-table-column>
            
            <el-table-column prop="signal_quality" label="信号质量" width="120">
              <template #default="scope">
                <el-progress
                  :percentage="scope.row.signal_quality"
                  :color="getSignalQualityColor(scope.row.signal_quality)"
                  :show-text="false"
                />
                <span class="ml-2">{{ scope.row.signal_quality }}%</span>
              </template>
            </el-table-column>
            
            <el-table-column prop="duration" label="监测时长" width="120">
              <template #default="scope">
                {{ formatDuration(scope.row.duration) }}
              </template>
            </el-table-column>
            
            <el-table-column prop="frames_processed" label="处理帧数" width="120" />
            
            <el-table-column label="操作" width="120">
              <template #default="scope">
                <el-button
                  size="small"
                  @click="viewDetail(scope.row)"
                >
                  详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="pagination-container">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="total"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </el-card>
      </el-main>
    </el-container>
    
    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="监测详情"
      width="800px"
    >
      <div v-if="selectedRecord">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="监测时间">
            {{ formatTime(selectedRecord.timestamp) }}
          </el-descriptions-item>
          <el-descriptions-item label="心率">
            {{ selectedRecord.heart_rate }} BPM
          </el-descriptions-item>
          <el-descriptions-item label="信号质量">
            {{ selectedRecord.signal_quality }}%
          </el-descriptions-item>
          <el-descriptions-item label="监测时长">
            {{ formatDuration(selectedRecord.duration) }}
          </el-descriptions-item>
          <el-descriptions-item label="处理帧数">
            {{ selectedRecord.frames_processed }}
          </el-descriptions-item>
          <el-descriptions-item label="平均处理时间">
            {{ selectedRecord.avg_processing_time?.toFixed(2) || 'N/A' }} ms
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="mt-20">
          <h4>BVP信号</h4>
          <div class="bvp-chart">
            <Line
              v-if="selectedRecord.bvp_signal && selectedRecord.bvp_signal.length > 0"
              :data="bvpChartData"
              :options="bvpChartOptions"
              height="200"
            />
            <div v-else class="no-data">
              <el-empty description="无BVP信号数据" />
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import dayjs from 'dayjs'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

export default {
  name: 'History',
  components: {
    Line
  },
  setup() {
    const loading = ref(false)
    const historyData = ref([])
    const currentPage = ref(1)
    const pageSize = ref(20)
    const total = ref(0)
    const detailDialogVisible = ref(false)
    const selectedRecord = ref(null)
    
    const filterForm = reactive({
      dateRange: [],
      minHR: null,
      maxHR: null
    })
    
    const chartData = ref({
      labels: [],
      datasets: [{
        label: '心率 (BPM)',
        data: [],
        borderColor: '#409eff',
        backgroundColor: 'rgba(64, 158, 255, 0.1)',
        tension: 0.4
      }]
    })
    
    const chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top'
        },
        title: {
          display: true,
          text: '心率变化趋势'
        }
      },
      scales: {
        y: {
          beginAtZero: false,
          min: 40,
          max: 200
        }
      }
    }
    
    const bvpChartData = computed(() => {
      if (!selectedRecord.value?.bvp_signal) {
        return { labels: [], datasets: [] }
      }
      
      const signal = selectedRecord.value.bvp_signal
      const labels = Array.from({ length: signal.length }, (_, i) => i)
      
      return {
        labels,
        datasets: [{
          label: 'BVP信号',
          data: signal,
          borderColor: '#67c23a',
          backgroundColor: 'rgba(103, 194, 58, 0.1)',
          tension: 0.4
        }]
      }
    })
    
    const bvpChartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top'
        },
        title: {
          display: true,
          text: 'BVP信号波形'
        }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
    
    const loadHistoryData = async () => {
      loading.value = true
      try {
        // 模拟数据加载
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // 生成模拟数据
        const mockData = generateMockData()
        historyData.value = mockData
        total.value = mockData.length
        
        // 更新图表数据
        updateChartData(mockData)
      } catch (error) {
        console.error('加载历史数据失败:', error)
      } finally {
        loading.value = false
      }
    }
    
    const generateMockData = () => {
      const data = []
      const now = dayjs()
      
      for (let i = 0; i < 50; i++) {
        const timestamp = now.subtract(i * 30, 'minute')
        data.push({
          id: i + 1,
          timestamp: timestamp.toDate(),
          heart_rate: Math.floor(Math.random() * 40) + 60, // 60-100 BPM
          signal_quality: Math.floor(Math.random() * 30) + 70, // 70-100%
          duration: Math.floor(Math.random() * 1800) + 300, // 5-35分钟
          frames_processed: Math.floor(Math.random() * 1000) + 500,
          avg_processing_time: Math.random() * 50 + 20,
          bvp_signal: Array.from({ length: 100 }, () => Math.random() * 2 - 1)
        })
      }
      
      return data
    }
    
    const updateChartData = (data) => {
      const sortedData = data.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
      
      chartData.value.labels = sortedData.map(item => 
        dayjs(item.timestamp).format('MM-DD HH:mm')
      )
      chartData.value.datasets[0].data = sortedData.map(item => item.heart_rate)
    }
    
    const resetFilter = () => {
      filterForm.dateRange = []
      filterForm.minHR = null
      filterForm.maxHR = null
      loadHistoryData()
    }
    
    const handleSizeChange = (val) => {
      pageSize.value = val
      currentPage.value = 1
      loadHistoryData()
    }
    
    const handleCurrentChange = (val) => {
      currentPage.value = val
      loadHistoryData()
    }
    
    const viewDetail = (record) => {
      selectedRecord.value = record
      detailDialogVisible.value = true
    }
    
    const formatTime = (timestamp) => {
      return dayjs(timestamp).format('YYYY-MM-DD HH:mm:ss')
    }
    
    const formatDuration = (seconds) => {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}分${remainingSeconds}秒`
    }
    
    const getHeartRateClass = (hr) => {
      if (hr < 60) return 'text-warning'
      if (hr > 100) return 'text-danger'
      return 'text-success'
    }
    
    const getSignalQualityColor = (quality) => {
      if (quality >= 90) return '#67c23a'
      if (quality >= 80) return '#e6a23c'
      return '#f56c6c'
    }
    
    onMounted(() => {
      loadHistoryData()
    })
    
    return {
      loading,
      historyData,
      currentPage,
      pageSize,
      total,
      filterForm,
      chartData,
      chartOptions,
      detailDialogVisible,
      selectedRecord,
      bvpChartData,
      bvpChartOptions,
      loadHistoryData,
      resetFilter,
      handleSizeChange,
      handleCurrentChange,
      viewDetail,
      formatTime,
      formatDuration,
      getHeartRateClass,
      getSignalQualityColor
    }
  }
}
</script>

<style lang="scss" scoped>
.history {
  min-height: 100vh;
  padding: 20px;
  overflow-y: auto;
}

.history :deep(.el-main) {
  padding: 0;
  overflow: visible;
}

.header {
  text-align: center;
  margin-bottom: 30px;
  
  h2 {
    color: $text-primary;
    margin-bottom: 10px;
  }
  
  p {
    color: $text-regular;
  }
}

.chart-container {
  height: 300px;
  position: relative;
}

.no-data {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bvp-chart {
  height: 200px;
  position: relative;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.mt-20 {
  margin-top: 20px;
}

.mx-2 {
  margin: 0 8px;
}

.ml-2 {
  margin-left: 8px;
}

.text-warning {
  color: $warning-color;
}

.text-danger {
  color: $danger-color;
}

.text-success {
  color: $success-color;
}
</style>
