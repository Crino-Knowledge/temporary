<template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="page-icon orange">
          <i class="el-icon-cpu"></i>
        </div>
        <div class="page-title">
          <h2>计算任务管理</h2>
          <p>管理算法计算任务</p>
        </div>
      </div>
      <button class="add-btn" @click="openAddDialogVisible">
        <i class="el-icon-plus"></i> 新建任务
      </button>
    </div>

    <!-- 搜索区域 -->
    <div class="search-section">
      <div class="search-row">
        <div class="search-box">
          <i class="el-icon-search search-icon"></i>
          <el-input
            v-model="queryInfo.searchKey"
            placeholder="搜索任务名称..."
            clearable
            @clear="changeList"
            @keyup.enter.native="changeList"
            class="search-input"
          />
          <button class="search-btn" @click="changeList">搜索</button>
        </div>
        <div class="filter-item">
          <span class="filter-label">模型名称：</span>
          <el-select
            v-model="queryInfo.modelNo"
            filterable
            remote
            clearable
            reserve-keyword
            placeholder="请输入模型名称"
            :remote-method="getSearchModelNoList"
            @change="changeList"
            :loading="loadingModel"
            class="filter-select">
            <el-option
              v-for="item in searchModelNoList"
              :key="item.modelNo"
              :label="item.name"
              :value="item.modelNo">
            </el-option>
          </el-select>
        </div>
        <div class="filter-item">
          <span class="filter-label">任务状态：</span>
          <el-select
            v-model="queryInfo.status"
            clearable
            @change="changeList"
            class="filter-select">
            <el-option label="启用" :value="1"></el-option>
            <el-option label="停止" :value="0"></el-option>
          </el-select>
        </div>
      </div>
    </div>

    <!-- 表格区域 -->
    <div class="table-section">
      <div class="table-header">
        <span class="table-title">任务列表</span>
        <span class="table-count">共 {{ total }} 条记录</span>
      </div>

      <div class="custom-table">
        <el-table :data="pageList" style="width: 100%" @cell-dblclick="dbcopy">
          <el-table-column type="index" label="序号" width="80" align="center">
            <template slot-scope="scope">
              <span class="index-badge">{{ scope.$index + 1 }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="taskName" label="任务名称" min-width="150" show-overflow-tooltip></el-table-column>
          <el-table-column prop="algorithmModelName" label="模型名称" min-width="120"></el-table-column>
          <el-table-column prop="customerName" label="客户名称" min-width="120"></el-table-column>
          <el-table-column prop="streamServerUrl" label="流媒体服务器地址" min-width="180" show-overflow-tooltip></el-table-column>
          <el-table-column prop="videoPlayUrl" label="原始视频" min-width="150" show-overflow-tooltip></el-table-column>
          <el-table-column prop="pushVideoPlayUrl" label="视频播放地址" min-width="150" show-overflow-tooltip></el-table-column>
          <el-table-column prop="computingVideoPlayUrl" label="实时计算地址" min-width="150" show-overflow-tooltip></el-table-column>
          <el-table-column prop="firstExecTime" label="首次执行时间" min-width="150">
            <template slot-scope="scope">
              <span>{{ parseTime(scope.row.firstExecTime) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="latestExecTime" label="最近执行时间" min-width="150">
            <template slot-scope="scope">
              <span>{{ parseTime(scope.row.latestExecTime) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="taskStatus" label="更新任务状态" width="120" align="center">
            <template slot-scope="scope">
              <el-button
                :type="!scope.row.taskStatus?'primary':'danger'"
                size="mini"
                @click="updateStatus(scope.row)">
                {{ !scope.row.taskStatus?'启用':'停用' }}
              </el-button>
            </template>
          </el-table-column>
          <el-table-column prop="taskStatus" label="任务状态" width="100" align="center">
            <template slot-scope="scope">
              <span class="status-tag" :class="scope.row.taskStatus ? 'status-running' : 'status-inactive'">
                {{ scope.row.taskStatus ? '运行中' : '已停止' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="操作" fixed="right" width="120" align="center">
            <template slot-scope="scope">
              <div class="action-btns">
                <button class="action-icon edit" @click="showEditDialog(scope.row)">
                  <i class="el-icon-edit"></i>
                </button>
                <button class="action-icon delete" @click="deleteById(scope.row.id)">
                  <i class="el-icon-delete"></i>
                </button>
                <button class="action-icon video" v-if="scope.row.taskStatus" @click="openVideo(scope.row)">
                  <i class="el-icon-video-camera"></i>
                </button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="queryInfo.pageNum"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="queryInfo.pageSize"
          layout="total, sizes, prev, pager, next"
          :total="total"
          background>
        </el-pagination>
      </div>
    </div>
    <!--添加对象的对话框-->
    <el-dialog title="添加" :visible.sync="addDialogVisible" width="30%" @close="addDialogClosed" :close-on-click-modal="false">
      <!--内容主体区域-->
      <el-form :model="addForm" label-width="110px" :rules="rules" ref="ruleForm">
        <el-form-item label="任务名称" prop="taskName">
          <el-input v-model="addForm.taskName"></el-input>
        </el-form-item>
        <el-form-item label="客户名称" prop="customerNo">
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
      <el-form :model="editForm" label-width="110px" :rules="rules" ref="ruleForm">
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
      pageList: [],
      total: 0,
      queryInfo: {
        searchKey: "",
        pageNum: 1,
        pageSize: 10,
      },
      queryModelInfo: {
        searchKey: "",
        pageNum: 1,
        pageSize: 20,
      },
      queryCustomerInfo: {
        searchKey: "",
        pageNum: 1,
        pageSize: 20,
      },
      addDialogVisible: false,
      addForm: {
        modelNo: "",
        customerNo: "",
        videoBaseInfo: "",
        videoPlayUrl: "",
        taskName:'',
        skipFrame:1,
        pushFrequency:60
      },
      editDialogVisible: false,
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
        searchKey: "",
        pageNum: 1,
        pageSize: 50,          
      },
      loadingModel:false,
      isLoadding:false
    };
  },
  created() {
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
        let blob = base64ToBlob(e);
        let evt = document.createEvent("HTMLEvents");
        evt.initEvent("click", true, true);
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
    handleSizeChange(newSize) {
      this.queryInfo.pageSize = newSize;
      this.getListPage();
    },
    handleCurrentChange(newPage) {
      this.queryInfo.pageNum = newPage;
      this.getListPage();
    },
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
    addDialogClosed() {
      this.$refs.ruleForm.resetFields();
    },
    showEditDialog(obj) {
      this.editDialogVisible = true;
      this.editForm = obj;
      this.queryCustomerInfo.searchKey = this.editForm.name
        this.getCustomerList()
        this.queryModelInfo.searchKey = this.editForm.name
      this.getModelNoList()
    },
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
    async deleteById(id) {
      const confirmResult = await this.$confirm(
        "此操作将永久删除该数据, 是否继续?",
        "提示",
        {
          confirmButtonText: "确定",
          cancelButtonText: "取消",
          type: "warning",
        }
      ).catch((err) => err);
      if (confirmResult == "confirm") {
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

<style scoped>
/* 页面容器 */
.page-container {
  padding: 0;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 31px;
  color: #ffffff;
}

.page-icon.orange {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.page-title h2 {
  font-size: 27px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.page-title p {
  font-size: 17px;
  color: #94a3b8;
  margin: 0;
}

.add-btn {
  height: 44px;
  padding: 0 24px;
  border-radius: 12px;
  font-size: 17px;
  font-weight: 500;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.add-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

/* 搜索区域 */
.search-section {
  background: #faf8f0;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.search-row {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #f8fafc;
  border-radius: 12px;
  padding: 4px;
  border: 2px solid #e2e8f0;
  transition: all 0.3s ease;
  max-width: 400px;
  flex: 1;
}

.search-box:focus-within {
  border-color: #667eea;
  background: #ffffff;
}

.search-icon {
  font-size: 21px;
  color: #94a3b8;
  margin-left: 12px;
}

.search-input {
  flex: 1;
}

.search-input >>> .el-input__inner {
  border: none;
  background: transparent;
  height: 40px;
  font-size: 17px;
  color: #1e293b;
}

.search-btn {
  height: 40px;
  padding: 0 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  border: none;
  border-radius: 10px;
  font-size: 17px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.search-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 17px;
  color: #64748b;
  font-weight: 500;
}

.filter-select {
  width: 180px;
}

/* 表格区域 */
.table-section {
  background: #faf8f0;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.table-title {
  font-size: 21px;
  font-weight: 600;
  color: #1e293b;
}

.table-count {
  color: #94a3b8;
  font-size: 16px;
}

.custom-table >>> .el-table {
  background: transparent;
}

.custom-table >>> .el-table th {
  background: #f8fafc;
  color: #64748b;
  font-weight: 600;
  font-size: 16px;
}

.custom-table >>> .el-table td {
  font-size: 17px;
  color: #475569;
}

.custom-table >>> .el-table--enable-row-hover .el-table__body tr:hover > td {
  background: #f8fafc;
}

.index-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: #f1f5f9;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #64748b;
}

.status-tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 15px;
  font-weight: 500;
}

.status-active {
  background: #dcfce7;
  color: #166534;
}

.status-inactive {
  background: #fee2e2;
  color: #991b1b;
}

.status-running {
  background: #dbeafe;
  color: #1e40af;
}

.status-pending {
  background: #fef3c7;
  color: #92400e;
}

.action-btns {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.action-icon {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 17px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-icon.edit {
  background: #dbeafe;
  color: #2563eb;
}

.action-icon.edit:hover {
  background: #2563eb;
  color: #ffffff;
}

.action-icon.delete {
  background: #fee2e2;
  color: #dc2626;
}

.action-icon.delete:hover {
  background: #dc2626;
  color: #ffffff;
}

.action-icon.video {
  background: #dcfce7;
  color: #16a34a;
}

.action-icon.video:hover {
  background: #16a34a;
  color: #ffffff;
}

/* 分页 */
.pagination-wrapper {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

/* 视频弹窗 */
.video-box {
  width: 100%;
}

.grid2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
}

.play-img {
  cursor: pointer;
}

.flex_row_start_center{
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 100%;
}
</style>

<!-- 全局放大Element UI组件内置文字 -->
<style>
.el-pagination, .el-dialog, .el-form, .el-descriptions {
  font-size: 17px !important;
}
.el-descriptions-item__label, .el-descriptions-item__content {
  font-size: 17px !important;
}
.el-dialog__title {
  font-size: 20px !important;
}
.el-form-item__label, .el-input__inner, .el-button {
  font-size: 17px !important;
}
.el-date-picker {
  font-size: 17px !important;
}
</style>
