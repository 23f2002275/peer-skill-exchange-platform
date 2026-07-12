const OfferingDetails = {
    data() {
        return {
            item: null,
            form: { message: '', preferred_time: '' },
            report: { reason: '', details: '' },
            error: '',
            success: '',
            loading: true
        }
    },
    created() {
        this.load()
    },
    methods: {
        async load() {
            try {
                const response = await api.get('/offerings/' + this.$route.params.id)
                this.item = response.data
            } catch (error) {
                this.error = error.response && error.response.data ? error.response.data.message : 'Offering not found'
            } finally {
                this.loading = false
            }
        },
        async requestSession() {
            this.error = ''
            this.success = ''
            if (!this.$root.isLoggedIn) {
                this.$router.push('/login')
                return
            }
            try {
                const response = await api.post('/offerings/' + this.item.id + '/requests', this.form)
                this.success = response.data.message
                this.form = { message: '', preferred_time: '' }
            } catch (error) {
                this.error = error.response && error.response.data ? error.response.data.message : 'Request failed'
            }
        },
        async submitReport() {
            try {
                const response = await api.post('/reports', {
                    offering_id: this.item.id,
                    reported_user_id: this.item.teacher_id,
                    reason: this.report.reason,
                    details: this.report.details
                })
                this.success = response.data.message
                this.report = { reason: '', details: '' }
            } catch (error) {
                this.error = error.response && error.response.data ? error.response.data.message : 'Report failed'
            }
        }
    },
    template: `
        <div class="container page-box">
            <div class="text-center py-5" v-if="loading">Loading...</div>
            <div class="alert alert-danger" v-if="error">{{ error }}</div>
            <div class="alert alert-success" v-if="success">{{ success }}</div>
            <div class="row g-4" v-if="item">
                <div class="col-lg-8">
                    <div class="card p-4 p-md-5">
                        <div class="d-flex gap-2 mb-3"><span class="badge bg-primary">{{ item.skill_name }}</span><span class="badge bg-secondary">{{ item.proficiency_level }}</span></div>
                        <h1 class="h2">{{ item.title }}</h1>
                        <p class="text-muted">Taught by {{ item.teacher_name }} · {{ item.teacher_rating }}/5</p>
                        <p class="lead">{{ item.description || 'No description provided.' }}</p>
                        <hr>
                        <div class="row g-3"><div class="col-md-4"><strong>Mode</strong><div>{{ item.teaching_mode }}</div></div><div class="col-md-4"><strong>Duration</strong><div>{{ item.duration_minutes }} minutes</div></div><div class="col-md-4"><strong>Cost</strong><div>{{ item.credit_cost }} credits</div></div><div class="col-12"><strong>Availability</strong><div>{{ item.availability_text || 'Contact through a request' }}</div></div></div>
                    </div>
                    <div class="card p-4 mt-4" v-if="$root.role === 'member' && item.teacher_id !== $root.user.id">
                        <h2 class="h5">Report this offering</h2>
                        <form class="row g-3" @submit.prevent="submitReport"><div class="col-md-4"><input class="form-control" placeholder="Reason" v-model.trim="report.reason" required></div><div class="col-md-6"><input class="form-control" placeholder="Details" v-model.trim="report.details"></div><div class="col-md-2"><button class="btn btn-outline-danger w-100">Report</button></div></form>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="card p-4" v-if="$root.role === 'member' && item.teacher_id !== $root.user.id">
                        <h2 class="h5">Request a session</h2>
                        <p class="text-muted">Your balance: {{ $root.user.credit_balance }} credits</p>
                        <form @submit.prevent="requestSession"><div class="mb-3"><label class="form-label">Message</label><textarea class="form-control" rows="3" v-model.trim="form.message"></textarea></div><div class="mb-3"><label class="form-label">Preferred time</label><input class="form-control" type="datetime-local" v-model="form.preferred_time"></div><button class="btn btn-primary w-100">Send request</button></form>
                    </div>
                    <div class="card p-4" v-else-if="!$root.isLoggedIn"><p>Login to request this session.</p><router-link class="btn btn-primary" to="/login">Login</router-link></div>
                    <div class="card p-4" v-else><p class="mb-0">This is your own offering.</p></div>
                </div>
            </div>
        </div>
    `
}
