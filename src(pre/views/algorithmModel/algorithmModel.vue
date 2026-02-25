<template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="page-icon green">
          <i class="el-icon-box"></i>
        </div>
        <div class="page-title">
          <h2>算法模型管理</h2>
          <p>管理系统算法模型配置</p>
        </div>
      </div>
      <button class="add-btn" @click="addDialogVisible = true">
        <i class="el-icon-plus"></i> 添加模型
      </button>
    </div>

    <!-- 搜索区域 -->
    <div class="search-section">
      <div class="search-box">
        <i class="el-icon-search search-icon"></i>
        <el-input
          v-model="queryInfo.searchKey"
          placeholder="搜索模型名称..."
          clearable
          @clear="getListPage"
          @keyup.enter.native="getListPage"
          class="search-input"
        />
        <button class="search-btn" @click="getListPage">搜索</button>
      </div>
    </div>

    <!-- 表格区域 -->
    <div class="table-section">
      <div class="table-header">
        <span class="table-title">模型列表</span>
        <span class="table-count">共 {{ total }} 条记录</span>
      </div>

      <div class="custom-table">
        <el-table :data="pageList" style="width: 100%">
          <el-table-column type="index" label="序号" width="80" align="center">
            <template slot-scope="scope">
              <span class="index-badge">{{ scope.$index + 1 }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="模型名称" min-width="150"></el-table-column>
          <el-table-column prop="modelKey" label="模型键" min-width="120"></el-table-column>
          <el-table-column prop="modelNo" label="模型序列号" min-width="150" show-overflow-tooltip></el-table-column>
          <el-table-column prop="algorithmType" label="算法类型" min-width="120">
            <template slot-scope="scope">
              <span v-for="dict in typelist" :key="dict.id">
                {{ scope.row.algorithmType == dict.id ? dict.name : '' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="coreTech" label="核心技术" min-width="120"></el-table-column>
          <el-table-column prop="latestTrainingTime" label="最近训练时间" min-width="140">
            <template slot-scope="scope">
              <span>{{ parseTime(scope.row.latestTrainingTime) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template slot-scope="scope">
              <span class="status-tag" :class="scope.row.status ? 'status-active' : 'status-inactive'">
                {{ scope.row.status ? '运行中' : '已停用' }}
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
    <el-dialog title="添加" :visible.sync="addDialogVisible" width="30%" @close="addDialogClosed" :close-on-click-modal="false">
      <!--内容主体区域-->
      <el-form :model="addForm" label-width="110px">
        <el-form-item label="模型名称" prop="name">
          <el-input v-model="addForm.name"></el-input>
        </el-form-item>
        <el-form-item label="模型键" prop="modelKey">
          <el-input v-model="addForm.modelKey"></el-input>
        </el-form-item>
        <el-form-item label="算法类型" prop="algorithmType">
          <el-select v-model="addForm.algorithmType" placeholder="请选择算法类型" clearable size="medium" style="width: 100%;">
              <el-option v-for="dict in typelist" :key="dict.id" :label="dict.name" :value="dict.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="核心技术" prop="coreTech">
          <el-input v-model="addForm.coreTech"></el-input>
        </el-form-item>
        <el-form-item label="最近训练时间" prop="latestTrainingTime">
          <el-date-picker v-model="addForm.latestTrainingTime" type="date" 
            value-format="timestamp" placeholder="选择日期" style="width: 100%">
          </el-date-picker>
        </el-form-item>
        <el-form-item label="上线时间" prop="onlineTime">
          <el-date-picker v-model="addForm.onlineTime" type="date" 
            value-format="timestamp" placeholder="选择日期" style="width: 100%">
          </el-date-picker>
        </el-form-item>
        <el-form-item label="标签列表" prop="labelList">
          <el-input v-model="addForm.labelList"></el-input>
        </el-form-item>
        <el-form-item label="脚本键" prop="shellKey">
          <el-input v-model="addForm.shellKey"></el-input>
        </el-form-item>
        <el-form-item label="排序号" prop="orderNum">
          <el-input v-model="addForm.orderNum"></el-input>
        </el-form-item>
        <el-form-item label="文件上传" required>
          <el-upload class="flex_column_start_start" action="1" :on-preview="handlePreview" :multiple="false"
            :limit="1" accept="*" :auto-upload="false" :on-remove="handleRemove" :on-change="handleChange"
            :before-remove="beforeRemove" :on-exceed="handleExceed" :file-list="fileList">
          <el-button size="small" type="primary">点击上传</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <!--底部按钮区域-->
      <span slot="footer" class="dialog-footer">
        <el-button @click="addDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="addObj">确 定</el-button>
      </span>
    </el-dialog>
    <!--修改用户的对话框-->
    <el-dialog title="修改" :visible.sync="editDialogVisible" width="30%" :close-on-click-modal="false">
      <!--内容主体区域-->
      <el-form :model="editForm" label-width="110px">
        <el-form-item label="模型名称" prop="name">
          <el-input v-model="editForm.name"></el-input>
        </el-form-item>
        <el-form-item label="模型键" prop="modelKey">
          <el-input v-model="editForm.modelKey"></el-input>
        </el-form-item>
        <el-form-item label="算法类型" prop="algorithmType">
          <el-select v-model="editForm.algorithmType" placeholder="请选择算法类型" clearable size="medium" style="width: 100%">
              <el-option v-for="dict in typelist" :key="dict.id" :label="dict.name" :value="dict.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="核心技术" prop="coreTech">
          <el-input v-model="editForm.coreTech"></el-input>
        </el-form-item>
        <el-form-item label="最近训练时间" prop="latestTrainingTime">
          <el-date-picker v-model="editForm.latestTrainingTime" type="date" 
            value-format="timestamp" placeholder="选择日期" style="width: 100%">
          </el-date-picker>
        </el-form-item>
        <el-form-item label="上线时间" prop="onlineTime">
          <el-date-picker v-model="editForm.onlineTime" type="date" 
            value-format="timestamp" placeholder="选择日期" style="width: 100%">
          </el-date-picker>
        </el-form-item>
        <el-form-item label="标签列表" prop="labelList">
          <el-input v-model="editForm.labelList"></el-input>
        </el-form-item>
        <el-form-item label="脚本键" prop="shellKey">
          <el-input v-model="editForm.shellKey"></el-input>
        </el-form-item>
        <el-form-item label="排序号" prop="orderNum">
          <div class="flex_row_start_center">
              <el-input-number v-model="editForm.orderNum" style="width: 160px" controls-position="right" :min="0" />
          </div>
        </el-form-item>
        <el-form-item label="状态" prop="status" >
          <div class="flex_row_start_center" style="width: 100%;height:40px;">
              <el-radio-group v-model="editForm.status">
                <el-radio :label="1">启用</el-radio>
                <el-radio :label="0">停用</el-radio>
              </el-radio-group>
          </div>
          
        </el-form-item>
        <el-form-item label="文件上传" required>
          <el-upload class="flex_column_start_start" action="1" :on-preview="handlePreview" :multiple="false"
            :limit="1" accept="*" :auto-upload="false" :on-remove="handleRemove" :on-change="handleChange"
            :before-remove="beforeRemove" :on-exceed="handleExceed" :file-list="fileList">
          <el-button size="small" type="primary">点击上传</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <!--底部按钮区域-->
      <span slot="footer" class="dialog-footer">
        <el-button @click="editDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="updateObj">确 定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { parseTime } from '@/utils/ruoyi'
import { add, deleteById, update, getById,listPage} from "@/api/algorithmModel";
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
      },
      addDialogVisible: false, //控制-添加对象对话框-是否一进页面就显示
      addForm: {
        name: "",
        modelKey: "",
        algorithmType: "",
        coreTech: "",
        latestTrainingTime: "",
        onlineTime: "",
        labelList: "",
        targetFileData: "",
        shellKey:'',
        orderNum:''
      },
      editDialogVisible: false, // 控制-修改对象对话框-是否一进页面显示
      editForm: {
        id: "",
        name: "",
        modelKey: "",
        algorithmType: "",
        coreTech: "",
        latestTrainingTime: "",
        onlineTime: "",
        labelList: "",
        orderNum: "",
        status: "",
        targetFileData: "",
        shellKey:'',
      },
      multipleSelection: [],
      ids: [],
      fileList: [],
      typelist:[]
    };
  },
  created() {
    // 生命周期函数
    this.getListPage();
    getDictById(100).then(res=>{
      if(res.data.code == 200){
        this.typelist = res.data.data.data
      }
      
    })
  },
  methods: {
    //默认显示时分秒，此处传入pattern {y}-{m}-{d}即只显示年月日
    parseTime(timestamp) {
         return parseTime(timestamp,"{y}-{m}-{d}");
    },
    handleChange (file, fileList) {
      console.log(file, fileList, 'success');
      this.targetFileData = file.raw
    },
    handleRemove (file, fileList) {
      console.log(file, fileList);
    },
    handlePreview (file) {
      console.log(file);
    },
    handleExceed (files, fileList) {
      this.$message.warning(`您已添加了一个文件，如需替换，请先删除已添加的文件！`);
    },
    beforeRemove (file, fileList) {
      return this.$confirm(`确定移除？`);
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
      let formData = new FormData();
      for (let key in this.addForm) {
        formData.append(key, this.addForm[key]);
      }
      formData.append("targetFile", this.targetFileData);
      add(formData)
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
      //console.log("请求后接收到的响应结果:"+obj);
      this.editForm = obj;
    },
    //修改
    updateObj() {
      let formData = new FormData();
      for (let key in this.editForm) {
        formData.append(key, this.editForm[key]);
      }
      formData.append("targetFile", this.targetFileData);
      update(formData)
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

.page-icon.green {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.page-icon.orange {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.page-icon.red {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.page-icon.purple {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
}

.page-icon.cyan {
  background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
}

.page-icon.pink {
  background: linear-gradient(135deg, #ec4899 0%, #db2777 100%);
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
.el-pagination, .el-dialog, .el-form, .el-select, .el-upload {
  font-size: 17px !important; /* 原14px +3 */
}
.el-form-item__label, .el-input__inner, .el-button, .el-date-picker {
  font-size: 17px !important; /* 原14px +3 */
}
.el-dialog__title {
  font-size: 20px !important; /* 原17px +3 */
}
.el-radio, .el-input-number {
  font-size: 17px !important; /* 原14px +3 */
}
.el-option {
  font-size: 17px !important; /* 原14px +3 */
}
</style>
