<template>
  <div class="page-container">
    <!-- 页面头部 - 对齐告警中心样式 -->
    <div class="page-header">
      <div class="header-content">
        <div class="page-icon purple">
          <i class="el-icon-s-promotion"></i>
        </div>
        <div class="page-title">
          <h2>推送日志</h2>
          <p>查看消息推送记录</p>
        </div>
      </div>
    </div>

    <!-- 搜索区域 - 重构为告警中心样式 -->
    <div class="search-section">
      <div class="search-content">
        <div class="search-box">
          <i class="el-icon-search search-icon"></i>
          <el-input
            placeholder="请输入内容"
            v-model="queryInfo.searchKey"
            clearable
            @clear="getListPage"
            class="search-input"
          >
          </el-input>
          <button class="search-btn" @click="getListPage">搜索</button>
        </div>
        
        <div class="customer-select">
          <span class="cf">客户名称：</span>
          <el-select
            v-model="queryInfo.customerNo"
            filterable
            remote
            reserve-keyword
            placeholder="请输入客户名称"
            @change="changeTypeList"
            :remote-method="remoteMethodCustomerNo"
            :loading="loadingCustomerNo"
            class="select-input"
          >
            <el-option
              v-for="item in customerList"
              :key="item.customerNo"
              :label="item.name"
              :value="item.customerNo"
            >
            </el-option>
          </el-select>
        </div>
      </div>
    </div>

    <!-- 表格区域 -->
    <div class="table-section">
      <div class="table-header">
        <span class="table-title">推送记录</span>
        <span class="table-count">共 {{ total }} 条记录</span>
      </div>

      <div class="custom-table">
        <el-table
          :data="pageList"
          border
          @cell-dblclick="dbcopy"
          style="width: 100%"
          v-loading="loadingTable"
        >
          <el-table-column type="index" label="序号" width="80" align="center">
            <template slot-scope="scope">
              <span class="index-badge">{{ scope.$index + 1 }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="pushDate" label="推送时间" align="center" width="180"></el-table-column>
          <el-table-column prop="status" label="推送状态" align="center" width="100">
            <template slot-scope="scope">
              <span class="status-tag" :class="scope.row.status ? 'status-active' : 'status-inactive'">
                {{ scope.row.status ? '成功' : '失败' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="latestData" label="是否最新数据" align="center">
            <template slot-scope="scope">
              <span class="status-tag" :class="scope.row.latestData ? 'status-running' : 'status-pending'">
                {{ scope.row.latestData ? '是' : '不是' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="httpReqUrl" label="请求地址" align="center" show-overflow-tooltip></el-table-column>
          <el-table-column prop="httpReqHeader" label="请求头" align="center"></el-table-column>
          <el-table-column prop="httpReqParam" label="请求参数" align="center" show-overflow-tooltip></el-table-column>
          <el-table-column prop="httpResult" label="返回结果" align="center" show-overflow-tooltip></el-table-column>
          <el-table-column prop="errorMsg" label="错误信息" align="center" show-overflow-tooltip></el-table-column>
          <el-table-column prop="taskNo" label="任务号" align="center"></el-table-column>
          <el-table-column prop="modelName" label="模型名称" align="center"></el-table-column>
          <el-table-column prop="customerName" label="客户名称" align="center"></el-table-column>
          <el-table-column label="操作" fixed="right" width="100" align="center">
            <!-- 作用域插槽 -->
            <template slot-scope="scope">
              <div class="action-btns">
                <button class="action-icon edit" @click="pushLog(scope.row)" title="推送">
                  <i class="el-icon-send"></i>
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
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          background
        >
        </el-pagination>
      </div>
    </div>
  </div>
</template>

<script>
import { parseTime } from '@/utils/ruoyi'
import { deleteById, getById, listPage, againPushLog } from "@/api/httpPushLog";
import { listPage as getCustomerListPage } from "@/api/customer";
import Clipboard from "clipboard"

export default {
  data() {
    return {
      pageList: [], // 列表
      total: 0, // 总数
      loadingTable: false, // 表格加载状态
      // 获取列表的参数对象
      queryInfo: {
        searchKey: "", // 查询参数
        pageNum: 1, // 当前页码
        pageSize: 10, //页面大小
        customerNo: "" // 客户编号
      },
      addDialogVisible: false, //控制-添加对象对话框-是否一进页面就显示
      editDialogVisible: false, // 控制-修改对象对话框-是否一进页面显示
      multipleSelection: [],
      ids: [],
      fileList: [],
      typelist: [{ id: 1, value: "吸烟" }, { id: 2, value: "安全帽" }, { id: 3, value: "人脸" }],
      customerList: [],
      loadingCustomerNo: false,
      isLoaddingLog: false, // 推送加载状态
      queryCustomerInfo: {
        searchKey: "", // 查询参数
        pageNum: 1, // 当前页码
        pageSize: 50, //页面大小
      },
    };
  },
  created() {
    // 生命周期函数
    this.getCustomerList()
  },
  methods: {
    dbcopy(row, column, cell, event) {
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
    changeTypeList() {
      this.queryInfo.pageNum = 1;
      // 重新发起请求列表
      this.getListPage();
    },
    getCustomerList() {
      this.loadingCustomerNo = true
      getCustomerListPage(this.queryCustomerInfo).then(res => {
        this.loadingCustomerNo = false
        if (res.data.code === 200) {
          this.customerList = res.data.data.list;
          if (this.customerList.length > 0) {
            this.queryInfo.customerNo = this.customerList[0].customerNo
          }
          this.getListPage();
        }
      }).catch(err => {
        this.loadingCustomerNo = false
      })
    },
    remoteMethodCustomerNo(query) {
      if (query != '') {
        this.queryCustomerInfo.searchKey = query
        this.getCustomerList()
      }
    },
    pushLog(row) {
      this.isLoaddingLog = true
      againPushLog({
        httpPushLogId: row.id
      }).then(res => {
        this.isLoaddingLog = false
        if (res.data.code === 200) {
          this.$message.success('推送成功');
          this.getListPage(); // 推送成功后刷新列表
        }
      }).catch(err => {
        this.isLoaddingLog = false
        this.$message.error('推送失败');
      })
    },
    //默认显示时分秒，此处传入pattern {y}-{m}-{d}即只显示年月日
    parseTime(timestamp) {
      return parseTime(timestamp, "{y}-{m}-{d} {h}:{i}:{s}");
    },
    getListPage() {
      this.loadingTable = true
      listPage(this.queryInfo)
        .then((res) => {
          this.loadingTable = false
          if (res.data.code === 200) {
            this.pageList = res.data.data.list;
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
      this.queryInfo.pageSize = newSize;
      // 重新发起请求列表
      this.getListPage();
    },
    // 监听 当前页码值 改变的事件
    handleCurrentChange(newPage) {
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
  font-size: 31px;
  color: #ffffff;
}

.page-icon.purple {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
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

/* 搜索区域 */
.search-section {
  background: #faf8f0;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.search-content {
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

.customer-select {
  display: flex;
  align-items: center;
  gap: 8px;
}

.customer-select .cf {
  font-size: 17px;
  color: #1e293b;
  font-weight: 500;
}

.select-input >>> .el-select__wrapper {
  height: 40px;
  font-size: 17px;
  border-radius: 10px;
  border: 2px solid #e2e8f0;
}

.select-input >>> .el-input__inner {
  font-size: 17px;
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
  font-size: 17px !important;
}
.el-descriptions-item__label, .el-descriptions-item__content {
  font-size: 17px !important;
}
.el-dialog__title {
  font-size: 20px !important;
}
.el-form-item__label, .el-input__inner, .el-button, .el-select {
  font-size: 17px !important;
}
.el-date-picker {
  font-size: 17px !important;
}
</style>
