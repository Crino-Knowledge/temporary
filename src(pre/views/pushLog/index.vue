<template>
    <div class="page-container">
        <!-- 页面头部 -->
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
            <button class="add-btn" @click="handleExport">
                <i class="el-icon-download"></i> 导出日志
            </button>
        </div>

        <!-- 搜索区域 -->
        <div class="search-section">
            <div class="search-box">
                <i class="el-icon-search search-icon"></i>
                <el-input
                    v-model="queryParams.searchKey"
                    placeholder="搜索关键字..."
                    clearable
                    @clear="handleQuery"
                    @keyup.enter.native="handleQuery"
                    class="search-input"
                />
                <button class="search-btn" @click="handleQuery">搜索</button>
            </div>
        </div>

        <!-- 表格区域 -->
        <div class="table-section">
            <div class="table-header">
                <span class="table-title">推送记录</span>
                <span class="table-count">共 {{ total }} 条记录</span>
            </div>

            <div class="custom-table">
                <el-table v-loading="loading" :data="configList" @selection-change="handleSelectionChange" style="width: 100%">
                    <el-table-column type="index" label="序号" width="80" align="center">
                        <template slot-scope="scope">
                            <span class="index-badge">{{ scope.$index + 1 }}</span>
                        </template>
                    </el-table-column>
                    <el-table-column label="设备序列号" prop="deviceSerialNum" min-width="150" show-overflow-tooltip></el-table-column>
                    <el-table-column label="产品ID" prop="productId" min-width="100" align="center"></el-table-column>
                    <el-table-column label="产品名称" prop="productName" min-width="150"></el-table-column>
                    <el-table-column label="是否最新推送" prop="isNew" min-width="120" align="center"></el-table-column>
                    <el-table-column label="推送区域" prop="regionName" min-width="180" show-overflow-tooltip></el-table-column>
                    <el-table-column label="推送类型" prop="pushType" min-width="120" align="center"></el-table-column>
                    <el-table-column label="推送状态" prop="status" min-width="100" align="center">
                        <template slot-scope="scope">
                            <span class="status-tag" :class="scope.row.status === '成功' ? 'status-active' : 'status-inactive'">
                                {{ scope.row.status }}
                            </span>
                        </template>
                    </el-table-column>
                    <el-table-column label="推送时间" prop="operateDate" min-width="160" align="center">
                        <template slot-scope="scope">
                            <span>{{ parseTime(scope.row.operateDate) }}</span>
                        </template>
                    </el-table-column>
                    <el-table-column label="操作" fixed="right" width="100" align="center">
                        <template slot-scope="scope">
                            <div class="action-btns">
                                <button class="action-icon edit" @click="handleUpdate(scope.row)" title="详情">
                                    <i class="el-icon-view"></i>
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
                    :current-page="queryParams.pageIndex"
                    :page-sizes="[10, 20, 50, 100]"
                    :page-size="queryParams.pageSize"
                    layout="total, sizes, prev, pager, next"
                    :total="total"
                    background
                >
                </el-pagination>
            </div>
        </div>

        <!-- 详情对话框 -->
        <el-dialog title="详情" :visible.sync="open" width="900px" append-to-body>
            <div class="re-push">
                <el-button size="small" type="danger" plain @click="openRePush">
                    重新推送</el-button>
            </div>

            <el-descriptions :column='2'>
                <el-descriptions-item label="设备序列号">{{info.deviceSerialNum}}</el-descriptions-item>
                <el-descriptions-item label="产品ID">{{info.productId}}</el-descriptions-item>
                <el-descriptions-item label="产品名称">{{info.productName}}</el-descriptions-item>
                <el-descriptions-item label="推送类型">{{info.pushType}}</el-descriptions-item>
                <el-descriptions-item label="推送状态">{{info.status}}</el-descriptions-item>
                <el-descriptions-item label="操作状态">{{info.status}}</el-descriptions-item>
                <el-descriptions-item label="是否最新推送">{{info.isNew}}</el-descriptions-item>
                <el-descriptions-item label="推送区域">{{info.regionName}}</el-descriptions-item>
                <el-descriptions-item label="推送时间">{{parseTime(info.operateDate)}} </el-descriptions-item>
            </el-descriptions>
            <el-descriptions :column='1'>
                <el-descriptions-item label="错误信息">{{info.errorMsg}}</el-descriptions-item>
                <el-descriptions-item labelStyle="width:60px" label="请求头">{{info.httpReqHeader}}</el-descriptions-item>
                <el-descriptions-item labelStyle="width:60px" label="请求地址">{{info.httpReqUrl}}</el-descriptions-item>
                <el-descriptions-item labelStyle="width:120px" label="请求参数">{{info.httpReqParam}}</el-descriptions-item>
                <el-descriptions-item labelStyle="width:60px" label="返回结果">{{info.httpResult}}</el-descriptions-item>
            </el-descriptions>
        </el-dialog>

        <!-- 推送数据 -->
        <el-dialog title="推送数据" :visible.sync="isRePush" width="900px" append-to-body>
            <el-form ref="formRePush" :model="formRePush" :rules="rulesRePush" label-width="100px">
                <el-form-item label="请求头" prop="headerJson">
                    <el-input type="textarea" :rows="2" v-model="formRePush.headerJson" placeholder="请输入请求头" />
                </el-form-item>
                <el-form-item label="请求参数" prop="dataJson">
                    <el-input type="textarea" :rows="3" v-model="formRePush.dataJson" placeholder="请输入请求参数" />
                </el-form-item>
            </el-form>
            <div slot="footer" class="dialog-footer">
                <el-button type="primary" @click="submitFormRePush">确 定</el-button>
                <el-button @click="cancel">取 消</el-button>
            </div>
        </el-dialog>
    </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { getHttpPushLogListPageVo,againPushLog } from "@/api/pushlog";
import { Tools } from "@/utils/tools"
import { getToken } from "@/utils/auth";
import { getDictById } from "@/api/jsDict"

export default {
    name: "PushLog",
    computed: {
        ...mapGetters([
            'regionCode',
            'regionParentCode',
            'dataType',
            'regionCodeType',
        ]),
    },
    data () {
        return {
            formRePush: {},
            rulesRePush: {},
            isRePush: false,
            regionCodeList: [],
            productTypeList: [],
            addressList: [],
            videoTypeList: [],

            defaultProps: {
                children: 'childList',
                label: 'name',
                value: 'code',
                expandTrigger: 'hover',
            },
            statusList: [
                {
                    label: '全部推送类型',
                    value: null
                },
                {
                    label: '设备信息',
                    value: 911
                },
                {
                    label: '设备日志',
                    value: 912
                },
                {
                    label: '心跳日志',
                    value: 913
                }],
            statusList2: [
                {
                    label: '是',
                    value: 1
                },
                {
                    label: '否',
                    value: 0
                }],
            statusList3: [
                {
                    label: '成功',
                    value: 1
                },
                {
                    label: '失败',
                    value: 0
                }],
            // 遮罩层
            loading: true,
            // 选中数组
            ids: [],
            // 非单个禁用
            single: true,
            // 非多个禁用
            multiple: true,
            // 显示搜索条件
            showSearch: true,
            // 总条数
            total: 0,
            // 参数表格数据
            configList: [],
            // 弹出层标题
            title: "",
            // 是否显示弹出层
            open: false,
            // 日期范围
            dateRange: [],
            // 查询参数
            queryParams: {
                pageIndex: 1,
                pageSize: 10,
                pushType: 912,
                regionCode: null,
                searchKey: null,
                latestData: null,
                deviceKey: null,
                status: null,
                productType: null
            },
            // 表单参数
            form: {},
            // 表单校验
            info: {}
        };
    },
    created () {
        // this.getList();
        this.getDictById('1372')

        this.getAddress(this.regionCode)
        this.dateRange = [this.getData(-7), this.getData(0)]

    },
    methods: {
        getData (day) {
            var today = new Date()
            var targetday = today.getTime() + 1000 * 60 * 60 * 24 * day
            today.setTime(targetday)
            var tYear = today.getFullYear()
            var tMonth = today.getMonth()
            var tDate = today.getDate()
            tMonth = this.doHandMonth(tMonth + 1)
            tDate = this.doHandMonth(tDate)
            return tYear + "-" + tMonth + "-" + tDate
        },


        doHandMonth (month) {
            var m = month
            if (month.toString().length == 1) {
                m = "0" + month
            }
            return m
        },
        cancel () {
            this.formRePush = {}
            this.isRePush = false;
        },
        submitFormRePush () {
            this.$refs["formRePush"].validate(valid => {
                if (valid) {
                    this.$modal.loading("正在推送数据...")
                    againPushLog(this.formRePush).then(res => {
                        this.$modal.closeLoading()

                        this.$modal.msgSuccess("推送成功");
                        this.cancel()
                    }).catch(err => {
                        this.$modal.closeLoading()
                    })
                }
            })
        },
        openRePush () {
            this.isRePush = true
            this.formRePush = {
                "dataJson": this.info.httpReqParam,
                "headerJson": this.info.httpReqHeader,
                "id": this.info.id
            }
        },
        getProductList () {
            this.queryParamsProduct.regionCode = this.regionCode
            getProductListPageVo(this.queryParamsProduct).then(res => {
                this.productList = res.data.list
            })
        },
        getDictById (id) {
            getDictById(id).then(res => {
                this.videoTypeList = res.data.data
                let list = [];
                this.videoTypeList.forEach(el => {
                    list.push(el.id)
                })
                // this.queryParams.productType = list
                // this.queryParamsProduct.deviceTypeList = list
                this.getList()
                // this.getProductList()
            })
        },
        changeDeviceQuery (value) {
            if (value.length > 0) {
                this.queryParams.productType = value[value.length - 1]
            } else {
                this.queryParams.productType = null
            }
            this.handleQuery()
        },
        changeRegionQuery (value) {
            if (this.regionCodeType == 405) {
                if (value.length > 1) {
                    getAssignChildListByParentCode(value[1]).then((res) => {
                        this.assignListQuery = res.data.childList
                    })
                }
            }
            if (this.regionCodeType == 404) {
                if (value.length > 2) {
                    getAssignChildListByParentCode(value[2]).then((res) => {
                        this.assignListQuery = res.data.childList
                    })
                }
            }
            if (value.length > 0) {
                this.queryParams.regionCode = value[value.length - 1]
            } else {
                this.queryParams.regionCode = this.regionCode
                this.queryParams.manageCode = null
                this.assignListQuery = []
                this.manageCodeValue = []
            }
            this.queryParams.pageIndex = 1
            this.getList()
        },
        /*查询区域地址*/
        getAddress (code) {
            this.addressList = []
            getAddressByParentCode(code).then((res) => {
                this.addressList.push(res.data)
            })
        },
        /** 查询参数列表 */
        getList () {
            this.loading = true;
            if (this.dateRange.length > 0) {

                this.queryParams.startTime = Date.parse(this.dateRange[0]) - 8 * 60 * 60 * 1000
                this.queryParams.endTime = Date.parse(this.dateRange[1]) + 16 * 60 * 60 * 1000 - 1
            } else {
                this.queryParams.startTime = null
                this.queryParams.endTime = null
            }

            getHttpPushLogListPageVo(this.queryParams).then(
                (response) => {



                    this.configList = response.data.list;
                    this.configList.forEach(e => {
                        if (e.status == 0) {
                            e.status = '失败'
                        } else {
                            e.status = '成功'
                        }
                        if (e.latestData == 1) {
                            e.isNew = '是'
                        } else {
                            e.isNew = '否'
                        }
                        if (e.pushType == 911) {
                            e.pushType = '设备信息'
                        } else if (e.pushType == 912) {
                            e.pushType = '设备日志'
                        }
                    })
                    this.total = response.data.total;
                    this.loading = false;
                }
            );
        },
        /** 搜索按钮操作 */
        handleQuery () {
            this.queryParams.pageIndex = 1;
            this.getList();
        },
        /** 重置按钮操作 */
        resetQuery () {
            this.dateRange = [this.getData(-7), this.getData(0)];
            this.queryParams = {
                pageIndex: 1,
                pageSize: 10,
                pushType: 912,
                regionCode: null,
                searchKey: null,
                latestData: null,
                deviceKey: null
            }
            this.handleQuery();
        },
        // 多选框选中数据
        handleSelectionChange (selection) {
            this.ids = selection.map((item) => item.id
            );
            this.single = selection.length != 1;
            this.multiple = !selection.length;
        },
        /** 修改按钮操作 */
        handleUpdate (row) {
            this.info = row;
            this.open = true;
        },
        getToken () {
            return getToken();
        },
        /** 导出按钮操作 */
        handleExport () {
            Tools.exportExcel(
                "/sys/httpPushLog/exportToExcel",
                this.queryParams,
                "推送日志",
                this
            );
        },
        /** 导出按钮操作 */
        handleExportwl () {
            Tools.exportExcel(
                "/sys/httpPushLog/exportToCdlotExcel",
                this.queryParams,
                "推送日志",
                this
            );
        },
        /** 刷新缓存按钮操作 */
        handleRefreshCache () {
            // refreshCache().then(() => {
            //     this.$modal.msgSuccess("刷新成功");
            // });
            this.getList()
        },
        // 监听 pageSize 改变的事件
        handleSizeChange(newSize) {
            this.queryParams.pageSize = newSize;
            this.getList();
        },
        // 监听 当前页码值 改变的事件
        handleCurrentChange(newPage) {
            this.queryParams.pageIndex = newPage;
            this.getList();
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
    font-size: 28px;
    color: #ffffff;
}

.page-icon.purple {
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
}

.page-title h2 {
    font-size: 24px;
    font-weight: 700;
    color: #1e293b;
    margin: 0 0 4px 0;
}

.page-title p {
    font-size: 14px;
    color: #94a3b8;
    margin: 0;
}

.add-btn {
    height: 44px;
    padding: 0 24px;
    border-radius: 12px;
    font-size: 14px;
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
    font-size: 18px;
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
    font-size: 14px;
    color: #1e293b;
}

.search-btn {
    height: 40px;
    padding: 0 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #ffffff;
    border: none;
    border-radius: 10px;
    font-size: 14px;
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
    font-size: 18px;
    font-weight: 600;
    color: #1e293b;
}

.table-count {
    color: #94a3b8;
    font-size: 13px;
}

.custom-table >>> .el-table {
    background: transparent;
}

.custom-table >>> .el-table th {
    background: #f8fafc;
    color: #64748b;
    font-weight: 600;
    font-size: 13px;
}

.custom-table >>> .el-table td {
    font-size: 14px;
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
    font-size: 13px;
    font-weight: 600;
    color: #64748b;
}

.status-tag {
    display: inline-flex;
    align-items: center;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
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
    font-size: 14px;
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

.re-push {
    position: absolute;
    right: 60px;
    top: 20px;
}
</style>
