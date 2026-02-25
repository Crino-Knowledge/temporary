<template>
  <div class="dashboard-content">
    <!-- 统计卡片行 -->
    <div class="stats-row">
      <div class="stat-card" style="--card-color: #667eea;">
        <div class="stat-icon">
          <i class="el-icon-box"></i>
        </div>
        <div class="stat-content">
          <span class="stat-value">18</span>
          <span class="stat-label">算法模型个数</span>
        </div>
        <div class="stat-trend">+5%</div>
      </div>
      <div class="stat-card" style="--card-color: #764ba2;">
        <div class="stat-icon">
          <i class="el-icon-coin"></i>
        </div>
        <div class="stat-content">
          <span class="stat-value">106</span>
          <span class="stat-label">计算任务总数</span>
        </div>
        <div class="stat-trend">+12%</div>
      </div>
      <div class="stat-card" style="--card-color: #f093fb;">
        <div class="stat-icon">
          <i class="el-icon-video-play"></i>
        </div>
        <div class="stat-content">
          <span class="stat-value">35</span>
          <span class="stat-label">正在运行任务</span>
        </div>
        <div class="stat-trend">+8%</div>
      </div>
      <div class="stat-card" style="--card-color: #f5576c;">
        <div class="stat-icon">
          <i class="el-icon-bell"></i>
        </div>
        <div class="stat-content">
          <span class="stat-value">3179</span>
          <span class="stat-label">历史告警次数</span>
        </div>
        <div class="stat-trend">+3%</div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="card-header">
          <div class="header-left">
            <div class="header-icon purple">
              <i class="el-icon-monitor"></i>
            </div>
            <div class="header-text">
              <h3>系统资源监控</h3>
              <p>实时性能数据</p>
            </div>
          </div>
          <span class="update-time">更新于 2026-02-23 10:30:00</span>
        </div>
        <div class="gauge-charts">
          <div class="gauge-item">
            <div id="memory-gauge" class="gauge-chart"></div>
            <span class="gauge-label">内存使用率</span>
          </div>
          <div class="gauge-item">
            <div id="cpu-gauge" class="gauge-chart"></div>
            <span class="gauge-label">CPU使用率</span>
          </div>
          <div class="gauge-item">
            <div id="gpu-gauge" class="gauge-chart"></div>
            <span class="gauge-label">GPU使用率</span>
          </div>
        </div>
      </div>

      <div class="chart-card">
        <div class="card-header">
          <div class="header-left">
            <div class="header-icon orange">
              <i class="el-icon-pie-chart"></i>
            </div>
            <div class="header-text">
              <h3>告警类型分布</h3>
              <p>近30天数据统计</p>
            </div>
          </div>
          <span class="update-time">更新于 2026-02-23 10:30:00</span>
        </div>
        <div class="pie-content">
          <div id="alarm-pie" class="pie-chart"></div>
          <div class="pie-legend">
            <div class="legend-item" v-for="(item, index) in alarmNameList" :key="item.name">
              <span class="legend-dot" :style="{background: colorList[index]}"></span>
              <span class="legend-name">{{item.name}}</span>
              <span class="legend-value">{{item.value}}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 告警列表 -->
    <div class="alarm-section">
      <div class="section-header">
        <div class="header-left">
          <div class="header-icon alarm">
            <i class="el-icon-warning"></i>
          </div>
          <div class="header-text">
            <h3>最新告警</h3>
            <p>实时告警信息</p>
          </div>
        </div>
        <el-button type="primary" plain size="small" icon="el-icon-refresh" @click="getAlarmList">
          刷新
        </el-button>
      </div>

      <div class="alarm-table">
        <div class="alarm-table-header">
          <span class="col-index">序号</span>
          <span class="col-type">告警类型</span>
          <span class="col-time">告警时间</span>
          <span class="col-customer">客户名称</span>
          <span class="col-status">状态</span>
        </div>

        <div class="alarm-item" v-for="(item, index) in alarmList" :key="item.id">
          <span class="col-index">
            <span class="index-badge" :class="{ top: index < 3 }">
              {{index < 9 ? '0' + (index + 1) : index + 1}}
            </span>
          </span>
          <span class="col-type">
            <i class="el-icon-warning-outline alarm-icon"></i>
            {{item.modelName}}
          </span>
          <span class="col-time">{{item.alarmDate}}</span>
          <span class="col-customer">{{item.customerName}}</span>
          <span class="col-status">
            <span class="status-tag" :class="{ unhandled: index < 3 }">
              {{index < 3 ? '未处理' : '已处理'}}
            </span>
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import { listPage as getAlarmListPage } from "@/api/alarmData";

export default {
  data() {
    return {
      colorList: ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe'],
      memoryGauge: null,
      cpuGauge: null,
      gpuGauge: null,
      alarmEchart: null,
      alarmList: [],
      alarmNameList: [
        { value: 1048, name: '裸土砂石告警' },
        { value: 735, name: '秸秆燃烧告警' },
        { value: 580, name: '车牌识别' },
        { value: 484, name: '河道漂浮物' },
        { value: 300, name: '城市流动摊贩' },
        { value: 200, name: '其他告警' }
      ]
    }
  },
  mounted() {
    this.initCharts();
    this.getAlarmList();
    window.addEventListener('resize', this.handleResize);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize);
    if (this.memoryGauge) this.memoryGauge.dispose();
    if (this.cpuGauge) this.cpuGauge.dispose();
    if (this.gpuGauge) this.gpuGauge.dispose();
    if (this.alarmEchart) this.alarmEchart.dispose();
  },
  methods: {
    initCharts() {
      // 内存使用率仪表盘
      this.memoryGauge = echarts.init(document.getElementById('memory-gauge'));
      this.memoryGauge.setOption({
        series: [{
          type: 'gauge',
          radius: '90%',
          startAngle: 90,
          endAngle: -270,
          pointer: { show: false },
          progress: {
            show: true,
            overlap: false,
            roundCap: true,
            clip: false,
            itemStyle: { color: '#667eea' }
          },
          axisLine: { lineStyle: { width: 12, color: [[1, '#e2e8f0']] } },
          splitLine: { show: false },
          axisTick: { show: false },
          axisLabel: { show: false },
          data: [{ value: 50, detail: { offsetCenter: ['0%', '0%'] } }],
          detail: {
            width: 60,  // 增加宽度避免文字溢出
            height: 18, // 增加高度
            fontSize: 31,  // 原28 +3
            color: '#1e293b',
            formatter: '{value}%',
            fontWeight: 'bold'
          }
        }]
      });

      // CPU使用率仪表盘
      this.cpuGauge = echarts.init(document.getElementById('cpu-gauge'));
      this.cpuGauge.setOption({
        series: [{
          type: 'gauge',
          radius: '90%',
          startAngle: 90,
          endAngle: -270,
          pointer: { show: false },
          progress: {
            show: true,
            overlap: false,
            roundCap: true,
            clip: false,
            itemStyle: { color: '#764ba2' }
          },
          axisLine: { lineStyle: { width: 12, color: [[1, '#e2e8f0']] } },
          splitLine: { show: false },
          axisTick: { show: false },
          axisLabel: { show: false },
          data: [{ value: 65, detail: { offsetCenter: ['0%', '0%'] } }],
          detail: {
            width: 60,  // 增加宽度避免文字溢出
            height: 18, // 增加高度
            fontSize: 31,  // 原28 +3
            color: '#1e293b',
            formatter: '{value}%',
            fontWeight: 'bold'
          }
        }]
      });

      // GPU使用率仪表盘
      this.gpuGauge = echarts.init(document.getElementById('gpu-gauge'));
      this.gpuGauge.setOption({
        series: [{
          type: 'gauge',
          radius: '90%',
          startAngle: 90,
          endAngle: -270,
          pointer: { show: false },
          progress: {
            show: true,
            overlap: false,
            roundCap: true,
            clip: false,
            itemStyle: { color: '#f093fb' }
          },
          axisLine: { lineStyle: { width: 12, color: [[1, '#e2e8f0']] } },
          splitLine: { show: false },
          axisTick: { show: false },
          axisLabel: { show: false },
          data: [{ value: 80, detail: { offsetCenter: ['0%', '0%'] } }],
          detail: {
            width: 60,  // 增加宽度避免文字溢出
            height: 18, // 增加高度
            fontSize: 31,  // 原28 +3
            color: '#1e293b',
            formatter: '{value}%',
            fontWeight: 'bold'
          }
        }]
      });

      // 告警类型饼图
      this.alarmEchart = echarts.init(document.getElementById('alarm-pie'));
      this.alarmEchart.setOption({
        tooltip: { trigger: 'item' },
        series: [{
          name: '告警类型',
          type: 'pie',
          radius: ['45%', '70%'],
          center: ['50%', '50%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 8,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: { show: false },
          emphasis: {
            label: {
              show: true,
              fontSize: 17,  // 原14 +3
              fontWeight: 'bold'
            }
          },
          labelLine: { show: false },
          data: this.alarmNameList.map((item, index) => ({
            ...item,
            itemStyle: { color: this.colorList[index] }
          }))
        }]
      });
    },
    handleResize() {
      if (this.memoryGauge) this.memoryGauge.resize();
      if (this.cpuGauge) this.cpuGauge.resize();
      if (this.gpuGauge) this.gpuGauge.resize();
      if (this.alarmEchart) this.alarmEchart.resize();
    },
    getAlarmList() {
      getAlarmListPage({
        pageNum: 1,
        pageSize: 5,
      }).then(res => {
        if (res.data.code === 200) {
          this.alarmList = res.data.data.list.slice(0, 5);
        }
      }).catch(() => {
        // 使用模拟数据
        this.alarmList = [
          { id: 1, modelName: '车牌识别异常', alarmDate: '2026-02-23 10:28:15', customerName: '万达广场停车场' },
          { id: 2, modelName: '设备离线', alarmDate: '2026-02-23 10:25:42', customerName: '国贸中心停车场' },
          { id: 3, modelName: '存储空间不足', alarmDate: '2026-02-23 10:20:18', customerName: '科技园停车场' },
          { id: 4, modelName: '网络延迟过高', alarmDate: '2026-02-23 10:15:33', customerName: '体育中心停车场' },
          { id: 5, modelName: '摄像头遮挡', alarmDate: '2026-02-23 10:10:09', customerName: '医院停车场' }
        ];
      });
    }
  }
};
</script>

<style scoped>
.dashboard-content {
  padding: 0;
}

/* 统计卡片 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: #faf8f0;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  min-height: 120px; /* 增加最小高度避免内容溢出 */
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: var(--card-color, #667eea);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  width: 60px;  /* 原56 +4 适配更大字体 */
  height: 60px; /* 原56 +4 适配更大字体 */
  border-radius: 14px;
  background: var(--card-color, #667eea);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 31px; /* 原28 +3 */
  color: #ffffff;
}

.stat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 35px; /* 原32 +3 */
  font-weight: 700;
  color: #1e293b;
  line-height: 1.1; /* 调整行高避免溢出 */
}

.stat-label {
  font-size: 17px; /* 原14 +3 */
  color: #64748b;
  margin-top: 8px; /* 增加间距 */
}

.stat-trend {
  font-size: 16px; /* 原13 +3 */
  color: #10b981;
  font-weight: 600;
  white-space: nowrap; /* 防止换行 */
}

/* 图表区域 */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.chart-card {
  background: #faf8f0;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px; /* 增加间距 */
  flex-wrap: wrap; /* 防止小屏幕下重叠 */
  gap: 10px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px; /* 增加间距 */
}

.header-icon {
  width: 48px; /* 原44 +4 适配更大字体 */
  height: 48px; /* 原44 +4 适配更大字体 */
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 25px; /* 原22 +3 */
  color: #ffffff;
}

.header-icon.purple {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header-icon.orange {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.header-icon.alarm {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
}

.header-text h3 {
  font-size: 21px; /* 原18 +3 */
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 6px 0; /* 增加间距 */
}

.header-text p {
  font-size: 16px; /* 原13 +3 */
  color: #94a3b8;
  margin: 0;
}

.update-time {
  font-size: 15px; /* 原12 +3 */
  color: #94a3b8;
  white-space: nowrap; /* 防止换行 */
}

/* 仪表盘 */
.gauge-charts {
  display: flex;
  justify-content: space-around;
  padding: 20px 0;
  flex-wrap: wrap; /* 响应式适配 */
  gap: 20px;
}

.gauge-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 160px; /* 增加最小宽度 */
}

.gauge-chart {
  width: 150px; /* 原140 +10 适配更大字体 */
  height: 150px; /* 原140 +10 适配更大字体 */
}

.gauge-label {
  font-size: 16px; /* 原13 +3 */
  color: #64748b;
  margin-top: 15px; /* 增加间距 */
  white-space: nowrap;
}

/* 饼图 */
.pie-content {
  display: flex;
  align-items: center;
  gap: 28px; /* 增加间距 */
  flex-wrap: wrap; /* 响应式适配 */
  justify-content: center;
}

.pie-chart {
  width: 210px; /* 原200 +10 适配更大字体 */
  height: 210px; /* 原200 +10 适配更大字体 */
}

.pie-legend {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 15px; /* 原12 +3 */
  min-width: 200px; /* 增加最小宽度 */
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 12px; /* 原10 +2 */
  font-size: 16px; /* 原13 +3 */
}

.legend-dot {
  width: 14px; /* 原12 +2 */
  height: 14px; /* 原12 +2 */
  border-radius: 4px; /* 原3 +1 */
}

.legend-name {
  color: #64748b;
  flex: 1;
}

.legend-value {
  color: #1e293b;
  font-weight: 600;
  white-space: nowrap;
}

/* 告警列表 */
.alarm-section {
  background: #faf8f0;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px; /* 原20 +4 */
  flex-wrap: wrap; /* 防止小屏幕下重叠 */
  gap: 10px;
}

.alarm-table {
  border: 1px solid #f1f5f9;
  border-radius: 12px;
  overflow: hidden;
}

.alarm-table-header {
  display: grid;
  grid-template-columns: 90px 2fr 1.5fr 1.5fr 110px; /* 增加列宽 */
  gap: 20px; /* 原16 +4 */
  padding: 16px 20px; /* 原14 +2 */
  background: #f8fafc;
  font-size: 16px; /* 原13 +3 */
  font-weight: 600;
  color: #64748b;
}

.alarm-item {
  display: grid;
  grid-template-columns: 90px 2fr 1.5fr 1.5fr 110px; /* 增加列宽 */
  gap: 20px; /* 原16 +4 */
  padding: 16px 20px; /* 原14 +2 */
  border-top: 1px solid #f1f5f9;
  font-size: 17px; /* 原14 +3 */
  align-items: center;
  color: #475569;
}

.alarm-item:hover {
  background: #f8fafc;
}

.index-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px; /* 原28 +4 */
  height: 32px; /* 原28 +4 */
  background: #f1f5f9;
  border-radius: 8px;
  font-size: 16px; /* 原13 +3 */
  font-weight: 600;
  color: #64748b;
}

.index-badge.top {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
  color: #ffffff;
}

.alarm-icon {
  color: #f59e0b;
  margin-right: 6px; /* 原4 +2 */
  font-size: 18px; /* 增加图标大小 */
}

.status-tag {
  display: inline-flex;
  align-items: center;
  padding: 6px 14px; /* 原4+2, 12+2 */
  border-radius: 20px;
  font-size: 15px; /* 原12 +3 */
  font-weight: 500;
  background: #dcfce7;
  color: #166534;
  white-space: nowrap;
}

.status-tag.unhandled {
  background: #fee2e2;
  color: #991b1b;
}

@media (max-width: 1200px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: 1fr;
  }
  .alarm-table-header,
  .alarm-item {
    grid-template-columns: 70px 1.5fr 1fr 90px; /* 调整移动端列宽 */
    gap: 15px;
  }
  .col-customer {
    display: none;
  }
  .gauge-item {
    min-width: 140px;
  }
  .gauge-chart {
    width: 140px;
    height: 140px;
  }
  .pie-chart {
    width: 180px;
    height: 180px;
  }
}

@media (max-width: 480px) {
  .stat-card {
    padding: 20px;
    flex-direction: column;
    text-align: center;
  }
  .stat-trend {
    margin-top: 10px;
  }
  .header-left {
    flex-direction: column;
    text-align: center;
  }
  .header-text {
    text-align: center;
  }
}
</style>
