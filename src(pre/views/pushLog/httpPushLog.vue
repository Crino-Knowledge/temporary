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
              @clear="getListPage"
            >
              <el-button
                slot="append"
                icon="el-icon-search"
                @click="getListPage"
              ></el-button>
            </el-input>
          </el-col>
          <el-col :span="3.5">
            <span class="cf">客户名称：</span>
            <el-select
            v-model="queryInfo.customerNo"
            filterable
            remote
            reserve-keyword
            placeholder="请输入客户名称"
            @change="changeTypeList"
            :remote-method="remoteMethodCustomerNo"
            :loading="loadingCustomerNo">
            <el-option
              v-for="item in customerList"
              :key="item.customerNo"
              :label="item.name"
              :value="item.customerNo">
            </el-option>
          </el-select>
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
          <el-table-column type="index" label="序号" width="80" align="center"></el-table-column>
          <el-table-column prop="pushDate" label="推送时间" align="center" width="180"></el-table-column>
          <el-table-column prop="status" label="推送状态" align="center" width="100">
            <template slot-scope="scope" >
              <span class="tag-js" v-if="scope.row.status">
                  {{scope.row.status?'成功':'失败'}}
              </span>
              <span class="tag-js" v-if="!scope.row.status">
                  {{scope.row.status?'成功':'失败'}}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="latestData" label="是否最新数据" align="center">
            <template slot-scope="scope">
              <span class="tag-js" v-if="scope.row.latestData">
                  {{scope.row.latestData?'是':'不是'}}
              </span>
              <span class="tag-js" v-if="!scope.row.latestData">
                  {{scope.row.latestData?'是':'不是'}}
              </span>
            </template>
          </el-table-column>
          <!-- <el-table-column prop="methodName" label="方法名称" align="center"></el-table-column> -->
          <el-table-column prop="httpReqUrl" label="请求地址" align="center" show-overflow-tooltip></el-table-column>
          <el-table-column prop="httpReqHeader" label="请求头" align="center" ></el-table-column>
          <el-table-column prop="httpReqParam" label="请求参数" align="center" show-overflow-tooltip></el-table-column>
          <el-table-column prop="httpResult" label="返回结果" align="center" show-overflow-tooltip></el-table-column>
          <el-table-column prop="errorMsg" label="错误信息" align="center" show-overflow-tooltip></el-table-column>
          <el-table-column prop="taskNo" label="任务号" align="center" ></el-table-column>
          <el-table-column prop="modelName" label="模型名称" align="center" ></el-table-column>
          <el-table-column prop="customerName" label="客户名称" align="center"></el-table-column>
          <el-table-column label="操作" fixed="right" width="200">
            <!-- 作用域插槽 -->
            <template slot-scope="scope">
              <!--修改按钮-->
              <el-button
                type="success"
                size="mini"
                @click="pushLog(scope.row)"
              >推送</el-button>
              <el-button
              v-if="false"
                type="primary"
                size="mini"
                icon="el-icon-edit"
                @click="showEditDialog(scope.row)"
              ></el-button>
              <!--删除按钮-->
              <el-button
              v-if="false"
                type="danger"
                size="mini"
                icon="el-icon-delete"
                @click="deleteById(scope.row.id)"
              ></el-button>
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
  </div>
</template>

<script>
import { parseTime } from '@/utils/ruoyi'
import { deleteById, getById,listPage,againPushLog} from "@/api/httpPushLog";
import { listPage as getCustomerListPage} from "@/api/customer";
import Clipboard from "clipboard"
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
  
      editDialogVisible: false, // 控制-修改对象对话框-是否一进页面显示
      multipleSelection: [],
      ids: [],
      fileList: [],
      typelist:[{id:1,value:"吸烟"},{id:2,value:"安全帽"},{id:3,value:"人脸"}],
      customerList:[],
      loadingCustomerNo:false,
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
    changeTypeList(){
      this.queryInfo.pageNum = 1;
      // 重新发起请求列表
      this.getListPage();
    },
    getCustomerList(){
      this.loadingCustomerNo = true
      getCustomerListPage(this.queryCustomerInfo).then(res=>{
        this.loadingCustomerNo = false
        if (res.data.code === 200) {
            this.customerList = res.data.data.list;
            this.queryInfo.customerNo = this.customerList[0].customerNo
            this.changeTypeList();
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
    pushLog(row){
      this.isLoaddingLog = true
      againPushLog({
        httpPushLogId:row.id
      }).then(res=>{
        this.isLoaddingLog = false
        if (res.data.code === 200) {
          this.$message.success('推送成功');
        }
      }).catch(err=>{
        this.isLoaddingLog = false
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
      //console.log("请求后接收到的响应结果:"+obj);
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

<style>
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
