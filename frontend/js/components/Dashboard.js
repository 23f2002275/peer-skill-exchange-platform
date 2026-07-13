const Dashboard = {
    data() {
        return { data: null, error: '', loading: true }
    },
    created() {
        this.loadDashboard()
    },
    methods: {
        async loadDashboard() {
            try {
                const response = await api.get('/dashboard')
                this.data = response.data
            } catch (error) {
                this.error = 'Could not load dashboard'
            } finally {
                this.loading = false
            }
        },
        date(value) {
            return value ? new Date(value).toLocaleString() : '-'
        }
    },
    template: `
        <div class="container page-box">
            <h1 class="h2 mb-4">Dashboard</h1>
            <div class="alert alert-danger" v-if="error">{{ error }}</div>
            <div class="text-center py-5" v-if="loading">Loading...</div>
            <div v-else-if="data">
                <div class="row g-3 mb-4">
                    <div class="col-sm-6 col-lg"><div class="card stat-card p-3"><div class="text-muted">Credits</div><div class="h3 mb-0">{{ data.credit_balance }}</div></div></div>
                    <div class="col-sm-6 col-lg"><div class="card stat-card p-3"><div class="text-muted">Active offerings</div><div class="h3 mb-0">{{ data.active_offerings }}</div></div></div>
                    <div class="col-sm-6 col-lg"><div class="card stat-card p-3"><div class="text-muted">Incoming requests</div><div class="h3 mb-0">{{ data.incoming_requests }}</div></div></div>
                    <div class="col-sm-6 col-lg"><div class="card stat-card p-3"><div class="text-muted">Outgoing requests</div><div class="h3 mb-0">{{ data.outgoing_requests }}</div></div></div>
                    <div class="col-sm-6 col-lg"><div class="card stat-card p-3"><div class="text-muted">Completed</div><div class="h3 mb-0">{{ data.completed_sessions }}</div></div></div>
                </div>
                <div class="d-flex gap-2 mb-4"><router-link class="btn btn-primary" to="/discover">Find a skill</router-link><router-link class="btn btn-outline-primary" to="/new-offering">Teach a skill</router-link></div>
                <div class="card p-4">
                    <h2 class="h5 mb-3">Upcoming sessions</h2>
                    <div class="text-muted" v-if="data.upcoming_sessions.length === 0">No upcoming sessions.</div>
                    <div class="table-responsive" v-else><table class="table"><thead><tr><th>Skill</th><th>Teacher</th><th>Learner</th><th>Time</th><th>Status</th></tr></thead><tbody><tr v-for="item in data.upcoming_sessions" :key="item.id"><td>{{ item.skill_name }}</td><td>{{ item.teacher_name }}</td><td>{{ item.learner_name }}</td><td>{{ date(item.scheduled_start) }}</td><td><span class="badge bg-primary">{{ item.status }}</span></td></tr></tbody></table></div>
                </div>
            </div>
        </div>
    `
}
