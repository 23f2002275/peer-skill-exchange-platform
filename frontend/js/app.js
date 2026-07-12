const routes = [
    { path: '/', component: Home },
    { path: '/login', component: Login },
    { path: '/register', component: Register },
    { path: '/discover', component: Discover },
    { path: '/offerings/:id', component: OfferingDetails },
    { path: '/new-offering', component: ManageOffering, meta: { auth: true, role: 'member' } },
    { path: '/offerings/:id/edit', component: ManageOffering, meta: { auth: true, role: 'member' } },
    { path: '/my-offerings', component: MyOfferings, meta: { auth: true, role: 'member' } },
    { path: '/dashboard', component: Dashboard, meta: { auth: true } },
    { path: '/requests', component: Requests, meta: { auth: true, role: 'member' } },
    { path: '/sessions', component: Sessions, meta: { auth: true, role: 'member' } },
    { path: '/wallet', component: Wallet, meta: { auth: true, role: 'member' } },
    { path: '/profile', component: Profile, meta: { auth: true, role: 'member' } },
    { path: '/admin', component: AdminDashboard, meta: { auth: true, role: 'admin' } }
]

const router = new VueRouter({ routes })

router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('skill_exchange_token')
    const user = JSON.parse(localStorage.getItem('skill_exchange_user') || 'null')
    const role = user && user.roles ? user.roles[0] : null

    if (to.matched.some(record => record.meta.auth) && !token) {
        next('/login')
        return
    }

    const neededRole = to.matched.find(record => record.meta.role)
    if (neededRole && neededRole.meta.role !== role) {
        next('/dashboard')
        return
    }

    next()
})

new Vue({
    el: '#app',
    router,
    data: {
        token: localStorage.getItem('skill_exchange_token'),
        user: JSON.parse(localStorage.getItem('skill_exchange_user') || 'null')
    },
    computed: {
        isLoggedIn() {
            return Boolean(this.token)
        },
        role() {
            return this.user && this.user.roles ? this.user.roles[0] : null
        }
    },
    created() {
        if (this.token) {
            this.loadUser()
        }
    },
    methods: {
        setAuth(token, user) {
            this.token = token
            this.user = user
            localStorage.setItem('skill_exchange_token', token)
            localStorage.setItem('skill_exchange_user', JSON.stringify(user))
        },
        updateUser(user) {
            this.user = user
            localStorage.setItem('skill_exchange_user', JSON.stringify(user))
        },
        async loadUser() {
            try {
                const response = await api.get('/auth/me')
                this.updateUser(response.data)
            } catch (error) {
                this.clearAuth()
            }
        },
        clearAuth() {
            this.token = null
            this.user = null
            localStorage.removeItem('skill_exchange_token')
            localStorage.removeItem('skill_exchange_user')
        },
        async logout() {
            try {
                await api.post('/auth/logout')
            } catch (error) {
            }
            this.clearAuth()
            this.$router.push('/login')
        }
    }
})
