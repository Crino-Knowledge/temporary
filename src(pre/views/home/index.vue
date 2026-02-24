<template>
  <div class="home-content">
      <div class="tab-list-box flex_row_start_center">
          <div class="tab-list" v-for="item in tabList" :key="item.title">
              <div class="flex_column_center_start cf list-box">
                <span class="tab-list-num mb fs40">{{item.num}}</span>
                <span class="tab-list-text fs16 cBBBCBD">{{item.title}}</span>
              </div>
          </div>
      </div>
      <div class="home-bottom-box flex_row_start_start">
        <div class="home-bottom-left flex_column_start_start">
            <div class="memory-information">
              <div id="memory-info"></div>
              <div class="memory-title-box flex_row_start_center">
                <span class="memory-line"></span>
                <span class="memory-title cf ml10">内存信息</span>
              </div>
              <span class="memory-time">2024.09.29 17:20:00更新</span>
            </div>
            <div class="memory-information flex_row_between_center">
              <div class="memory-title-box flex_row_start_center">
                <span class="memory-line"></span>
                <span class="memory-title cf ml10">CPU/GPU信息</span>
              </div>
              <span class="memory-time">2024.09.29 17:20:00更新</span>
              <!-- <div class="flex_row_between_center cf memory-time">
                <span>2024.09.29 17:20:00更新</span>
                <span>2024.09.29 17:20:00更新</span>
              </div> -->
              <div class="cpu-information" id="cpu-info"></div>
              <div class="gpu-information" id="gpu-info"></div>
            </div>
        </div>
        <div class="home-bottom-center">
            <div class="memory-title-box flex_row_start_center">
                  <span class="memory-line"></span>
                  <span class="memory-title cf ml10">近一月告警占比</span>
            </div>
            <span class="memory-time-center">2024.09.29 17:20:00更新</span>
            <div id="alarm-pie"></div>
            <div class="flex_column_start_start legend-box">
              <div class="flex_row_start_center mb10" v-for="(item,index) in alarmNameList" :key="item.name">
                <span class="alarm-color mr10" :style="{backgroundColor:colorList[index]}"></span>
                <span class="alarm-name mr10">{{item.name}}</span>
                <span class="alarm-num mr10">{{item.value}}</span>
                <span class="alarm-num"></span>
              </div>
            </div>
        </div>
        <div class="home-bottom-right">
            <div class="memory-title-box flex_row_start_center">
                  <span class="memory-line"></span>
                  <span class="memory-title cf ml10">告警信息</span>
            </div>
            <div class="flex_row_start_center alarm-list-title">
              <span>序号</span>
              <span>告警类型</span>
              <span>告警时间</span>
              <span>客户名称</span>
            </div>
            <div class="flex_row_start_center alarm-list" v-for="(item,index) in alarmList" :key="item.id">
              <span>{{index<9?'0'+(index+1):index+1}}</span>
              <span>{{item.modelName}}</span>
              <span>{{item.alarmDate}}</span>
              <span>{{item.customerName}}</span>
            </div>
        </div>
      </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import { listPage as getAlarmListPage} from "@/api/alarmData";
export default {
  data() {
    return {
        colorList:['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272'],
        memoryInfoEchart:null,
        cpuInfoEchart:null,
        gpuInfoEchart:null,
        alarmEchart:null,
        tabList: [
          {
            title: "算法模型个数",
            num: "18",
            url: "../../assets/home/bg1@2x.png",
          },
          {
            title: "计算任务总数",
            num: "106",
            url: "../../assets/home/bg2@2x.png",
          },
          {
            title: "正在运行任务数量",
            num: "35",
            url: "../../assets/home/bg3@2x.png",
          },
          {
            title: "历史告警次数",
            num: "3179",
            url: "../../assets/home/bg4@2x.png",
          },
        ],
        alarmList:[],
        alarmNameList:[ { value: 1048, name: '裸土砂石告警' },
              { value: 735, name: '秸秆燃烧告警' },
              { value: 580, name: '车牌识别' },
              { value: 484, name: '河道漂浮物' },
              { value: 300, name: '城市流动摊贩' },
              { value: 200, name: '其他告警' }]
    }
  },
  mounted(){
    this.memoryInfoEchart = echarts.init(document.getElementById("memory-info"));
    this.cpuInfoEchart = echarts.init(document.getElementById("cpu-info"));
    this.gpuInfoEchart = echarts.init(document.getElementById("gpu-info")); 
    this.alarmEchart = echarts.init(document.getElementById("alarm-pie")); 
    this.initMemoryInforEchart()
    this.initCpuInforEchart()
    this.initGpuInforEchart()
    this.initAlarmEchart()
    this.getAlarmList()
  },
  methods:{
    initMemoryInforEchart(){
      this.memoryInfoEchart.setOption({
        tooltip: {
            formatter: '{a} <br/>{b} : {c}%'
          },
          series: [
            {
              name: '',
              type: 'gauge',
              pointer:{
                show: false
              },
              detail: {
                show:true,
                color: '#ffffff',
                fontFamily:"DIN",
                fontSize:40,
                lineHeight:100,
                backgroundColor:{
                  type: 'radial',
                    x: 0.5,
                    y: 0.5,
                    r: 0.5,
                    colorStops: [{
                        offset: 0.7, color: '#1D2029' // 0% 处的颜色
                    }, {
                        offset: 1, color: '#212C4A' // 100% 处的颜色
                    }],
                    global: false // 缺省为 false
                  },
                valueAnimation: true,
                formatter: '{value}%',
                width:130,
                height:140,  
                borderRadius:150,
                borderWidth:1,
                borderColor:'#212C4A',
                offsetCenter:['0','0'],
              },
              progress:{
                show: true,
                roundCap:true,
                itemStyle:{
                  color: '#4660FF',
                  // shadowColor: 'rgba(0,138,255,0.45)',
                  
                }
              },
              axisLine:{
                show: true,
                roundCap:true,
                lineStyle:{
                  color: [[1,'#363947']],
                  // shadowColor: 'rgba(0,138,255,0.45)',
                  
                }
              },
              axisLabel:{
                show:false
              },
              data: [
                {
                  value: 50,
                  name: '内存占用率',
                  title:{
                    show:true,
                    color: '#BBBCBD',
                    fontSize: 16,
                    offsetCenter:['0','100%'],
                  }
                }
              ]
            }
          ]
        });
    },
    initCpuInforEchart(){
      this.cpuInfoEchart.setOption({
        tooltip: {
            formatter: '{a} <br/>{b} : {c}%'
          },
          series: [
            {
              name: '',
              type: 'gauge',
              pointer:{
                show: false
              },
              detail: {
                show:true,
                color: '#ffffff',
                fontFamily:"DIN",
                fontSize:40,
                lineHeight:100,
                backgroundColor:{
                  type: 'radial',
                    x: 0.5,
                    y: 0.5,
                    r: 0.5,
                    colorStops: [{
                        offset: 0.7, color: '#1D2029' // 0% 处的颜色
                    }, {
                        offset: 1, color: '#212C4A' // 100% 处的颜色
                    }],
                    global: false // 缺省为 false
                  },
                valueAnimation: true,
                formatter: '{value}%',
                width:100,
                height:110,  
                borderRadius:150,
                borderWidth:1,
                borderColor:'#212C4A',
                offsetCenter:['0','0'],
              },
              progress:{
                show: true,
                roundCap:true,
                itemStyle:{
                  color: {
                    type: 'linear',
                    x: 0,
                    y: 0,
                    colorStops: [{
                        offset: 0.3, color: '#457FFF' // 0% 处的颜色
                    }, 
                    {
                        offset: .6, color: '#21B9D9' // 100% 处的颜色
                    },
                    {
                        offset: 1, color: '#ED5D11' // 100% 处的颜色
                    }
                  ],
                  },
                }
              },
              axisLine:{
                show: true,
                roundCap:true,
                lineStyle:{
                  color: [[1,'#363947']],
                }
              },
              axisLabel:{
                show:false
              },
              data: [
                {
                  value: 50,
                  name: 'CPU内存占用率',
                  title:{
                    show:true,
                    color: '#BBBCBD',
                    fontSize: 16,
                    offsetCenter:['0','100%'],
                  }
                }
              ]
            }
          ]
        });
    },
    initGpuInforEchart(){
      this.gpuInfoEchart.setOption({
        tooltip: {
            formatter: '{a} <br/>{b} : {c}%'
          },
          series: [
            {
              name: '',
              type: 'gauge',
              pointer:{
                show: false
              },
              detail: {
                show:true,
                color: '#ffffff',
                fontFamily:"DIN",
                fontSize:40,
                lineHeight:100,
                backgroundColor:{
                  type: 'radial',
                    x: 0.5,
                    y: 0.5,
                    r: 0.5,
                    colorStops: [{
                        offset: 0.7, color: '#1D2029' // 0% 处的颜色
                    }, {
                        offset: 1, color: '#212C4A' // 100% 处的颜色
                    }],
                    global: false // 缺省为 false
                  },
                valueAnimation: true,
                formatter: '{value}%',
                width:100,
                height:110,  
                borderRadius:150,
                borderWidth:1,
                borderColor:'#212C4A',
                offsetCenter:['0','0'],
              },
              progress:{
                show: true,
                roundCap:true,
                itemStyle:{
                  color: {
                    type: 'linear',
                    x: 0,
                    y: 0,
                    colorStops: [{
                        offset: 0.3, color: '#457FFF' // 0% 处的颜色
                    }, 
                    {
                        offset: .6, color: '#21B9D9' // 100% 处的颜色
                    },
                    {
                        offset: 1, color: '#ED5D11' // 100% 处的颜色
                    }
                  ],
                  },
                }
              },
              axisLine:{
                show: true,
                roundCap:true,
                lineStyle:{
                  color: [[1,'#363947']],
                  // shadowColor: 'rgba(0,138,255,0.45)',
                  
                }
              },
              axisLabel:{
                show:false
              },
              data: [
                {
                  value: 90,
                  name: 'GPU内存占用率',
                  title:{
                    show:true,
                    color: '#BBBCBD',
                    fontSize: 16,
                    offsetCenter:['0','100%'],
                  }
                }
              ]
            }
          ]
        });
    },
    initAlarmEchart(){
      this.alarmEchart.setOption({
        tooltip: {
          show:true,
          trigger: 'item'
        },
        legend: {
          show:false,
          bottom: 0,
          left: 'center',
          orient:"vertical",
          itemGap:20,
          textStyle :{
            color:"#7D7E81"
          },
          formatter: '{name}'
        },
        title:{
          text:"3347",
          textStyle:{
            color:"#ffffff",
            fontSize:40,
            fontFamily:"DIN"
          },         
          subtext:"告警总次数",
          subtextStyle:{
            color:"#7D7E81",
            fontSize:16,
          },
          left: 'center',
          top: 'center',

        },
       
        series: [
          {
            name: '告警总次数',
            type: 'pie',
            radius: ['50%', '72%'],
            avoidLabelOverlap: false,
            label: {
              show: false,
              position: 'center'
            },
            labelLine: {
              show: false
            },
            data: [
              { value: 1048, name: '裸土砂石告警' },
              { value: 735, name: '秸秆燃烧告警' },
              { value: 580, name: '车牌识别' },
              { value: 484, name: '河道漂浮物' },
              { value: 300, name: '城市流动摊贩' },
              { value: 200, name: '其他告警' }
            ]
          },
           // 外边框虚线
            {
              name:"外边框",
              type: 'pie',
              zlevel: 4,
              // silent: true,
              hoverAnimation: false, //鼠标移入变大
              radius: ['78%', '72%'], // 外层圆环半径
              center: ['50%', '50%'], // 控制外层圆环位置，和内层一致即可
              // 禁用外层圆环 label 样式
              label: {
                normal: {
                  show: false
                }
              },
              tooltip: {
                show:false
              },
              labelLine: {
                normal: {
                  show: false
                }
              },
              // 自定义外层圆环数据
              data: [{
                value: 1,
                itemStyle:{
                  color:"#34373F",
                }
                
              }]
            },
             // 内边框虚线
             {
              name:"外边框",
              type: 'pie',
              zlevel: 4,
              // silent: true,
              hoverAnimation: false, //鼠标移入变大
              radius: ['43%', '50%'], // 外层圆环半径
              center: ['50%', '50%'], // 控制外层圆环位置，和内层一致即可
              // 禁用外层圆环 label 样式
              label: {
                normal: {
                  show: false
                }
              },
              tooltip: {
                show:false
              },
              labelLine: {
                normal: {
                  show: false
                }
              },
              // 自定义外层圆环数据
              data: [{
                value: 1,
                itemStyle:{
                  color:"#292B34",
                }
                
              }]
            }
        ]
      })
    },
    getAlarmList(){
      getAlarmListPage({
        pageNum: 1, // 当前页码
        pageSize: 20, //页面大小
      }).then(res=>{
        this.loadingTable = false
          if (res.data.code === 200) {
            this.alarmList = res.data.data.list;
          }
      })
    }
  }
};
</script>
<style scoped>
.legend-box{
  position: absolute;
  left: 50%;
  bottom: 15%;
  transform: translateX(-50%);
}
.alarm-name{
  color: #78797D;
}
.alarm-num{
  color:#B4B4B6;
}
.alarm-color{
  width: 16px;
  height: 16px;
  background: #4378F3;
  border-radius: 1px;
}
.tab-list{
  width: 400px;
  height: 180px;
  margin-right: 24px;
  position: relative;
}
.tab-list:nth-child(1){
  background: url('../../assets/home/bg1@2x.png') no-repeat;
  background-size: 100% 100%;
}
.tab-list:nth-child(2){
  background: url('../../assets/home/bg2@2x.png') no-repeat;
  background-size: 100% 100%;
}
.tab-list:nth-child(3){
  background: url('../../assets/home/bg3@2x.png') no-repeat;
  background-size: 100% 100%;
}
.tab-list:nth-child(4){
  background: url('../../assets/home/bg4@2x.png') no-repeat;
  background-size: 100% 100%;
}
.tab-list-num{
  font-family: 'DIN';
}
.list-box{
  position: absolute;
  left: 40px;
  top: 50%;
  transform: translateY(-50%);
}
.home-bottom-box{
  margin-top: 24px;
}
.memory-information{
  width: 510px;
  height: 362px;
  background: #1D2029;
  border-radius: 2px;
  margin-bottom: 24px;
  position: relative;
}
.memory-title-box{
  position: absolute;
  left: 20px;
  top: 20px;
}
.memory-line{
  width: 3px;
  height: 16px;
  background: #4378F3;
  border-radius: 2px;
}
.memory-time{
  color: #78797D;
  position: absolute;
  left: 50%;
  bottom: 20px;
  transform: translateX(-50%);
  font-size: 16px;
}
.memory-time-center{
  color: #78797D;
  position: absolute;
  right: 20px;
  top: 20px;
  font-size: 16px;
}
.memory-information:last-child{
  margin-bottom: 0;
}
.home-bottom-center{
  width: 560px;
  height: 748px;
  /* height: 100%; */
  border-radius: 2px;
  background: #1D2029;
  margin: 0 24px;
  position: relative;
}
.home-bottom-right{
  width: 554px;
  height: 748px;
  /* height: 100%; */
  border-radius: 2px;
  background: #1D2029;
  position: relative;
  overflow: hidden;
}
.cpu-information,.gpu-information{
  width: 400px;
  height: 300px;
}
#memory-info{
  width: 400px;
  height: 300px;
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translateX(-50%) translateY(-50%);
}
#alarm-pie{
  width: 400px;
  height: 400px;
  position: absolute;
  left: 50%;
  top: 5%;
  transform: translateX(-50%);
}
.alarm-list-title{
  width: 95%;
  height: 30px;
  background: #303441;
  color: #BBBCBD;
  font-size: 14px;
  margin: 0 auto;
  margin-top: 10%;
  display: grid;
  grid-template-columns: 80px 1fr 1fr 1fr;
}
.alarm-list{
  width: 95%;
  height: 50px;
  border-bottom: 1px dotted #303441;
  color: #BBBCBD;
  font-size: 14px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 80px 1fr 1fr 1fr;
}
</style>
