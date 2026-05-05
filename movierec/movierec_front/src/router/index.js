import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/HomePage.vue'
import Login from '../views/LoginPage.vue'
import Register from '../views/RegisterPage.vue'
import MovieDetail from '../views/MovieDetailPage.vue'
import Recommend from '../views/RecommendPage.vue'
import Search from '../views/SearchPage.vue'
import Visualize from '../views/VisualizePage.vue'
import WordCloud from '../views/WordCloudPage.vue'
import Profile from '../views/ProfilePage.vue'
import MyActivity from '../views/MyActivityPage.vue'
import AdminPage from '../views/admin/AdminPage.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/home', name: 'home', component: Home },
  { path: '/movie/:id', name: 'movie_detail', component: MovieDetail, props: true },
  { path: '/recommend', name: 'recommend', component: Recommend },
  { path: '/search', name: 'search', component: Search },
  { path: '/visualize', name: 'visualize', component: Visualize },
  { path: '/wordcloud', name: 'wordcloud', component: WordCloud },
  { path: '/profile', name: 'profile', component: Profile },
  { path: '/activity', name: 'activity', component: MyActivity },
  { path: '/admin', name: 'admin', component: AdminPage },
  { path: '/login', name: 'login', component: Login },
  { path: '/register', name: 'register', component: Register },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const publicPages = ['login', 'register']
  const authRequired = !publicPages.includes(to.name)
  const loggedIn = !!localStorage.getItem('access')

  if (authRequired && !loggedIn) {
    return next('/login')
  }

  // 仅标记为管理员的账号可访问 /admin
  if (to.name === 'admin') {
    const isAdmin = localStorage.getItem('is_admin') === '1'
    if (!isAdmin) {
      return next('/home')
    }
  }

  next()
})

export default router
