<template>
    <div class="app-container">
        <el-form :model="queryParams" ref="queryForm" :inline="true" v-show="showSearch" label-width="160px">
            <el-form-item label="关键字" prop="searchKey">
                <el-input v-model="queryParams.searchKey" placeholder="请输入关键字" clearable size="small"
                    style="width: 240px" @keyup.enter.native="handleQuery" />
            </el-form-item>

            <el-form-item label="设备序列号" prop="deviceKey">
                <el-input v-model="queryParams.deviceKey" placeholder="请输入设备序列号" clearable size="small"
                    style="width: 240px" @keyup.enter.native="handleQuery" />
            </el-form-item>
            <el-form-item label="开始日期/结束日期">
                <el-date-picker v-model="dateRange" size="small" style="width: 360px" value-format="yyyy-MM-dd"
                    type="daterange" @change="handleQuery" range-separator="-" start-placeholder="开始日期"
                    end-placeholder="结束日期">
                </el-date-picker>
            </el-form-item>

            <el-form-item label="推送类型">
                <el-select v-model="queryParams.pushType" @change="handleQuery" placeholder="推送类型" clearable
                    size="small" style="width: 240px">
                    <el-option v-for="dict in this.statusList" :key="dict.value" :label="dict.label"
                        :value="dict.value" />
                </el-select>
            </el-form-item>
            <el-form-item label="安装区域" prop="regionCode">
                <el-cascader clearable style="width: 240px;" change-on-select :props="defaultProps"
                    v-model="regionCodeList" :options="addressList" @change="changeRegionQuery"></el-cascader>
            </el-form-item>
            <el-form-item label="设备类型" prop="productType">
                <el-cascader change-on-select clearable :show-all-levels="false" v-model="productTypeList"
                    @change="changeDeviceQuery" :options="videoTypeList"
                    :props="{ children: 'childList', label: 'name', value: 'id' }"></el-cascader>
            </el-form-item>
            <el-form-item label="是否最新推送">
                <el-select v-model="queryParams.latestData" @change="handleQuery" placeholder="是否最新推送" clearable
                    size="small" style="width: 240px">
                    <el-option v-for="dict in this.statusList2" :key="dict.value" :label="dict.label"
                        :value="dict.value" />
                </el-select>
            </el-form-item>

            <el-form-item label="推送状态">
                <el-select v-model="queryParams.status" @change="handleQuery" placeholder="推送状态" clearable size="small"
                    style="width: 240px">
                    <el-option v-for="dict in this.statusList3" :key="dict.value" :label="dict.label"
                        :value="dict.value" />
                </el-select>
            </el-form-item>

            <el-form-item>
                <el-button type="primary" icon="el-icon-search" size="mini" @click="handleQuery">搜索</el-button>
                <el-button icon="el-icon-refresh" type="info" size="mini" @click="resetQuery">重置</el-button>
                <div style="float:right;margin-left:300px;">
                    <el-button type="danger" plain icon="el-icon-refresh" size="mini" @click="handleRefreshCache"
                        v-hasPermi="['system:config:remove']">刷新缓存</el-button>
                    <el-button type="warning" plain icon="el-icon-upload2" size="mini"
                        @click="handleExport">导出</el-button>
                    <el-button type="warning" style="margin-left:20px;" plain icon="el-icon-upload2" size="mini"
                        @click="handleExportwl">物联导出</el-button>
                </div>
            </el-form-item>
        </el-form>

        <el-table v-loading="loading" :data="configList" @selection-change="handleSelectionChange">
            <el-table-column type="selection" width="55" align="center" />
            <!-- <el-table-column label="日志编号" align="center" prop="id" /> -->
            <el-table-column label="设备序列号" align="center" prop="deviceSerialNum" />
            <!-- <el-table-column label="设备UUID" align="center" prop="deviceUuid" /> -->
            <el-table-column label="产品ID" align="center" prop="productId" />
            <el-table-column label="产品名称" align="center" prop="productName" />
            <el-table-column label="是否最新推送" align="center" prop="isNew" />
            <el-table-column label="推送区域" width="220" align="center" prop="regionName" />
            <el-table-column label="推送类型" align="center" prop="pushType" />
            <el-table-column label="推送状态" align="center" prop="status" />
            <el-table-column label="推送时间" align="center" prop="operateDate" width="180">
                <template slot-scope="scope">
                    <span>{{ parseTime(scope.row.operateDate) }}</span>
                </template>
            </el-table-column>
            <el-table-column label="操作" align="center" class-name="small-padding fixed-width">
                <template slot-scope="scope">
                    <el-button size="small " type="success" plain icon="el-icon-edit" @click="handleUpdate(scope.row)">
                        详情</el-button>
                </template>
            </el-table-column>
        </el-table>

        <pagination v-show="total > 0" :total="total" :page.sync="queryParams.pageIndex"
            :limit.sync="queryParams.pageSize" @pagination="getList" />

        <!-- 添加或修改参数配置对话框 -->
        <el-dialog title="详情" :visible.sync="open" width="900px" append-to-body>
            <div class="re-push">
                <el-button size="small " type="danger" plain @click="openRePush">
                    重新推送</el-button>
            </div>

            <el-descriptions :column='2'>
                <el-descriptions-item label="设备序列号">{{info.deviceSerialNum}}</el-descriptions-item>
                <!-- <el-descriptions-item label="设备UUID">{{info.deviceUuid}}</el-descriptions-item> -->
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
    },
};
</script>
<style scoped>
.app-container {
    background: #ffffff;
    width: calc(100% - 24px - 24px);
    height: calc(100vh - 60px - 24px - 24px);
    margin: 24px auto;
    overflow-y: hidden;
    box-shadow: 0px 3px 19px 2px rgba(47, 47, 47, 0.06);
    border-radius: 6px;
}
.re-push {
    position: absolute;
    right: 10px;
    top: 64px;
}
</style>
