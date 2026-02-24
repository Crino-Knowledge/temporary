<template>
  <div>
    <!--Layout布局-->
    <el-row>
      <el-col :span="24">
        <el-row :gutter="20">
          <el-col :span="3">
            <!--搜索区域-->
            <el-input
              placeholder="请输入内容"
              v-model="queryInfo.searchKey"
              clearable
              @clear="changeList"
            >
              <el-button
                slot="append"
                icon="el-icon-search"
                @click="changeList"
              ></el-button>
            </el-input>
          </el-col>
          <el-col :span="3.5">
            <span class="cf">模型名称：</span>
            <el-select
                v-model="queryInfo.modelNo"
                filterable
                remote
                clearable
                reserve-keyword
                placeholder="请输入模型名称"
                :remote-method="getSearchModelNoList"
                @change="changeList"
                :loading="loadingModel">
                <el-option
                  v-for="item in searchModelNoList"
                  :key="item.modelNo"
                  :label="item.name"
                  :value="item.modelNo">
                </el-option>
              </el-select>
          </el-col>
          <el-col :span="3.5">
            <span class="cf">任务状态：</span>
            <el-select
                v-model="queryInfo.status" clearable @change="changeList">
                <el-option
                  label="启用"
                  :value="1">
                  </el-option>
                  <el-option
                  label="停止"
                  :value="0">
                  </el-option>
              </el-select>
          </el-col>
          <el-col :span="2.5">
            <el-button type="primary" @click="openAddDialogVisible">添加</el-button>
          </el-col>
        </el-row>
      </el-col>
      <el-col :span="24">
        <!--表格-->
        <el-table
          :data="pageList"
          border
          @cell-dblclick="dbcopy"
        >
          <!-- <el-table-column type="index" label="序号" width="80" align="center"></el-table-column> -->
          <el-table-column prop="taskName" label="任务名称" fixed="left" align="center" width="150" show-overflow-tooltip></el-table-column>
          <el-table-column prop="algorithmModelName" label="模型名称" align="center" width="150"></el-table-column>
          <el-table-column prop="customerName" label="客户名称" align="center" width="150"></el-table-column>
          <el-table-column prop="streamServerUrl" label="流媒体服务器地址" align="center"  show-overflow-tooltip></el-table-column>
          <el-table-column prop="videoPlayUrl" label="原始视频" align="center" width="150" show-overflow-tooltip></el-table-column>
          <el-table-column prop="pushVideoPlayUrl" label="视频播放地址" align="center" width="150" show-overflow-tooltip></el-table-column>
          <el-table-column prop="computingVideoPlayUrl" label="实时计算地址" align="center" width="150" show-overflow-tooltip></el-table-column>
          <el-table-column prop="firstExecTime" label="首次执行时间" align="center" width="180">
            <template slot-scope="scope">
              <span>{{ parseTime(scope.row.firstExecTime) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="latestExecTime" label="最近执行时间" align="center" width="180">
            <template slot-scope="scope">
              <span>{{ parseTime(scope.row.latestExecTime) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="taskStatus" label="更新任务状态" align="center" width="150">
            <template slot-scope="scope">
              <el-button
                :type="!scope.row.taskStatus?'primary':'danger'"
                size="mini"
                @click="updateStatus(scope.row)"
              >{{ !scope.row.taskStatus?'启用':'停用' }}</el-button>
              
            </template>
          </el-table-column>
          <el-table-column prop="taskStatus" label="任务状态" align="center" width="150">
            <template slot-scope="scope">
              <span style="color:#F56C6C" v-if="scope.row.taskStatus">计算中</span>
              <span style="color:#409EFF" v-if="!scope.row.taskStatus">已停止</span>
            </template>
          </el-table-column>
          
          <el-table-column label="操作" fixed="right" min-width="150">
            <!-- 作用域插槽 -->
            <template slot-scope="scope">
              <div class="flex_row_start_center">
                  <!--修改按钮-->
                    <el-button
                      type="primary"
                      size="mini"
                      icon="el-icon-edit"
                      @click="showEditDialog(scope.row)"
                    ></el-button>
                    <!--删除按钮-->
                    <el-button
                      type="danger"
                      size="mini"
                      icon="el-icon-delete"
                      @click="deleteById(scope.row.id)"
                    ></el-button>
                    <el-button
                      type="success"
                      size="mini"
                      v-if="scope.row.taskStatus"
                      icon="el-icon-video-camera"
                      @click="openVideo(scope.row)"
                    ></el-button>
              </div>
              
            </template>
          </el-table-column>
        </el-table>
      </el-col>
    </el-row>
    <el-row>
      <!--分页区域-->
      <el-pagination
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page="queryInfo.pageNum"
        :page-sizes="[1, 2, 5, 10]"
        :page-size="queryInfo.pageSize"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
      >
      </el-pagination>
    </el-row>
    <!--添加对象的对话框-->
    <el-dialog title="添加" :visible.sync="addDialogVisible" width="30%" @close="addDialogClosed" :close-on-click-modal="false">
      <!--内容主体区域-->
      <el-form :model="addForm" label-width="140px" :rules="rules" ref="ruleForm">
        <el-form-item label="任务名称" prop="taskName">
          <el-input v-model="addForm.taskName"></el-input>
        </el-form-item>
        <el-form-item label="客户名称" prop="customerNo">
          <!-- <el-input v-model="addForm.customerNo"></el-input> -->
          <el-select
            v-model="addForm.customerNo"
            filterable
            remote
            reserve-keyword
            placeholder="请输入关键词"
            :remote-method="remoteMethodCustomerNo"
            style="width:100%"
            :loading="loadingCustomerNo">
            <el-option
              v-for="item in customerList"
              :key="item.customerNo"
              :label="item.name"
              :value="item.customerNo">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="模型名称" prop="modelNo">
          <!-- <el-input v-model="addForm.modelNo"></el-input> -->
          <el-select
            v-model="addForm.modelNo"
            filterable
            remote
            reserve-keyword
            placeholder="请输入关键词"
            :remote-method="remoteMethod"
            style="width:100%"
            @change="changeModelNo"
            :loading="loadingModelNo">
            <el-option
              v-for="item in modelNoList"
              :key="item.modelNo"
              :label="item.name"
              :value="item.modelNo">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="视频播放地址" prop="videoPlayUrl">
          <el-input v-model="addForm.videoPlayUrl"></el-input>
        </el-form-item>
        <el-form-item label="跳帧数量" prop="skipFrame">
          <div class="flex_row_start_center">
            <el-input-number v-model="addForm.skipFrame" :min="1" ></el-input-number>
          </div>
        </el-form-item>
        <el-form-item label="推送频率" prop="pushFrequency">
          <div class="flex_row_start_center">
            <el-input-number v-model="addForm.pushFrequency" :min="1" ></el-input-number>
          </div>
          
        </el-form-item>
        
      </el-form>
      <!--底部按钮区域-->
      <span slot="footer" class="dialog-footer">
        <el-button @click="addDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="addObj" :loading="isLoadding">确 定</el-button>
      </span>
    </el-dialog>
    <!--修改用户的对话框-->
    <el-dialog title="修改" :visible.sync="editDialogVisible" width="30%" :close-on-click-modal="false">
      <!--内容主体区域-->
      <el-form :model="editForm" label-width="140px" :rules="rules" ref="ruleForm">
        <el-form-item label="任务名称" prop="taskName">
          <el-input v-model="editForm.taskName"></el-input>
        </el-form-item>
        <el-form-item label="客户名称" prop="customerNo">
          <el-select
            v-model="editForm.customerNo"
            filterable
            remote
            reserve-keyword
            placeholder="请输入关键词"
            :remote-method="remoteMethodCustomerNo"
            style="width:100%"
            :loading="loadingCustomerNo">
            <el-option
              v-for="item in customerList"
              :key="item.customerNo"
              :label="item.name"
              :value="item.customerNo">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="模型名称" prop="modelNo">
          <el-select
            v-model="editForm.modelNo"
            filterable
            remote
            reserve-keyword
            placeholder="请输入关键词"
            :remote-method="remoteMethod"
            style="width:100%"
            :loading="loadingModelNo">
            <el-option
              v-for="item in modelNoList"
              :key="item.modelNo"
              :label="item.name"
              :value="item.modelNo">
            </el-option>
          </el-select>
        </el-form-item>
        
        <!-- <el-form-item label="视频信息" prop="videoBaseInfo">
          <el-input v-model="editForm.videoBaseInfo"></el-input>
        </el-form-item> -->
        <el-form-item label="视频播放地址" prop="videoPlayUrl">
          <el-input v-model="editForm.videoPlayUrl"></el-input>
        </el-form-item>
        <el-form-item label="跳帧数量" prop="skipFrame" >
          <div class="flex_row_start_center">
            <el-input-number v-model="editForm.skipFrame" :min="1" ></el-input-number>
          </div>
          
        </el-form-item>
        <el-form-item label="推送频率" prop="pushFrequency">
          <div class="flex_row_start_center">
            <el-input-number v-model="editForm.pushFrequency" :min="1" ></el-input-number>
          </div>
          
        </el-form-item>
      </el-form>
      <!--底部按钮区域-->
      <span slot="footer" class="dialog-footer">
        <el-button @click="editDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="updateObj" :loading="isLoadding">确 定</el-button>
      </span>
    </el-dialog>
    <el-dialog title="视频查看" :visible.sync="videoDialogVisible" width="70%" @close="closeVideo" :close-on-click-modal="false">
      <!--内容主体区域-->
      <div class="grid2 video-box">
        <!-- <EasyPlayer style="height: 50vh;" :video-url="videoRow.pushVideoPlayUrl" ></EasyPlayer> -->
        <player ref="pushVideoPlayUrl" style="height: 50vh;" :videoUrl="videoRow.pushVideoPlayUrl" fluent autoplay @screenshot="shot"
                      @destroy="destroyJessibuca"/>
        <player ref="computingVideoPlayUrl" style="height: 50vh;margin-left: 10px;" :videoUrl="videoRow.computingVideoPlayUrl" fluent autoplay @screenshot="shot"
                      @destroy="destroyJessibuca"/>

      </div>
      
      </el-dialog>

  </div>
</template>

<script>
import { parseTime,timestampToTime } from '@/utils/ruoyi'
//import EasyPlayer from '@easydarwin/easyplayer';
import { add, deleteById, update, getById,listPage,setAlgorithmTaskStatus} from "@/api/algorithmTask";
import { listPage as getModelNoListPage} from "@/api/algorithmModel";
import { listPage as getCustomerListPage} from "@/api/customer";
import player from '@/components/jessibuca.vue'
import Clipboard from "clipboard"
export default {
  components:{player },
  data() {
    return {
      customerList:[],
      loadingModelNo:false,
      loadingCustomerNo:false,
      modelNoList:[],
      videoRow:{
        pushVideoPlayUrl:null,
        computingVideoPlayUrl:null
      },
      videoDialogVisible:false,
      pageList: [], // 列表
      total: 0, // 总数
      // 获取列表的参数对象
      queryInfo: {
        searchKey: "", // 查询参数
        pageNum: 1, // 当前页码
        pageSize: 10, //页面大小
      },
      // 获取列表的参数对象
      queryModelInfo: {
        searchKey: "", // 查询参数
        pageNum: 1, // 当前页码
        pageSize: 20, //页面大小
      },
      queryCustomerInfo: {
        searchKey: "", // 查询参数
        pageNum: 1, // 当前页码
        pageSize: 20, //页面大小
      },
      addDialogVisible: false, //控制-添加对象对话框-是否一进页面就显示
      addForm: {
        modelNo: "",
        customerNo: "",
        videoBaseInfo: "",
        videoPlayUrl: "",
        taskName:'',
        skipFrame:1,
        pushFrequency:60
      },
      editDialogVisible: false, // 控制-修改对象对话框-是否一进页面显示
      editForm: {
        id: "",
        modelNo: "",
        customerNo: "",
        videoBaseInfo: "",
        videoPlayUrl: "",
        taskName:'',
        skipFrame:1,
        pushFrequency:60
      },
      rules:{
        modelNo:{ required: true, message: '请选择模型', trigger: 'blur' },
        customerNo:{ required: true, message: '请选择客户', trigger: 'blur' },
        videoPlayUrl:{ required: true, message: '请填写视频地址', trigger: 'blur' },
      },
      multipleSelection: [],
      ids: [],
      fileList: [],
      typelist:[{id:1,value:"吸烟"},{id:2,value:"安全帽"},{id:3,value:"人脸"}],
      isUpdate:false,
      searchModelNoList:[],
      searchModelPage:{
        searchKey: "", // 查询参数
        pageNum: 1, // 当前页码
        pageSize: 50, //页面大小
              
      },
      loadingModel:false,
      isLoadding:false
    };
  },
  created() {
    // 生命周期函数
    this.getListPage();
    this.getModelNoList()
    this.getCustomerList()
    this.getSearchModelNoList()
  },
  methods: {
    dbcopy(row, column, cell, event){
      this.handleClipboard(event)
    },
    handleClipboard(event) {
      const clipboard = new Clipboard(event.target, {
        text: () => event.target.innerText
      })
      clipboard.on('success', () => {
        this.$message({
          showClose: true,
          message: '复制成功',
          type: 'success'
        });
        clipboard.destroy()
      })
      clipboard.on('error', () => {
        this.$message({
          showClose: true,
          message: '复制失败',
          type: 'error'
        });
        clipboard.destroy()
      })
      clipboard.onClick(event)
    },
    changeModelNo(value){
      console.log("模型选择",value)
      this.modelNoList.forEach(el=>{
        if(el.modelNo === value){
          this.addForm.taskName = el.name
        }
      })
      // this.addForm.taskName = this.modelNoList[0].name
    },
    changeList(){
      this.queryInfo.pageNum = 1
      this.getListPage()
    },
    openAddDialogVisible(){
      this.addDialogVisible = true
      let user = this.$store.state.user
      this.addForm.customerNo = this.customerList[0].customerNo
      
    },
    destroyJessibuca(idx) {
        console.log(idx);
        this.clear(idx)
      },
      clear(idx) {
        let dataStr = window.localStorage.getItem('playData') || '[]'
        let data = JSON.parse(dataStr);
        data[idx - 1] = null;
        console.log(data);
        window.localStorage.setItem('playData', JSON.stringify(data))
      },
    shot(e) {
        // console.log(e)
        // send({code:'image',data:e})
        var base64ToBlob = function (code) {
          let parts = code.split(';base64,');
          let contentType = parts[0].split(':')[1];
          let raw = window.atob(parts[1]);
          let rawLength = raw.length;
          let uInt8Array = new Uint8Array(rawLength);
          for (let i = 0; i < rawLength; ++i) {
            uInt8Array[i] = raw.charCodeAt(i);
          }
          return new Blob([uInt8Array], {
            type: contentType
          });
        };
        let aLink = document.createElement('a');
        let blob = base64ToBlob(e); //new Blob([content]);
        let evt = document.createEvent("HTMLEvents");
        evt.initEvent("click", true, true); //initEvent 不加后两个参数在FF下会报错  事件类型，是否冒泡，是否阻止浏览器的默认行为
        aLink.download = '截图';
        aLink.href = URL.createObjectURL(blob);
        aLink.click();
      },
    remoteMethodCustomerNo(query){
      if(query != ''){
        this.queryCustomerInfo.searchKey = query
        this.getCustomerList()
      }
    },
    getCustomerList(){
      getCustomerListPage(this.queryCustomerInfo).then(res=>{
        this.loadingCustomerNo = false
        if (res.data.code === 200) {
            this.customerList = res.data.data.list;
        }
      }).catch(err=>{
        this.loadingCustomerNo = false
      })
    },
    // changeModelNo(row){
    //   if(row){
    //     this.addForm.customerNo = row.customerNo
    //   }else{
    //     this.addForm.customerNo = null
    //   }
    // },
    getModelNoList(){
      getModelNoListPage(this.queryModelInfo).then(res=>{
        this.loadingModelNo = false
        if (res.data.code === 200) {
            this.modelNoList = res.data.data.list;
            this.addForm.modelNo = this.modelNoList[0].modelNo
            this.addForm.taskName = this.modelNoList[0].name
        }
          
      }).catch(err=>{
        this.loadingModelNo = false
      })
    },
    getSearchModelNoList(){
      getModelNoListPage(this.searchModelPage).then(res=>{
        if (res.data.code === 200) {
            this.searchModelNoList = res.data.data.list;
        }
          
      }).catch(err=>{
        this.loadingModelNo = false
      })
    },
    remoteMethod(query){
      if(query != ''){
        this.queryModelInfo.searchKey = query
      this.getModelNoList()

      }
    },
    closeVideo(){
      console.log("关闭")
      this.videoDialogVisible=false
      this.videoRow={
        pushVideoPlayUrl:null,
        computingVideoPlayUrl:null
      }
    },
    openVideo(row){
      this.videoDialogVisible = true
      this.videoRow = {
        pushVideoPlayUrl:row.pushVideoPlayUrl,
        computingVideoPlayUrl:row.computingVideoPlayUrl
      }
      
    },
    updateStatus(row){
      const loading = this.$loading({
          lock: true,
          text: 'Loading',
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)'
        });
      let taskStatus = 0
      if(row.taskStatus==1){
        taskStatus = 0
      }else{
        taskStatus = 1
      }
      setAlgorithmTaskStatus({
        "taskNo": row.taskNo,
        "taskStatus": taskStatus
      }).then(()=>{
        loading.close();
        this.getListPage()
      }).catch(err=>{
        loading.close();
      })
    },
    //默认显示时分秒，此处传入pattern {y}-{m}-{d}即只显示年月日
    parseTime(timestamp) {
      return parseTime(timestamp,"{y}-{m}-{d} {h}:{i}:{s}");
    },
    getListPage() {
      listPage(this.queryInfo)
        .then((res) => {
          if (res.data.code === 200) {
            this.pageList = res.data.data.list;
            this.total = res.data.data.total;
          } else {
            this.$message.error(res.data.msg);
          }
        })
        .catch((err) => {
          console.log(err);
        });
    },
    // 监听 pageSize 改变的事件
    handleSizeChange(newSize) {
      // console.log(newSize)
      this.queryInfo.pageSize = newSize;
      // 重新发起请求列表
      this.getListPage();
    },
    // 监听 当前页码值 改变的事件
    handleCurrentChange(newPage) {
      // console.log(newPage)
      this.queryInfo.pageNum = newPage;
      // 重新发起请求列表
      this.getListPage();
    },
    //添加对象
    addObj() {
      this.$refs['ruleForm'].validate((valid) => {
          if (valid) {
            this.isLoadding = true
            add(this.addForm)
              .then((res) => {
                this.isLoadding = false
                if (res.data.code === 200) {
                  this.addDialogVisible = false;
                  this.getListPage();
                  this.$message({
                    message: "添加成功",
                    type: "success",
                  });
                } else {
                  this.$message.error(res.data.msg);
                }
              })
              .catch((err) => {
                this.isLoadding = false
                this.$message.error("添加异常");
                console.log(err);
              });
          }
        })
      
    },

    // 监听添加对话框的关闭事件
    addDialogClosed() {
      // 表单内容重置为空
      this.$refs.ruleForm.resetFields();
    },

    // 监听修改状态
    showEditDialog(obj) {
      this.editDialogVisible = true;
      //console.log("请求后接收到的响应结果:"+obj);
      this.editForm = obj;
      this.queryCustomerInfo.searchKey = this.editForm.name
        this.getCustomerList()
        this.queryModelInfo.searchKey = this.editForm.name
      this.getModelNoList()
    },
    //修改
    updateObj() {
      this.$refs['ruleForm'].validate((valid) => {
          if (valid) {
            this.isLoadding = true
            update(this.editForm)
              .then((res) => {
                this.isLoadding = false
                if (res.data.code === 200) {
                  this.editDialogVisible = false;
                  this.getListPage();
                  this.$message({
                    message: "修改成功",
                    type: "success",
                  });
                } else {
                  this.$message.error(res.data.msg);
                }
              })
              .catch((err) => {
                this.isLoadding = false
                this.$message.error(err);
                console.loge(err);
              });
          }
        })
      
    },
    // 根据ID删除对应的信息
    async deleteById(id) {
      // 弹框 询问用户是否删除
      const confirmResult = await this.$confirm(
        "此操作将永久删除该数据, 是否继续?",
        "提示",
        {
          confirmButtonText: "确定",
          cancelButtonText: "取消",
          type: "warning",
        }
      ).catch((err) => err);
      // 如果用户确认删除，则返回值为字符串 confirm
      // 如果用户取消删除，则返回值为字符串 cancel
      // console.log(confirmResult)
      if (confirmResult == "confirm") {
        //删除
        deleteById(id)
          .then((res) => {
            if (res.data.code === 200) {
              this.getListPage();
              this.$message({
                message: "删除成功",
                type: "success",
              });
            } else {
              this.$message.error(res.data.msg);
            }
          })
          .catch((err) => {
            this.$message.error(err);
            console.log(err);
          });
      }
    },
  },
};
</script>

<style>

.play-img{
  cursor: pointer;
}
.el-row {
  margin-bottom: 20px;
}
.el-col {
  border-radius: 4px;
}
/* .el-card {
  box-shadow: 0 1px 1px rgba(0, 0, 0, 0.1) !important;
  height: 60pt;
} */
</style>
<style scoped>
.video-box{
  width: 100%;
}
.grid2{
  display: grid;
  grid-template-columns: 1fr 1fr;
}
</style>
