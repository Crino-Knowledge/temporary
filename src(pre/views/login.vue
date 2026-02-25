<template>
  <div id="login-page">
    <div class="login-background">
      <div class="gradient-overlay"></div>
      <div class="floating-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
      </div>
    </div>

    <div class="login-container">
      <div class="login-left">
        <div class="brand-section">
          <div class="logo">&#127969;</div>
          <h1 class="brand-title">地下停车场<br>智能识别系统</h1>
          <p class="brand-subtitle">基于深度学习的智能停车管理解决方案<br>让停车更便捷，让管理更高效</p>
        </div>

        <div class="feature-list">
          <div class="feature-item">
            <div class="feature-icon">&#128247;</div>
            <div class="feature-text">
              <h4>智能车牌识别</h4>
              <p>高精度识别，支持多种车牌类型</p>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon">&#128200;</div>
            <div class="feature-text">
              <h4>实时数据分析</h4>
              <p>多维度数据统计，可视化展示</p>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon">&#128276;</div>
            <div class="feature-text">
              <h4>智能告警推送</h4>
              <p>异常情况实时提醒，多渠道推送</p>
            </div>
          </div>
        </div>
      </div>

      <div class="login-right">
        <div class="login-header">
          <h2>欢迎登录</h2>
          <p>请使用您的账号密码登录系统</p>
        </div>

        <el-form class="login-form" label-position="left" label-width="0px">
          <p class="login_title" style="display:none;">视频检测AI算法中台</p>
          
          <el-form-item>
            <label class="form-label">用户名</label>
            <input 
              type="text" 
              class="form-input" 
              auto-complete="off" 
              placeholder="请输入用户名" 
              v-model="loginForm.username"
            >
          </el-form-item>
          
          <el-form-item>
            <label class="form-label">密码</label>
            <div class="relative">
              <input 
                :type="isShowEye?'text':'password'" 
                class="form-input" 
                auto-complete="off"  
                @keyup.enter="login" 
                placeholder="请输入密码" 
                v-model="loginForm.password"
              >
              <img 
                class="eye_img" 
                v-if="isShowEye" 
                src="@/assets/login/show@2x.png" 
                @click="isShowEye=!isShowEye" 
                alt=""
              >
              <img 
                class="eye_img" 
                v-if="!isShowEye" 
                src="@/assets/login/noshow@2x.png" 
                @click="isShowEye=!isShowEye" 
                alt=""
              >
            </div>
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              @click="login"
              :loading="isLoading"
              class="login-btn"
            >
              <span v-if="!isLoading">登 录</span>
              <span v-else>登录中...</span>
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="login-footer">
          <a href="#" @click.prevent="forgetPassword">忘记密码?</a>
          <a href="#" @click.prevent="registerAccount">注册账号</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { sha256 } from 'js-sha256'
import { userLogin } from "@/api/user";

export default {
  name: "Login",
  data() {
    return {
      loginForm: {
        username: "",
        password: "",
      },
      responseResult: [],
      isLoading: false,
      isShowEye: false
    };
  },
  methods: {
    // 注释掉：真实登录逻辑（需接入后端API）
    /*
    login() {
      var _this = this;
      this.isLoading = true;
      
      // 实际的API调用
      userLogin(this.loginForm)
        .then(response => {
          const { token, user } = response.data;
          _this.$store.commit('SET_TOKENN', token);
          _this.$store.commit('SET_USER', user);
          
          var path = this.$route.query.redirect;
          this.$router.replace({path: path === '/' || path === undefined ? '/' : path});
        })
        .catch(error => {
          console.error('登录失败:', error);
          this.$message.error('登录失败，请检查用户名和密码');
          this.isLoading = false;
        });
    },
    */

    // 模拟登陆
    login() {
      var _this = this;
      this.isLoading = true;
      // 模拟登录成功，跳过API验证
      setTimeout(() => {
        this.isLoading = false;
        // 1. 模拟一个假token（仅用于通过前端路由检查）
        let mockToken = 'mock_token_' + Date.now();
        // 2. 模拟用户信息（使用输入的用户名，或默认admin）
        let mockUser = {
          username: this.loginForm.username || 'admin',
          // 可以补充其他可能需要的字段，如id、avatar等，但通常非必需
        };
        // 3. 将模拟数据存入store（模仿原逻辑）
        _this.$store.commit('SET_TOKENN', mockToken);
        _this.$store.commit('SET_USER', mockUser);
        // 4. 跳转到首页或重定向页面
        var path = this.$route.query.redirect;
        this.$router.replace({path: path === '/' || path === undefined ? '/' : path});
      }, 300); // 添加300ms延迟，模拟网络请求，让登录按钮的loading状态可见
    },
    // 模拟登陆
    
    forgetPassword() {
      this.$message.info('忘记密码功能待实现');
    },
    
    registerAccount() {
      this.$message.info('注册账号功能待实现');
    }
  },
};
</script>

<style scoped>
/* 背景样式 */
.login-background {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  z-index: 0;
}

.gradient-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

.floating-shapes {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 20s infinite ease-in-out;
}

.shape-1 { 
  width: 500px; 
  height: 500px; 
  top: -120px; 
  right: -120px; 
  animation-delay: 0s; 
}
.shape-2 { 
  width: 400px; 
  height: 400px; 
  bottom: -60px; 
  left: -60px; 
  animation-delay: -5s; 
}
.shape-3 { 
  width: 250px; 
  height: 250px; 
  top: 50%; 
  left: 30%; 
  animation-delay: -10s; 
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-40px) rotate(180deg); }
}

/* 整体布局 */
#login-page {
  min-height: 100vh;
  display: flex;
  position: relative;
  overflow: hidden;
}

.login-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 1400px;
  margin: auto;
  display: flex;
  padding: 60px;
  gap: 80px;
  align-items: center;
}

/* 左侧品牌区 */
.login-left {
  flex: 1;
  color: #ffffff;
  padding: 60px;
}

.brand-section {
  margin-bottom: 80px;
}

.logo {
  width: 100px;
  height: 100px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 25px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 50px;
  margin-bottom: 40px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.brand-title {
  font-size: 50px;
  font-weight: 800;
  margin-bottom: 20px;
  letter-spacing: -1px;
  line-height: 1.3;
}

.brand-subtitle {
  font-size: 22px;
  opacity: 0.9;
  line-height: 1.7;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px 25px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.feature-icon {
  width: 55px;
  height: 55px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 25px;
}

.feature-text h4 {
  font-size: 19px;
  font-weight: 600;
  margin-bottom: 5px;
}

.feature-text p {
  font-size: 17px;
  opacity: 0.8;
}

/* 右侧登录区 */
.login-right {
  width: 550px;
  background: #ffffff;
  border-radius: 30px;
  padding: 60px;
  box-shadow: 0 30px 60px -15px rgba(0, 0, 0, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 50px;
}

.login-header h2 {
  font-size: 35px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 10px;
}

.login-header p {
  font-size: 17px;
  color: #64748b;
}

.form-group {
  margin-bottom: 30px;
}

.form-label {
  display: block;
  font-size: 17px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 10px;
}

.form-input {
  width: 100%;
  height: 60px;
  padding: 0 25px;
  border: 2px solid #e5e7eb;
  border-radius: 15px;
  font-size: 18px;
  transition: all 0.3s ease;
  background: #f9fafb;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  background: #ffffff;
  box-shadow: 0 0 0 5px rgba(102, 126, 234, 0.1);
}

.relative {
  position: relative;
}

.eye_img {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  width: 30px;
  height: 30px;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.3s ease;
}

.eye_img:hover {
  opacity: 1;
}

.login-btn {
  width: 100%;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  border: none;
  border-radius: 15px;
  font-size: 19px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 20px;
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
}

.login-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.login-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 30px;
  font-size: 17px;
}

.login-footer a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.login-footer a:hover {
  text-decoration: underline;
}

/* 响应式 */
@media (max-width: 1400px) {
  .login-container {
    padding: 40px;
    gap: 60px;
  }
  
  .login-left {
    padding: 40px;
  }
  
  .brand-title {
    font-size: 42px;
  }
  
  .brand-subtitle {
    font-size: 19px;
  }
  
  .feature-item {
    padding: 18px 22px;
  }
  
  .feature-icon {
    width: 50px;
    height: 50px;
    font-size: 22px;
  }
  
  .feature-text h4 {
    font-size: 17px;
  }
  
  .feature-text p {
    font-size: 15px;
  }
}

@media (max-width: 1200px) {
  .login-container {
    padding: 30px;
    gap: 50px;
  }
  
  .login-left {
    padding: 30px;
  }
  
  .brand-title {
    font-size: 36px;
  }
  
  .brand-subtitle {
    font-size: 16px;
  }
  
  .feature-item {
    padding: 15px 20px;
  }
  
  .feature-icon {
    width: 45px;
    height: 45px;
    font-size: 20px;
  }
  
  .feature-text h4 {
    font-size: 16px;
  }
  
  .feature-text p {
    font-size: 14px;
  }
  
  .login-right {
    width: 500px;
    padding: 50px;
  }
  
  .login-header h2 {
    font-size: 30px;
  }
  
  .login-header p {
    font-size: 15px;
  }
  
  .form-input {
    height: 55px;
    font-size: 16px;
  }
  
  .form-label {
    font-size: 15px;
  }
  
  .login-btn {
    height: 55px;
    font-size: 17px;
  }
}

@media (max-width: 992px) {
  .login-container {
    padding: 25px;
    gap: 40px;
  }
  
  .login-left {
    padding: 25px;
  }
  
  .brand-title {
    font-size: 32px;
  }
  
  .brand-subtitle {
    font-size: 15px;
  }
  
  .feature-item {
    padding: 14px 18px;
  }
  
  .feature-icon {
    width: 42px;
    height: 42px;
    font-size: 18px;
  }
  
  .feature-text h4 {
    font-size: 15px;
  }
  
  .feature-text p {
    font-size: 13px;
  }
  
  .login-right {
    width: 450px;
    padding: 45px;
  }
  
  .login-header h2 {
    font-size: 28px;
  }
  
  .form-input {
    height: 52px;
    font-size: 15px;
  }
  
  .login-btn {
    height: 52px;
    font-size: 16px;
  }
}

@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
    padding: 20px;
    gap: 30px;
  }
  
  .login-left {
    display: none;
  }
  
  .login-right {
    width: 100%;
    max-width: 400px;
    padding: 40px;
  }
  
  .login-header h2 {
    font-size: 24px;
  }
  
  .form-input {
    height: 48px;
    font-size: 14px;
  }
  
  .form-label {
    font-size: 13px;
  }
  
  .login-btn {
    height: 48px;
    font-size: 15px;
  }
}

@media (max-width: 480px) {
  .login-right {
    padding: 30px;
  }
  
  .login-header {
    margin-bottom: 35px;
  }
  
  .login-header h2 {
    font-size: 22px;
  }
  
  .login-header p {
    font-size: 13px;
  }
  
  .form-group {
    margin-bottom: 25px;
  }
  
  .form-input {
    height: 46px;
  }
  
  .login-btn {
    height: 46px;
  }
}

/* 原始样式（保持兼容性） */
.login_title {
  margin: 0px auto 40px auto;
  color: #ffffff;
  font-size: 40px;
  font-family: 'DOUYU';
  text-align: start;
}
.login_name{
  width:520px; 
  height: 40px;
  line-height: 40px;
  background-color: transparent;
  border: none;
  border-bottom:1px solid #666666;
  color:#ffffff;
  outline: none;
}
.login_name_label{
  color: #666666;
  text-align: start;
}
</style>
