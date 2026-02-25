<template>
  <el-container class="home-container">
    <!--顶部导航栏-->
    <el-header class="main-header">
      <div class="header-left">
        <div class="menu-toggle" @click="toggleSidebar">
          <i class="el-icon-menu"></i>
        </div>
        <div class="header-logo">
          <img src="@/assets/logo@2x.png" style="width: 100%; height: 100%; object-fit: cover;" alt="Logo">
        </div>
        <span class="system-title">视频检测AI算法中台</span>
      </div>

      <div class="header-right">
        <div class="header-actions">
          <div class="action-btn">
            <i class="el-icon-bell"></i>
            <span class="badge" v-if="unreadCount > 0">{{ unreadCount }}</span>
          </div>
          <div class="action-btn">
            <i class="el-icon-question"></i>
          </div>
        </div>

        <el-dropdown class="user-info" @command="handleCommand">
          <div class="flex_row_center_center">
            <div class="user-avatar">
              <i class="el-icon-user"></i>
            </div>
            <span class="username">{{ this.$store.state.user.username }}</span>
            <i class="el-icon-arrow-down"></i>
          </div>
          <el-dropdown-menu slot="dropdown">
            <el-dropdown-item command="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
      </div>
    </el-header>

    <!-- 顶部常驻功能菜单 -->
    <div class="top-nav-bar">
      <div class="top-nav-container">
        <div 
          v-for="(item, i) in navList" 
          :key="i"
          class="top-nav-item"
          :class="{ 'active': isActiveTopNav(item.name) }"
          @click="goToPage(item.name)"
        >
          <i :class="item.icon"></i> {{ item.title }}
        </div>
      </div>
    </div>

    <!-- 侧边栏遮罩 -->
    <div 
      v-if="sidebarVisible" 
      class="sidebar-overlay" 
      @click="toggleSidebar"
    ></div>

    <!-- 抽屉式侧边栏 -->
    <el-aside 
      :class="['sidebar', { 'visible': sidebarVisible }]" 
      width="260px"
    >
      <div class="sidebar-header">
        <span class="sidebar-title">功能菜单</span>
        <div class="close-btn" @click="toggleSidebar">
          <i class="el-icon-close"></i>
        </div>
      </div>
      <div class="sidebar-menu">
        <div 
          v-for="(item, i) in navList" 
          :key="i"
          class="sidebar-item"
          :class="{ 'active': isActiveTopNav(item.name) }"
          @click="goToPageAndClose(item.name)"
        >
          <i :class="item.icon"></i> {{ item.title }}
        </div>
      </div>
      <div class="sidebar-footer">
        <div class="system-version">
          <i class="el-icon-info"></i>
          <span>系统版本 v2.0.0</span>
        </div>
      </div>
    </el-aside>

    <!-- 主体内容 -->
    <el-main class="main-content">
      <!--路由占位符-->
      <router-view></router-view>
    </el-main>
  </el-container>
</template>

<script>
export default {
  name: "Home",
  data() {
    return {
      navList: [
        { name: "/index", title: "首页", icon: "el-icon-s-home" },
        { name: "/algorithmModel", title: "算法模型", icon: "el-icon-box" },
        { name: "/task", title: "计算任务", icon: "el-icon-coin" },
        { name: "/alarmCenter", title: "告警中心", icon: "el-icon-bell" },
        { name: "/pushLog", title: "推送日志", icon: "el-icon-postcard" },
        { name: "/customer", title: "客户管理", icon: "el-icon-s-check" },
        { name: "/user", title: "用户管理", icon: "el-icon-s-custom" },
        { name: "/dict", title: "字典管理", icon: "el-icon-notebook-1" }
      ],
      sidebarVisible: false,
      unreadCount: 3 // 示例未读消息数
    };
  },
  methods: {
    handleCommand(command) {
      if(command === 'logout') {
        this.$store.commit('SET_TOKENN', '');
        this.$store.commit('SET_USER', '');
        this.$router.replace({path:'/login'});
      }
    },
    toggleSidebar() {
      this.sidebarVisible = !this.sidebarVisible;
    },
    goToPage(path) {
      this.$router.push({ path });
      if (this.sidebarVisible) {
        this.sidebarVisible = false;
      }
    },
    goToPageAndClose(path) {
      this.goToPage(path);
    },
    isActiveTopNav(path) {
      return this.$route.path.startsWith(path);
    }
  }
};
</script>

<style scoped>
/* 重置Element UI默认样式 */
.el-header {
  padding: 0;
  height: 72px !important; /* 增加高度 */
  background: #faf8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  position: relative;
  z-index: 100;
  flex-shrink: 0;
}

.el-main {
  padding: 24px;
  background: #f8fafc;
  overflow-y: auto;
}

/* 自定义样式 */
.home-container {
  height: 100vh;
  overflow: hidden;
}

/* 顶部导航样式 */
.main-header {
  background: #faf8f0 !important;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.menu-toggle {
  width: 48px; /* 增大按钮 */
  height: 48px;
  border-radius: 12px; /* 圆角稍微增加 */
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px; /* 图标更大 */
  color: #64748b;
  cursor: pointer;
  transition: all 0.3s ease;
  background: transparent;
  border: none;
}

.menu-toggle:hover {
  background: #f1f5f9;
  color: #667eea;
}

.header-logo {
  width: 48px; /* 增大logo */
  height: 48px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.system-title {
  font-size: 26px; /* 更大的字体 */
  font-weight: 700;
  color: #1e293b;
  letter-spacing: -0.5px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 48px; /* 增大按钮 */
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px; /* 图标更大 */
  color: #64748b;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  background: transparent;
  border: none;
}

.action-btn:hover {
  background: #f1f5f9;
  color: #667eea;
}

.badge {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 20px;
  height: 20px;
  background: #ef4444;
  color: #ffffff;
  font-size: 12px;
  font-weight: 600;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px; /* 增大按钮区域 */
  border-radius: 12px;
  transition: all 0.3s ease;
  cursor: pointer;
  background: transparent;
}

.user-info:hover {
  background: #f1f5f9;
}

.user-avatar {
  width: 36px; /* 增大头像 */
  height: 36px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px; /* 图标更大 */
  color: #ffffff;
}

.username {
  font-size: 20px; /* 更大的字体 */
  font-weight: 500;
  color: #1e293b;
}

/* 顶部常驻功能菜单 - 修改为全屏平铺 */
.top-nav-bar {
  background: #faf8f0;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
  height: 64px; /* 增加高度 */
}

.top-nav-container {
  display: flex;
  align-items: center;
  height: 100%;
  width: 100%;
  /* 将菜单项平均分配宽度 */
  gap: 0;
}

.top-nav-item {
  flex: 1; /* 平均分配空间 */
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  font-size: 16px; /* 顶部菜单字体 */
  color: #64748b;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  user-select: none;
  text-align: center;
  padding: 0 4px; /* 减少左右padding */
  position: relative;
}

.top-nav-item i {
  font-size: 18px; /* 顶部菜单图标 */
  margin-bottom: 4px;
}

.top-nav-item:hover {
  background: #f8fafc;
  color: #667eea;
}

/* 书签样式的激活状态 */
.top-nav-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  /* 书签效果：左下角圆弧 */
  border-radius: 0 0 12px 12px;
  /* 添加轻微的书签阴影效果 */
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.2);
}

/* 侧边栏遮罩 */
.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 199;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* 抽屉式侧边栏 */
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 260px !important;
  background: #ffffff;
  border-right: 1px solid #e2e8f0;
  z-index: 200;
  transform: translateX(-100%);
  transition: transform 0.3s ease;
  box-shadow: 4px 0 20px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.sidebar.visible {
  transform: translateX(0);
}

.sidebar-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sidebar-title {
  font-size: 16px; /* 放大字体 */
  font-weight: 600;
  color: #1e293b;
}

.close-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.3s ease;
  background: transparent;
  border: none;
}

.close-btn:hover {
  background: #f1f5f9;
  color: #667eea;
}

.sidebar-menu {
  flex: 1;
  padding: 16px 12px;
  overflow-y: auto;
}

.sidebar-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 16px;
  height: 48px;
  border-radius: 10px;
  margin-bottom: 4px;
  font-size: 16px; /* 放大字体 */
  color: #64748b;
  cursor: pointer;
  transition: all 0.3s ease;
}

.sidebar-item:hover {
  background: #f8fafc;
}

.sidebar-item.active {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  color: #667eea;
  font-weight: 600;
}

.sidebar-item i {
  font-size: 20px; /* 图标也放大 */
}

.sidebar-footer {
  padding: 20px 24px;
  border-top: 1px solid #f1f5f9;
}

.system-version {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px; /* 放大字体 */
  color: #94a3b8;
}

/* 主内容区 */
.main-content {
  flex: 1;
  padding: 24px;
  background: #f8fafc;
  overflow-y: auto;
}

/* 工具类 */
.flex_row_center_center {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
