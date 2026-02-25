<template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="page-icon pink">
          <i class="el-icon-collection"></i>
        </div>
        <div class="page-title">
          <h2>字典管理</h2>
          <p>管理系统数据字典</p>
        </div>
      </div>
      <button class="add-btn" @click="handleAdd">
        <i class="el-icon-plus"></i> 添加字典
      </button>
    </div>

    <!-- 搜索区域 -->
    <div class="search-section">
      <div class="search-box">
        <i class="el-icon-search search-icon"></i>
        <el-input
          v-model="queryParams.searchKey"
          placeholder="搜索字典名称..."
          clearable
          @clear="getList"
          @keyup.enter.native="getList"
          class="search-input"
        />
        <button class="search-btn" @click="getList">搜索</button>
      </div>
    </div>

    <!-- 表格区域 -->
    <div class="table-section">
      <div class="table-header">
        <span class="table-title">字典列表</span>
        <span class="table-count">共 {{ deptList.length }} 条记录</span>
      </div>

      <div class="custom-table">
        <el-table
          v-if="refreshTable"
          v-loading="loading"
          :data="deptList"
          row-key="id"
          :default-expand-all="isExpandAll"
          :tree-props="{children: 'childList', hasChildren: 'hasChildren'}"
          style="width: 100%"
        >
          <el-table-column type="index" label="序号" width="80" align="center">
            <template slot-scope="scope">
              <span class="index-badge">{{ scope.$index + 1 }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="字典名称" min-width="180"></el-table-column>
          <el-table-column prop="id" label="字典ID" min-width="120"></el-table-column>
          <el-table-column prop="orderNum" label="字典排序" width="100" align="center"></el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template slot-scope="scope">
              <span class="status-tag" :class="scope.row.status ? 'status-active' : 'status-inactive'">
                {{ scope.row.status ? '启用' : '停用' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="操作" fixed="right" width="180" align="center">
            <template slot-scope="scope">
              <div class="action-btns">
                <button class="action-icon edit" @click="handleUpdate(scope.row)" title="修改">
                  <i class="el-icon-edit"></i>
                </button>
                <button class="action-icon add" @click="handleAdd(scope.row)" title="新增">
                  <i class="el-icon-plus"></i>
                </button>
                <button class="action-icon delete" @click="handleDelete(scope.row)" title="删除">
                  <i class="el-icon-delete"></i>
                </button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 添加或修改部门对话框 -->
    <el-dialog :title="title" :visible.sync="open" width="750px"  :close-on-click-modal="false">
      <el-form ref="form" :model="form" :rules="rules" label-width="110px">
        <el-row>
          <el-col :span="24">
            <el-form-item label="上级字典" prop="parentId">
              <treeselect v-model="form.parentId" :options="deptOptions" :normalizer="normalizer" placeholder="选择上级字典" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="12">
            <el-form-item label="字典名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入字典名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="显示排序" prop="orderNum">
              <el-input-number v-model="form.orderNum" controls-position="right" :min="0" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="12">
            <el-form-item label="字典状态">
              <el-radio-group v-model="form.status">
                <el-radio
                  :label="1"
                >正常</el-radio>
                 <el-radio
                  :label="0"
                >停用</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="submitForm">确 定</el-button>
        <el-button @click="cancel">取 消</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getDictList, getAllDict, delDict, addDict, updateDict } from "@/api/jsDict";
import Treeselect from "@riophae/vue-treeselect";
import "@riophae/vue-treeselect/dist/vue-treeselect.css";

export default {
  name: "Dict",
  // dicts: ['sys_normal_disable'],
  components: { Treeselect },
  data() {
    return {
      tableHeight:"0px",
      // 遮罩层
      loading: true,
      // 显示搜索条件
      showSearch: true,
      // 表格树数据
      deptList: [],
      // 部门树选项
      deptOptions: [],
      // 弹出层标题
      title: "",
      // 是否显示弹出层
      open: false,
      // 是否展开，默认全部展开
      isExpandAll: true,
      // 重新渲染表格状态
      refreshTable: true,
      // 查询参数
      queryParams: {
        "endTime": null,
        "name": null,
        "pageIndex": 1,
        "pageSize": 1000,
        "searchKey": null,
        "startTime": null,
        "status": null
      },
      // 表单参数
      form: {},
      // 表单校验
      rules: {
        parentId: [
          { required: true, message: "上级字典不能为空", trigger: "change" }
        ],
        name: [
          { required: true, message: "字典名称不能为空", trigger: "blur" }
        ],
        orderNum: [
          { required: true, message: "显示排序不能为空", trigger: "blur" }
        ]
      }
    };
  },
  created() {
    //  this.tableHeight = (window.innerHeight - 60 - 24 - 24 - 50 - 24) + 'px'
    this.getList();
  },
  methods: {
    getList() {
      this.loading = true;
      getAllDict().then(response => {
        // console.log("getAllDict",response.data)
        this.deptList = response.data.data.data;
        this.loading = false;
      }).catch(err=>{
        this.loading = false;
      });
    },
    /** 转换部门数据结构 */
    normalizer(node) {
      if (node.childList && !node.childList.length) {
        delete node.childList;
      }
      return {
        id: node.id,
        label: node.name,
        children: node.childList
      };
    },
    // 取消按钮
    cancel() {
      this.open = false;
      this.reset();
    },
    // 表单重置
    reset() {
      this.form = {
          "name": null,
          "orderNum": 1,
          "parentId": 0,
          "status": 1
      };
      this.resetForm("form");
    },
    /** 搜索按钮操作 */
    handleQuery() {
      this.getList();
    },
    /** 重置按钮操作 */
    resetQuery() {
      this.resetForm("queryForm");
      this.handleQuery();
    },
    /** 新增按钮操作 */
    handleAdd(row) {
      this.reset();
      if (row != undefined) {
        this.form.parentId = row.id;
      }
      this.open = true;
      this.title = "添加字典";
      getAllDict().then(response => {
        // this.deptOptions = response.data.data
        this.deptOptions = [];
        const dept = { id: 0, name: '新建字典', childList: [] };
        dept.childList = response.data.data.data;
         this.deptOptions.push(dept);
        // this.deptOptions = this.handleTree(response.data.list)
      });
    },
    /** 展开/折叠操作 */
    toggleExpandAll() {
      this.refreshTable = false;
      this.isExpandAll = !this.isExpandAll;
      this.$nextTick(() => {
        this.refreshTable = true;
      });
    },
    /** 修改按钮操作 */
    handleUpdate(row) {
      this.reset();
       getAllDict().then(response => {
        // this.deptOptions = response.data.data
        this.deptOptions = [];
        const dept = { id: 0, name: '新建字典', childList: [] };
        dept.childList = response.data.data.data;
         this.deptOptions.push(dept);
         this.form = row;
         this.open = true;
         this.title = "修改字典";
      });

    },
    /** 提交按钮 */
    submitForm: function() {
      this.$refs["form"].validate(valid => {
        if (valid) {
          if (this.form.id != undefined) {
            updateDict(this.form).then(response => {
              this.$message({
                message: '修改成功',
              });
              this.open = false;
              this.getList();
            });
          } else {
            addDict(this.form).then(response => {
              this.$message({
                message: '新增成功',
              });
              this.open = false;
              this.getList();
            });
          }
        }
      });
    },
    /** 删除按钮操作 */
    handleDelete(row) {
      this.$confirm('是否确认删除名称为"' + row.name + '"的数据项？').then(function() {
        return delDict(row.id);
      }).then(() => {
        this.getList();
        this.$message({
          message: '删除成功',
        });
      }).catch(() => {});
    }
  }
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

.action-icon.add {
  background: #dcfce7;
  color: #16a34a;
}

.action-icon.add:hover {
  background: #16a34a;
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
.el-date-picker, .el-radio, .el-input-number {
  font-size: 17px !important; /* 原14px +3 */
}
/* 适配treeselect组件字体大小 */
.vue-treeselect__placeholder, .vue-treeselect__single-value, .vue-treeselect__option-label {
  font-size: 17px !important;
}
</style>
