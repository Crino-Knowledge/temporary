<template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="page-icon red">
          <i class="el-icon-bell"></i>
        </div>
        <div class="page-title">
          <h2>告警中心</h2>
          <p>查看和处理系统告警</p>
        </div>
      </div>
      <button class="add-btn" @click="addDialogVisible = true">
        <i class="el-icon-plus"></i> 告警规则
      </button>
    </div>

    <!-- 搜索区域 -->
    <div class="search-section">
      <div class="search-box">
        <i class="el-icon-search search-icon"></i>
        <el-input
          v-model="queryInfo.searchKey"
          placeholder="搜索告警内容..."
          clearable
          @clear="changeTypeList"
          @keyup.enter.native="changeTypeList"
          class="search-input"
        />
        <button class="search-btn" @click="changeTypeList">搜索</button>
      </div>
    </div>

    <!-- 表格区域 -->
    <div class="table-section">
      <div class="table-header">
        <span class="table-title">告警列表</span>
        <span class="table-count">共 {{ total }} 条记录</span>
      </div>

      <div class="custom-table">
        <el-table :data="pageList" style="width: 100%" v-loading="loadingTable">
          <el-table-column type="index" label="序号" width="80" align="center">
            <template slot-scope="scope">
              <span class="index-badge" :class="{ 'top': scope.$index < 3 }">{{ scope.$index + 1 }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="告警名称" min-width="150" align="center"></el-table-column>
          <el-table-column prop="alarmType" label="告警类型" min-width="120" align="center">
            <template slot-scope="scope">
              {{ getDitcLabel(alarmTypeList,scope.row.alarmType) }}
            </template>
          </el-table-column>
          <el-table-column prop="alarmImage" label="告警图片" min-width="100" align="center">
            <template slot-scope="scope">
              <el-image
                style="width: 30px; height: 30px"
                :src="scope.row.alarmImage"
                :preview-src-list="alarmImageList">
              </el-image>
            </template>
          </el-table-column>
          <el-table-column prop="alarmDate" label="告警时间" min-width="150" align="center"></el-table-column>
          <el-table-column prop="taskNo" label="算法任务号" min-width="120" align="center"></el-table-column>
          <el-table-column prop="modelName" label="模型名称" min-width="120" align="center"></el-table-column>
          <el-table-column prop="customerName" label="客户名称" min-width="120" align="center"></el-table-column>
          <el-table-column label="操作" fixed="right" width="120" align="center">
            <template slot-scope="scope">
              <div class="action-btns">
                <button class="action-icon edit" @click="showEditDialog(scope.row)">
                  <i class="el-icon-view"></i>
                </button>
                <button class="action-icon delete" @click="deleteById(scope.row.id)" v-if="false">
                  <i class="el-icon-delete"></i>
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
          background
        >
        </el-pagination>
      </div>
    </div>

    <!--添加对象的对话框-->
    <el-dialog title="添加" :visible.sync="addDialogVisible" width="30%" @close="addDialogClosed">
      <!--内容主体区域-->
      <el-form :model="addForm" label-width="110px">
        <el-form-item label="告警名称" prop="name">
          <el-input v-model="addForm.name"></el-input>
        </el-form-item>
        <el-form-item label="告警类型" prop="alarmType">
          <el-input v-model="addForm.alarmType"></el-input>
        </el-form-item>
        <el-form-item label="告警图片" prop="alarmImage">
          <el-input v-model="addForm.alarmImage"></el-input>
        </el-form-item>
        <el-form-item label="告警时间" prop="alarmTime">
          <el-date-picker v-model="addForm.alarmTime" type="date"
            value-format="timestamp" placeholder="选择日期" style="width: 420px">
          </el-date-picker>
        </el-form-item>
        <el-form-item label="算法任务号" prop="taskNo">
          <el-input v-model="addForm.taskNo"></el-input>
        </el-form-item>
        <el-form-item label="模型序列号" prop="modelNo">
          <el-input v-model="addForm.modelNo"></el-input>
        </el-form-item>
        <el-form-item label="模型名称" prop="algorithmModelName">
          <el-input v-model="addForm.algorithmModelName"></el-input>
        </el-form-item>
        <el-form-item label="客户号" prop="customerNo">
          <el-input v-model="addForm.customerNo"></el-input>
        </el-form-item>
        <el-form-item label="客户名称" prop="customerName">
          <el-input v-model="addForm.customerName"></el-input>
        </el-form-item>
      </el-form>
      <!--底部按钮区域-->
      <span slot="footer" class="dialog-footer">
        <el-button @click="addDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="addObj">确 定</el-button>
      </span>
    </el-dialog>

    <!--修改用户的对话框-->
    <el-dialog title="查看" :visible.sync="editDialogVisible" width="30%">
      <el-descriptions class="margin-top" title="告警内容" :column="3"  border>
        <el-descriptions-item>
          <template slot="label">
            告警名称
          </template>
          {{editForm.name}}
        </el-descriptions-item>
        <el-descriptions-item>
          <template slot="label">
            告警类型
          </template>
          {{ getDitcLabel(alarmTypeList,editForm.alarmType) }}
        </el-descriptions-item>
        <el-descriptions-item>
          <template slot="label">
            告警图片
          </template>
          <el-image
            style="width: 100px; height: 100px"
            :src="editForm.alarmImage"
            :preview-src-list="[editForm.alarmImage]">
          </el-image>
        </el-descriptions-item>
        <el-descriptions-item>
          <template slot="label">
            告警时间
          </template>
          {{parseTime(editForm.alarmTime)}}
        </el-descriptions-item>
        <el-descriptions-item>
          <template slot="label">
            客户名称
          </template>
          {{editForm.customerName}}
        </el-descriptions-item>
        <el-descriptions-item>
          <template slot="label">
            模型名称
          </template>
          {{editForm.modelName}}
        </el-descriptions-item>
        <el-descriptions-item>
          <template slot="label">
            算法任务号
          </template>
          {{editForm.taskNo}}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script>
import { parseTime } from '@/utils/ruoyi'
import { add, deleteById, update, getById,listPage} from "@/api/alarmData";
import { listPage as getCustomerListPage} from "@/api/customer";
import { listPage as getModelNoListPage} from "@/api/algorithmModel";
import { listPage as getTaskNoListPage} from "@/api/algorithmTask";
import {
  getDictById
} from "@/api/jsDict";
export default {
  data() {
    return {
      pageList: [], // 列表
      total: 0, // 总数
      // 获取列表的参数对象
      queryInfo: {
        searchKey: "", // 查询参数
        pageNum: 1, // 当前页码
        pageSize: 10, //页面大小
        alarmType:''
      },
      addDialogVisible: false, //控制-添加对象对话框-是否一进页面就显示
      addForm: {
        name: "",
        alarmType: "",
        alarmImage: "",
        alarmTime: "",
        taskNo: "",
        modelNo: "",
        algorithmModelName: "",
        customerNo: "",
        customerName: "",
      },
      editDialogVisible: false, // 控制-修改对象对话框-是否一进页面显示
      editForm: {
        id: "",
        name: "",
        alarmType: "",
        alarmImage: "",
        alarmTime: "",
        taskNo: "",
        modelNo: "",
        algorithmModelName: "",
        customerNo: "",
        customerName: "",
      },
      multipleSelection: [],
      ids: [],
      fileList: [],
      typelist:[{id:1,value:"吸烟"},{id:2,value:"安全帽"},{id:3,value:"人脸"}],
      alarmImageList:[],
      alarmTypeList:[],
      queryCustomerInfo: {
        searchKey: "", // 查询参数
        pageNum: 1, // 当前页码
        pageSize: 50, //页面大小
      },
      queryModelInfo: {
        searchKey: "", // 查询参数
        pageNum: 1, // 当前页码
        pageSize: 50, //页面大小
      },
      customerList:[],
      loadingCustomerNo:false,
      modelNoList:[],
      loadingModelNo:false,
      loadingTaskNo:false,
      taskList:[],
      loadingTable:false
    };
  },
  created() {
    // 生命周期函数
    this.getListPage();
    this.getCustomerList()
    this.getModelNoList()
    this.remoteMethodtaskNo()
    getDictById(100).then(res=>{
      if(res.data.code == 200){
        this.alarmTypeList = res.data.data.data
      }

    })
  },
  methods: {
    remoteMethodtaskNo(query){
      this.loadingTaskNo = true
      getTaskNoListPage({
        searchKey: query, // 查询参数
        pageNum: 1, // 当前页码
        pageSize: 50, //页面大小
      }).then(res=>{
        this.loadingTaskNo = false
        if(res.data.code === 200){
          this.taskList = res.data.data.list
        }
      }).catch(err=>{
        this.loadingTaskNo = false
      })
    },
    getDitcLabel(list,type){
      let name = null
      list.forEach(el=>{
        if(el.id === type){
          name = el.name
        }
      })
      return name
    },
    getModelNoList(){
      this.loadingModelNo = true
      getModelNoListPage(this.queryModelInfo).then(res=>{
        this.loadingModelNo = false
        if (res.data.code === 200) {
            this.modelNoList = res.data.data.list;
        }

      }).catch(err=>{
        this.loadingModelNo = false
      })
    },
    remoteMethodModel(query){
      this.queryModelInfo.searchKey = query
        this.getModelNoList()
    },
    getCustomerList(){
      this.loadingCustomerNo = true
      getCustomerListPage(this.queryCustomerInfo).then(res=>{
        this.loadingCustomerNo = false
        if (res.data.code === 200) {
            this.customerList = res.data.data.list;
        }
      }).catch(err=>{
        this.loadingCustomerNo = false
      })
    },
    remoteMethodCustomerNo(query){
      if(query != ''){
        this.queryCustomerInfo.searchKey = query
        this.getCustomerList()
      }
    },
    changeTypeList(){
      this.queryInfo.pageNum = 1;
      // 重新发起请求列表
      this.getListPage();
    },
    //默认显示时分秒，此处传入pattern {y}-{m}-{d}即只显示年月日
    parseTime(timestamp) {
      return parseTime(timestamp,"{y}-{m}-{d} {h}:{i}:{s}");
    },
    getListPage() {
      this.loadingTable = true
      listPage(this.queryInfo)
        .then((res) => {
          this.loadingTable = false
          if (res.data.code === 200) {
            this.alarmImageList = []
            this.pageList = res.data.data.list;
            this.pageList.forEach(element => {
              this.alarmImageList.push(element.alarmImage)
            });
            this.total = res.data.data.total;
          } else {
            this.$message.error(res.data.msg);
          }
        })
        .catch((err) => {
          this.loadingTable = false
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
      add(this.addForm)
        .then((res) => {
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
          this.$message.error("添加异常");
          console.log(err);
        });
    },

    // 监听添加对话框的关闭事件
    addDialogClosed() {
      // 表单内容重置为空
      this.$refs.addFormRef.resetFields();
    },

    // 监听修改状态
    showEditDialog(obj) {
      this.editDialogVisible = true;

      this.editForm = obj;
    },
    //修改
    updateObj() {
      update(this.editForm)
        .then((res) => {
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
          this.$message.error("修改异常");
          console.loge(err);
        });
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
            this.$message.error("删除异常");
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
  font-size: 31px; /* 原28px +3 */
  color: #ffffff;
}

.page-icon.red {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.page-title h2 {
  font-size: 27px; /* 原24px +3 */
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.page-title p {
  font-size: 17px; /* 原14px +3 */
  color: #94a3b8;
  margin: 0;
}

.add-btn {
  height: 44px;
  padding: 0 24px;
  border-radius: 12px;
  font-size: 17px; /* 原14px +3 */
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
}

.search-box:focus-within {
  border-color: #667eea;
  background: #ffffff;
}

.search-icon {
  font-size: 21px; /* 原18px +3 */
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
  font-size: 17px; /* 原14px +3 */
  color: #1e293b;
}

.search-btn {
  height: 40px;
  padding: 0 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  border: none;
  border-radius: 10px;
  font-size: 17px; /* 原14px +3 */
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.search-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
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
  font-size: 21px; /* 原18px +3 */
  font-weight: 600;
  color: #1e293b;
}

.table-count {
  color: #94a3b8;
  font-size: 16px; /* 原13px +3 */
}

.custom-table >>> .el-table {
  background: transparent;
}

.custom-table >>> .el-table th {
  background: #f8fafc;
  color: #64748b;
  font-weight: 600;
  font-size: 16px; /* 原13px +3 */
}

.custom-table >>> .el-table td {
  font-size: 17px; /* 原14px +3 */
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
  font-size: 16px; /* 原13px +3 */
  font-weight: 600;
  color: #64748b;
}

.index-badge.top {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: #ffffff;
}

.status-tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 15px; /* 原12px +3 */
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
  font-size: 17px; /* 原14px +3 */
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

/* 分页 */
.pagination-wrapper {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}
</style>

<!-- 全局放大Element UI组件内置文字 -->
<style>
.el-pagination, .el-dialog, .el-form, .el-descriptions {
  font-size: 17px !important; /* 原14px +3 */
}
.el-descriptions-item__label, .el-descriptions-item__content {
  font-size: 17px !important; /* 原14px +3 */
}
.el-dialog__title {
  font-size: 20px !important; /* 原17px +3 */
}
.el-form-item__label, .el-input__inner, .el-button {
  font-size: 17px !important; /* 原14px +3 */
}
.el-date-picker {
  font-size: 17px !important; /* 原14px +3 */
}
</style>
