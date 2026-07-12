const MyOfferings = {
    data() {
        return { items: [], error: '', loading: true }
    },
    created() {
        this.loadItems()
    },
    methods: {
        async loadItems() {
            this.loading = true
            try {
                const response = await api.get('/offerings/mine')
                this.items = response.data
            } catch (error) {
                this.error = 'Could not load your offerings'
            } finally {
                this.loading = false
            }
        },
        async changeStatus(item, status) {
            try {
                await api.patch('/offerings/' + item.id + '/status', { status })
                await this.loadItems()
            } catch (error) {
                this.error = error.response && error.response.data ? error.response.data.message : 'Could not update status'
            }
        },
        async remove(item) {
            if (!confirm('Delete this offering?')) return
            try {
                await api.delete('/offerings/' + item.id)
                await this.loadItems()
            } catch (error) {
                this.error = error.response && error.response.data ? error.response.data.message : 'Could not delete offering'
            }
        }
    },
    template: `
        <div class="container page-box">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <div><h1 class="h2 mb-1">My offerings</h1><p class="text-muted mb-0">Manage the skills you teach</p></div>
                <router-link class="btn btn-primary" to="/new-offering">Create offering</router-link>
            </div>
            <div class="alert alert-danger" v-if="error">{{ error }}</div>
            <div class="text-center py-5" v-if="loading">Loading...</div>
            <div class="card p-5 text-center" v-else-if="items.length === 0"><h2 class="h5">No offerings yet</h2><p class="text-muted">Create your first teaching offering.</p></div>
            <div class="row g-4" v-else>
                <div class="col-md-6" v-for="item in items" :key="item.id">
                    <div class="card p-4 h-100">
                        <div class="d-flex justify-content-between gap-3">
                            <div><span class="badge bg-light text-dark mb-2">{{ item.skill_name }}</span><h2 class="h5">{{ item.title }}</h2></div>
                            <span class="badge align-self-start" :class="item.status === 'ACTIVE' ? 'bg-success' : item.status === 'PAUSED' ? 'bg-warning text-dark' : 'bg-secondary'">{{ item.status }}</span>
                        </div>
                        <p class="text-muted">{{ item.proficiency_level }} · {{ item.teaching_mode }} · {{ item.duration_minutes }} minutes · {{ item.credit_cost }} credit</p>
                        <div class="d-flex flex-wrap gap-2 mt-auto">
                            <router-link class="btn btn-sm btn-outline-primary" :to="'/offerings/' + item.id + '/edit'">Edit</router-link>
                            <button class="btn btn-sm btn-outline-warning" v-if="item.status === 'ACTIVE'" @click="changeStatus(item, 'PAUSED')">Pause</button>
                            <button class="btn btn-sm btn-outline-success" v-if="item.status === 'PAUSED'" @click="changeStatus(item, 'ACTIVE')">Activate</button>
                            <button class="btn btn-sm btn-outline-secondary" v-if="item.status !== 'ARCHIVED'" @click="changeStatus(item, 'ARCHIVED')">Archive</button>
                            <button class="btn btn-sm btn-outline-danger" @click="remove(item)">Delete</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `
}
