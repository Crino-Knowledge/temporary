<template>
  <div class="">
    <el-row :gutter="10" class="mb10">
      <el-col :span="1.5">
        <el-button
          type="primary"
          plain
          icon="el-icon-plus"
          size="mini"
          @click="handleAdd"
        >新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="info"
          plain
          icon="el-icon-sort"
          size="mini"
          @click="toggleExpandAll"
        >展开/折叠</el-button>
      </el-col>
      <!-- <right-toolbar :showSearch.sync="showSearch" @queryTable="getList"></right-toolbar> -->
    </el-row>

    <el-table
      v-if="refreshTable"
      v-loading="loading"
      :data="deptList"
      row-key="id"
      :default-expand-all="isExpandAll"
      :tree-props="{children: 'childList', hasChildren: 'hasChildren'}"
    >
      <el-table-column prop="name" label="字典名称" width="260"></el-table-column>
      <el-table-column prop="id" label="字典ID" width="260"></el-table-column>
      <el-table-column prop="orderNum" label="字典排序" width="260"></el-table-column>
      <el-table-column prop="status" label="状态" align="center" width="100">
        <template slot-scope="scope">
           <span class="tag-js" v-if="scope.row.status">
            {{scope.row.status?'正常':'停用'}}
          </span>
           <span class="tag-js tag-d" v-if="!scope.row.status">
            {{scope.row.status?'正常':'停用'}}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width">
        <template slot-scope="scope">
          <el-button
            size="mini"
            type="text"
            icon="el-icon-edit"
            @click="handleUpdate(scope.row)"
          >修改</el-button>
          <el-button
            size="mini"
            type="text"
            icon="el-icon-plus"
            @click="handleAdd(scope.row)"
          >新增</el-button>
          <el-button
            size="mini"
            type="text"
            icon="el-icon-delete"
            @click="handleDelete(scope.row)"
          >删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加或修改部门对话框 -->
    <el-dialog :title="title" :visible.sync="open" width="750px"  :close-on-click-modal="false">
      <el-form ref="form" :model="form" :rules="rules" label-width="120px">
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
<style  scoped>
</style>
