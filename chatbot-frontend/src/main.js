import Vue from 'vue'
import App from './App.vue'
import VueChatScroll from 'vue-chat-scroll'
import { BootstrapVue} from 'bootstrap-vue'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
//import "bootstrap/dist/css/bootstrap.min.css";
import VueRouter from "vue-router";
import axios from 'axios'
Vue.use(BootstrapVue)
Vue.use(VueRouter)
Vue.use(VueChatScroll)
Vue.config.productionTip = false

new Vue({
  render: h => h(App),
}).$mount('#app')

Vue.prototype.$axios = axios