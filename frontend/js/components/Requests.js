const Requests = {
    data() {
        return {
            incoming: [],
            outgoing: [],
            tab: 'incoming',
            schedules: {},
            error: '',
            success: '',
            loading: true
        }
    },
    created() {
        this.loadRequests()
    },
    methods: {
        async loadRequests() {
            this.loading = true
            try {
                const response = await api.get('/requests/mine')
                this.incoming = response.data.incoming
                this.outgoing = response.data.outgoing
                this.incoming.forEach(item => { if (!this.schedules[item.id]) this.$set(this.schedules, item.id, { scheduled_start: '', meeting_details: '' }) })
            } catch (error) {
                this.error = 'Could not load requests'
            } finally {
                this.loading = false
            }
        },
        async action(item, name) {
            this.error = ''
            this.success = ''
            try {
                const response = await api.patch('/requests/' + item.id + '/' + name)
                this.success = response.data.message
                await this.loadRequests()
            } catch (error) {
                this.error = error.response && error.response.data ? error.response.data.message : 'Action failed'
            }
        },
        async schedule(item) {
            const form = this.schedules[item.id] || {}
            if (!form.scheduled_start) {
                this.error = 'Choose a session time'
                return
            }
            try {
                const response = await api.post('/requests/' + item.id + '/session', form)
                this.success = response.data.message
                await this.loadRequests()
            } catch (error) {
                this.error = error.response && error.response.data ? error.response.data.message : 'Could not schedule session'
            }
        },
        date(value) {
            return value ? new Date(value).toLocaleString() : '-'
        },
        statusClass(status) {
            if (['COMPLETED', 'ACCEPTED', 'SCHEDULED'].includes(status)) return 'bg-success'
            if (['REJECTED', 'CANCELLED'].includes(status)) return 'bg-secondary'
            return 'bg-warning text-dark'
        }
    },
    template: `
        <div class="container page-box">
            <h1 class="h2 mb-4">Session requests</h1>
            <div class="alert alert-danger" v-if="error">{{ error }}</div>
            <div class="alert alert-success" v-if="success">{{ success }}</div>
            <ul class="nav nav-tabs mb-4"><li class="nav-item"><button class="nav-link" :class="{active: tab === 'incoming'}" @click="tab = 'incoming'">Incoming ({{ incoming.length }})</button></li><li class="nav-item"><button class="nav-link" :class="{active: tab === 'outgoing'}" @click="tab = 'outgoing'">Outgoing ({{ outgoing.length }})</button></li></ul>
            <div class="text-center py-5" v-if="loading">Loading...</div>
            <div v-else>
                <div class="card p-4 mb-3" v-for="item in (tab === 'incoming' ? incoming : outgoing)" :key="item.id">
                    <div class="d-flex justify-content-between flex-wrap gap-2"><div><h2 class="h5 mb-1">{{ item.offering_title }}</h2><div class="text-muted">{{ item.skill_name }} · {{ tab === 'incoming' ? 'Learner: ' + item.learner_name : 'Teacher: ' + item.teacher_name }}</div></div><span class="badge align-self-start" :class="statusClass(item.status)">{{ item.status }}</span></div>
                    <p class="mt-3 mb-1" v-if="item.message">{{ item.message }}</p>
                    <div class="small text-muted">Preferred: {{ date(item.preferred_time) }} · Requested: {{ date(item.requested_at) }}</div>
                    <div class="d-flex flex-wrap gap-2 mt-3" v-if="tab === 'incoming' && item.status === 'PENDING'"><button class="btn btn-sm btn-success" @click="action(item, 'accept')">Accept</button><button class="btn btn-sm btn-outline-danger" @click="action(item, 'reject')">Reject</button></div>
                    <div class="row g-2 mt-2" v-if="tab === 'incoming' && item.status === 'ACCEPTED'"><div class="col-md-5"><input type="datetime-local" class="form-control" v-model="schedules[item.id].scheduled_start"></div><div class="col-md-5"><input class="form-control" placeholder="Meeting link or room" v-model="schedules[item.id].meeting_details"></div><div class="col-md-2"><button class="btn btn-primary w-100" @click="schedule(item)">Schedule</button></div></div>
                    <div class="mt-3" v-if="['PENDING', 'ACCEPTED'].includes(item.status)"><button class="btn btn-sm btn-outline-secondary" @click="action(item, 'cancel')">Cancel</button></div>
                    <router-link class="btn btn-sm btn-outline-primary mt-3 align-self-start" :to="'/sessions'" v-if="item.session_id">View session</router-link>
                </div>
                <div class="card p-5 text-center" v-if="(tab === 'incoming' ? incoming : outgoing).length === 0">No requests in this section.</div>
            </div>
        </div>
    `
}
