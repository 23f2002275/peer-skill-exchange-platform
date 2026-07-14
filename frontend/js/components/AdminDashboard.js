const AdminDashboard = {
    data() {
        return {
            stats: {}, users: [], categories: [], skills: [], offerings: [], reports: [],
            categoryForm: { name: '', description: '' },
            skillForm: { name: '', category_id: '', description: '' },
            error: '', success: '', loading: true
        }
    },
    created() {
        this.loadAll()
    },
    methods: {
        async loadAll() {
            this.loading = true
            try {
                const responses = await Promise.all([
                    api.get('/admin/statistics'), api.get('/admin/users'), api.get('/skills/categories'),
                    api.get('/skills'), api.get('/admin/offerings'), api.get('/admin/reports')
                ])
                this.stats = responses[0].data
                this.users = responses[1].data
                this.categories = responses[2].data
                this.skills = responses[3].data
                this.offerings = responses[4].data
                this.reports = responses[5].data
            } catch (error) {
                this.error = 'Could not load admin data'
            } finally {
                this.loading = false
            }
        },
        async createCategory() {
            await this.run(() => api.post('/admin/categories', this.categoryForm))
            this.categoryForm = { name: '', description: '' }
        },
        async createSkill() {
            await this.run(() => api.post('/admin/skills', this.skillForm))
            this.skillForm = { name: '', category_id: '', description: '' }
        },
        async toggleUser(user) {
            await this.run(() => api.patch('/admin/users/' + user.id + '/active', { active: !user.active }))
        },
        async adjust(user) {
            const amount = prompt('Credit amount, for example 2 or -1')
            if (amount === null) return
            const reason = prompt('Reason for adjustment')
            if (!reason) return
            await this.run(() => api.post('/admin/users/' + user.id + '/credit-adjustments', { amount, reason }))
        },
        async toggleOffering(item) {
            await this.run(() => api.patch('/admin/offerings/' + item.id + '/visibility', { visible: item.status === 'HIDDEN' }))
        },
        async resolve(report, status) {
            const notes = prompt('Admin notes') || ''
            await this.run(() => api.patch('/admin/reports/' + report.id, { status, admin_notes: notes }))
        },
        async run(call) {
            this.error = ''
            this.success = ''
            try {
                const response = await call()
                this.success = response.data.message
                await this.loadAll()
            } catch (error) {
                this.error = error.response && error.response.data ? error.response.data.message : 'Action failed'
            }
        },
        date(value) {
            return value ? new Date(value).toLocaleString() : '-'
        }
    },
    template: `
        <div class="container page-box">
            <h1 class="h2 mb-4">Admin dashboard</h1>
            <div class="alert alert-danger" v-if="error">{{ error }}</div><div class="alert alert-success" v-if="success">{{ success }}</div>
            <div class="text-center py-5" v-if="loading">Loading...</div>
            <div v-else>
                <div class="row g-3 mb-4"><div class="col-6 col-md" v-for="(value, key) in stats"><div class="card p-3"><div class="text-muted text-capitalize">{{ key.split('_').join(' ') }}</div><div class="h3 mb-0">{{ value }}</div></div></div></div>
                <div class="row g-4 mb-4">
                    <div class="col-lg-6"><div class="card p-4"><h2 class="h5">Create category</h2><div class="row g-2"><div class="col-md-5"><input class="form-control" placeholder="Category name" v-model.trim="categoryForm.name"></div><div class="col-md-5"><input class="form-control" placeholder="Description" v-model.trim="categoryForm.description"></div><div class="col-md-2"><button class="btn btn-primary w-100" @click="createCategory">Add</button></div></div></div></div>
                    <div class="col-lg-6"><div class="card p-4"><h2 class="h5">Create skill</h2><div class="row g-2"><div class="col-md-4"><input class="form-control" placeholder="Skill name" v-model.trim="skillForm.name"></div><div class="col-md-4"><select class="form-select" v-model="skillForm.category_id"><option value="" disabled>Category</option><option v-for="item in categories" :value="item.id">{{ item.name }}</option></select></div><div class="col-md-2"><input class="form-control" placeholder="Info" v-model.trim="skillForm.description"></div><div class="col-md-2"><button class="btn btn-primary w-100" @click="createSkill">Add</button></div></div></div></div>
                </div>
                <div class="card p-4 mb-4"><h2 class="h5 mb-3">Users</h2><div class="table-responsive"><table class="table"><thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Credits</th><th>Status</th><th></th></tr></thead><tbody><tr v-for="user in users" :key="user.id"><td>{{ user.name }}</td><td>{{ user.email }}</td><td>{{ user.roles.join(', ') }}</td><td>{{ user.credit_balance }}</td><td>{{ user.active ? 'Active' : 'Suspended' }}</td><td class="text-end"><button class="btn btn-sm btn-outline-warning me-2" @click="adjust(user)">Credits</button><button class="btn btn-sm" :class="user.active ? 'btn-outline-danger' : 'btn-outline-success'" @click="toggleUser(user)">{{ user.active ? 'Suspend' : 'Activate' }}</button></td></tr></tbody></table></div></div>
                <div class="card p-4 mb-4"><h2 class="h5 mb-3">Offerings</h2><div class="table-responsive"><table class="table"><thead><tr><th>Title</th><th>Teacher</th><th>Skill</th><th>Status</th><th></th></tr></thead><tbody><tr v-for="item in offerings" :key="item.id"><td>{{ item.title }}</td><td>{{ item.teacher_name }}</td><td>{{ item.skill_name }}</td><td>{{ item.status }}</td><td class="text-end"><button class="btn btn-sm" :class="item.status === 'HIDDEN' ? 'btn-outline-success' : 'btn-outline-danger'" @click="toggleOffering(item)">{{ item.status === 'HIDDEN' ? 'Restore' : 'Hide' }}</button></td></tr></tbody></table></div></div>
                <div class="card p-4"><h2 class="h5 mb-3">Reports</h2><div class="text-muted" v-if="reports.length === 0">No reports.</div><div class="table-responsive" v-else><table class="table"><thead><tr><th>Reporter</th><th>Reason</th><th>Entity</th><th>Status</th><th>Created</th><th></th></tr></thead><tbody><tr v-for="item in reports" :key="item.id"><td>{{ item.reporter_name }}</td><td>{{ item.reason }}</td><td>User {{ item.reported_user_id || '-' }} / Offering {{ item.offering_id || '-' }} / Session {{ item.session_id || '-' }}</td><td>{{ item.status }}</td><td>{{ date(item.created_at) }}</td><td class="text-end" v-if="item.status === 'OPEN'"><button class="btn btn-sm btn-outline-success me-2" @click="resolve(item, 'RESOLVED')">Resolve</button><button class="btn btn-sm btn-outline-secondary" @click="resolve(item, 'DISMISSED')">Dismiss</button></td></tr></tbody></table></div></div>
            </div>
        </div>
    `
}
