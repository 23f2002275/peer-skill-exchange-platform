const Sessions = {
    data() {
        return { items: [], reviews: {}, error: '', success: '', loading: true }
    },
    created() {
        this.loadSessions()
    },
    methods: {
        async loadSessions() {
            this.loading = true
            try {
                const response = await api.get('/sessions/mine')
                this.items = response.data
                this.items.forEach(item => { if (!this.reviews[item.id]) this.$set(this.reviews, item.id, { rating: '', comment: '' }) })
            } catch (error) {
                this.error = 'Could not load sessions'
            } finally {
                this.loading = false
            }
        },
        async action(item, name) {
            try {
                const response = await api.patch('/sessions/' + item.id + '/' + name)
                this.success = response.data.message
                await this.loadSessions()
                await this.$root.loadUser()
            } catch (error) {
                this.error = error.response && error.response.data ? error.response.data.message : 'Action failed'
            }
        },
        async review(item) {
            const form = this.reviews[item.id] || {}
            try {
                const response = await api.post('/sessions/' + item.id + '/reviews', form)
                this.success = response.data.message
                await this.loadSessions()
            } catch (error) {
                this.error = error.response && error.response.data ? error.response.data.message : 'Could not submit review'
            }
        },
        date(value) {
            return value ? new Date(value).toLocaleString() : '-'
        },
        canReview(item) {
            return item.status === 'COMPLETED' && !item.reviewed_by.includes(this.$root.user.id)
        },
        confirmationText(item) {
            if (this.$root.user.id === item.teacher_id) return item.teacher_confirmed ? 'You confirmed' : 'Confirm completion'
            return item.learner_confirmed ? 'You confirmed' : 'Confirm completion'
        },
        alreadyConfirmed(item) {
            return this.$root.user.id === item.teacher_id ? item.teacher_confirmed : item.learner_confirmed
        }
    },
    template: `
        <div class="container page-box">
            <h1 class="h2 mb-4">My sessions</h1>
            <div class="alert alert-danger" v-if="error">{{ error }}</div>
            <div class="alert alert-success" v-if="success">{{ success }}</div>
            <div class="text-center py-5" v-if="loading">Loading...</div>
            <div class="card p-5 text-center" v-else-if="items.length === 0">No sessions scheduled.</div>
            <div class="card p-4 mb-3" v-else v-for="item in items" :key="item.id">
                <div class="d-flex justify-content-between flex-wrap gap-2"><div><h2 class="h5 mb-1">{{ item.offering_title }}</h2><div class="text-muted">{{ item.skill_name }} · {{ item.teacher_name }} with {{ item.learner_name }}</div></div><span class="badge bg-primary align-self-start">{{ item.status }}</span></div>
                <div class="row mt-3"><div class="col-md-4"><strong>Time</strong><div>{{ date(item.scheduled_start) }}</div></div><div class="col-md-4"><strong>Duration</strong><div>{{ item.duration_minutes }} minutes</div></div><div class="col-md-4"><strong>Meeting details</strong><div>{{ item.meeting_details || 'Not provided' }}</div></div></div>
                <div class="small text-muted mt-3">Teacher confirmation: {{ item.teacher_confirmed ? 'Done' : 'Pending' }} · Learner confirmation: {{ item.learner_confirmed ? 'Done' : 'Pending' }}</div>
                <div class="d-flex flex-wrap gap-2 mt-3" v-if="['SCHEDULED', 'AWAITING_CONFIRMATION'].includes(item.status)"><button class="btn btn-success btn-sm" :disabled="alreadyConfirmed(item)" @click="action(item, 'confirm')">{{ confirmationText(item) }}</button><button class="btn btn-outline-danger btn-sm" @click="action(item, 'cancel')">Cancel session</button></div>
                <div class="row g-2 mt-3" v-if="canReview(item)"><div class="col-md-2"><select class="form-select" v-model.number="reviews[item.id].rating"><option disabled value="">Rating</option><option v-for="n in 5" :value="n">{{ n }}</option></select></div><div class="col-md-8"><input class="form-control" placeholder="Share your feedback" v-model="reviews[item.id].comment"></div><div class="col-md-2"><button class="btn btn-primary w-100" @click="review(item)">Review</button></div></div>
            </div>
        </div>
    `
}
