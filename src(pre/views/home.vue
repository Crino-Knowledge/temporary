<template>
  <el-container class="home-container">
    <!--顶部-->
    <el-header style=" width: 100%" class="relative" >
      <div class="flex_row_start_center">
          <div class="nav-logo">
            <img src="@/assets/logo@2x.png" style="width:100%;" alt="">
          </div>
          <span class="head-title">视频检测AI算法中台</span>
      </div>
      
      <el-dropdown class="user-menu" @command="handleCommand">
          <div class="flex_row_center_center cf" style="cursor: pointer;">
            <span class="el-icon-user mr5"></span>
            <span style="margin-right: 5px;color:#ffffff">{{ this.$store.state.user.username }}</span>
            <span class="el-icon-arrow-down"></span>
          </div>
          <el-dropdown-menu slot="dropdown">
            <el-dropdown-item command="logout">退出登陆</el-dropdown-item>
          </el-dropdown-menu>
      </el-dropdown>
      
    </el-header>
    <!-- 主体 -->
    <el-container class="container" >
      <!-- 侧边栏 -->
      <el-aside width="240px" style="height:100%;">
        <el-menu
          :default-active="$route.path"
          router
          text-color="#ADAEB0"
          active-text-color="#409EFF"
          background-color="#222630"
        >
          <el-menu-item
            v-for="(item, i) in navList"
            :key="i"
            :index="item.name"
          >
            <i :class="item.icon"></i>
            {{ item.title }}
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main style="padding:20px;height: 100%;background-color: #15171F;">
        <!--路由占位符-->
        <router-view></router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script>
export default {
  name: "Home",
  data() {
    return {
      navList: [
        { name: "/index", title: "首页", icon: "el-icon-s-home" },
        { name: "/algorithmModel", title: "算法模型",icon:"el-icon-box" },
        { name: "/task", title: "计算任务",icon:"el-icon-coin" },
        { name: "/alarmCenter", title: "告警中心",icon:"el-icon-bell" },
        { name: "/pushLog", title: "推送日志",icon:"el-icon-postcard" },
        { name: "/customer", title: "客户管理",icon:"el-icon-s-check" },
        { name: "/user", title: "用户管理",icon:"el-icon-s-custom" },
        { name: "/dict", title: "字典管理",icon:"el-icon-notebook-1" }
      ],
    };
  },
  methods:{
    handleCommand(command){
      if(command == 'logout'){
        this.$store.commit('SET_TOKENN', '');
        this.$store.commit('SET_USER', '');
        this.$router.replace({path:'/login'})
      }
    }
  }
};
</script>

<style  scoped>

  .el-header{
    background-color: #1D2029;
    color: #ffffff;
    height: 80px !important;
    border-bottom: 1px solid #303441;
  }
  .el-aside{
    background-color: #222630;
  }
  .el-menu{
    border:none;
    
  }
  /* .el-menu-item{
    color: #ADAEB0 ;
  } */


.container{
  width: 100%;
  height: calc(100vh - 80px);
  /* padding:20px;
  box-sizing: border-box; */
}
.nav-logo {
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  width: 30px;
  /* height: 40px; */
  
}
.nav-logo img{
  width: 100%;
  height: 100%;
}
.head-title {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  left: 70px;
  font-size: 22px;
  font-family: 'DOUYU';
  
}
.user-menu{
  position: absolute !important;
  right: 20px !important;
  top: 50% !important;
  transform: translateY(-50%) !important;
}

</style>
