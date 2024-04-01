<template>
    <el-row class="login-container">
        <el-col :lg="16" :md="12" class="left">
            <div>
            <div>OSPF监控系统</div>
            <div>Author:KenyonZ</div>
            </div>
        </el-col>
        <el-col :lg="8" :md="12" class="right">
            <h2>内部开发版</h2>
            <div>
                <span class="line"></span>
                <span>账号密码登录</span>
                <span class="line"></span>
            </div>
            <el-form ref="formRef" :rules="rules" :model="form" class="w-[250px]">
                <el-form-item prop="username">
                    <el-input v-model="form.username" placeholder="请输入用户名" >
                        <template #prefix>
                            <el-icon><user /></el-icon>
                        </template>
                    </el-input>
                </el-form-item>
                <el-form-item prop="password">
                    <el-input v-model="form.password" placeholder="请输入密码" show-password>
                        <template #prefix>
                            <el-icon><lock /></el-icon>
                        </template>    
                    </el-input>
                </el-form-item>
                <el-form-item>
                    <el-button round color="#626aef" class="w-[250px]" type="primary" @click="onSubmit">登 录</el-button>
                </el-form-item>
            </el-form>
        </el-col>
    </el-row>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { User,Lock } from '@element-plus/icons-vue'
import { login } from '~/api/manager'
import {ElNotification} from 'element-plus'
import { useRouter } from 'vue-router'
import { setToken } from '~/composables/auth'

const router = useRouter()

const form = reactive({
  username: "",
  password: "",
})

const rules = {
    username: [
        { required: true, message: '用户名不能为空', trigger: 'blur' },
        { min:6, required: true, message: '用户名长度最低为6位', trigger: 'blur' },
    ],
    password: [
        { required: true, message: '密码不能为空', trigger: 'blur' },
        { min:6, required: true, message: '密码长度最低为6位', trigger: 'blur' },
    ],
}

const formRef = ref(null)

const onSubmit = () => {
    formRef.value.validate((valid) => {
        if (!valid) {
            return false
        } else {
            login(form.username, form.password)
            .then(res => {
                ElNotification({
                    message: "登录成功",
                    type: 'success',
                    duration: 2000
                })
                setToken(res.token)
                router.push("/")
            })
            .catch(err => {
                ElNotification({
                    message: err.response.data.msg || "请求失败",
                    type: 'error',
                    duration: 2000
                })
            })  
        }
    })
}
</script>

<style scoped>
.login-container {
    @apply min-h-screen bg-indigo-500;
}

.login-container .left, .login-container .right {
    @apply flex items-center justify-center;
}
.login-container .right {
    @apply bg-light-50 flex-col;
}
.left>div>div:first-child{
    @apply font-bold text-5xl text-light-50 mb-4;
}
.left>div>div:last-child{
    @apply  text-light-200 text-sm;
}
.right>h2{
    @apply font-bold text-3xl text-gray-800;
}
.right>div{
    @apply flex items-center justify-center my-5 text-gray-300 space-x-2;
}

.right .line{
    @apply h-[1px] w-16 bg-gray-200;
}
</style>


