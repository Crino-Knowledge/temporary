<template>
  <div id="login-page">
    <el-form class="login-container" label-position="left" label-width="0px">
      <p class="login_title">视频检测AI算法中台</p>
      <el-form-item>
        <p class="login_name_label">用户名称</p>
        <input type="text" class="login_name" auto-complete="off" placeholder="请输入用户名" v-model="loginForm.username" >

      </el-form-item>
      <el-form-item >
        <p class="login_name_label">密码</p>
        <div class="relative">
          <input :type="isShowEye?'text':'password'" class="login_name"  auto-complete="off"  @keyup.enter="login" placeholder="请输入密码" v-model="loginForm.password" >
          <img class="eye_img" v-if="isShowEye" src="@/assets/login/show@2x.png" @click="isShowEye=!isShowEye" alt="">
          <img class="eye_img" v-if="!isShowEye" src="@/assets/login/noshow@2x.png" @click="isShowEye=!isShowEye" alt="">
        </div>
        
      </el-form-item>
      <el-form-item class="flex_row_start_center">
        <el-button
          type="primary"
          @click="login"
          :loading="isLoading"
          style="width:170px;"
          >登录</el-button
        >
      </el-form-item>
    </el-form>
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
      isLoading:false,
      isShowEye:false
    };
  },
  methods: {
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
  },
};
</script>

<style scoped>
#login-page {
  background: url("../assets/login/bg@2x.png") no-repeat;
  background-position: center;
  height: 100%;
  width: 100%;
  background-size: cover;
  position: fixed;
}
.login-container {
  position: fixed;
  left: 147px;
  top: 50%;
  transform: translateY(-50%);
  
}

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
.eye_img{
  position: absolute;
  right: 10px;
  /* bottom: 10px; */
  top: 50%;
  transform: translateY(-50%);
  width: 34px;
}
</style>

