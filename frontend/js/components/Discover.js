const Discover = {
    data() {
        return {
            items: [],
            categories: [],
            skills: [],
            filters: { keyword: '', category_id: '', skill_id: '', mode: '', level: '' },
            page: 1,
            pages: 1,
            total: 0,
            loading: false,
            error: ''
        }
    },
    created() {
        this.loadCatalog()
        this.loadOfferings()
    },
    methods: {
        async loadCatalog() {
            try {
                const [categories, skills] = await Promise.all([api.get('/skills/categories'), api.get('/skills')])
                this.categories = categories.data
                this.skills = skills.data
            } catch (error) {
                this.categories = []
                this.skills = []
            }
        },
        async loadOfferings(page = 1) {
            this.loading = true
            this.error = ''
            try {
                const params = Object.assign({}, this.filters, { page, per_page: 9 })
                const response = await api.get('/offerings', { params })
                this.items = response.data.items
                this.page = response.data.page
                this.pages = response.data.pages
                this.total = response.data.total
            } catch (error) {
                this.error = 'Could not load offerings'
            } finally {
                this.loading = false
            }
        },
        clearFilters() {
            this.filters = { keyword: '', category_id: '', skill_id: '', mode: '', level: '' }
            this.loadOfferings(1)
        }
    },
    template: `
        <div class="container page-box">
            <div class="d-flex justify-content-between align-items-center mb-4"><div><h1 class="h2">Discover skills</h1><p class="text-muted mb-0">{{ total }} active offerings</p></div><router-link class="btn btn-primary" to="/new-offering" v-if="$root.role === 'member'">Teach a skill</router-link></div>
            <div class="card p-4 mb-4">
                <form class="row g-3" @submit.prevent="loadOfferings(1)">
                    <div class="col-md-3"><input class="form-control" placeholder="Search" v-model.trim="filters.keyword"></div>
                    <div class="col-md-2"><select class="form-select" v-model="filters.category_id"><option value="">All categories</option><option v-for="item in categories" :value="item.id">{{ item.name }}</option></select></div>
                    <div class="col-md-2"><select class="form-select" v-model="filters.skill_id"><option value="">All skills</option><option v-for="item in skills" :value="item.id">{{ item.name }}</option></select></div>
                    <div class="col-md-2"><select class="form-select" v-model="filters.mode"><option value="">Any mode</option><option>Online</option><option>Offline</option><option>Hybrid</option></select></div>
                    <div class="col-md-1"><select class="form-select" v-model="filters.level"><option value="">Level</option><option>Beginner</option><option>Intermediate</option><option>Advanced</option></select></div>
                    <div class="col-md-2 d-flex gap-2"><button class="btn btn-primary flex-fill">Search</button><button type="button" class="btn btn-outline-secondary" @click="clearFilters">Clear</button></div>
                </form>
            </div>
            <div class="alert alert-danger" v-if="error">{{ error }}</div>
            <div class="text-center py-5" v-if="loading">Loading...</div>
            <div class="card p-5 text-center" v-else-if="!items.length">No offerings found.</div>
            <div class="row g-4" v-else>
                <div class="col-md-6 col-lg-4" v-for="item in items" :key="item.id">
                    <div class="card offering-card p-4">
                        <div class="d-flex justify-content-between mb-3"><span class="badge bg-primary">{{ item.skill_name }}</span><span class="badge bg-light text-dark">{{ item.proficiency_level }}</span></div>
                        <h2 class="h5">{{ item.title }}</h2>
                        <p class="text-muted">{{ item.teacher_name }} · {{ item.teacher_rating }}/5</p>
                        <p>{{ item.teaching_mode }} · {{ item.duration_minutes }} minutes</p>
                        <p class="fw-semibold">{{ item.credit_cost }} credit{{ item.credit_cost > 1 ? 's' : '' }}</p>
                        <router-link class="btn btn-outline-primary mt-auto" :to="'/offerings/' + item.id">View details</router-link>
                    </div>
                </div>
            </div>
            <div class="d-flex justify-content-center gap-2 mt-4" v-if="pages > 1"><button class="btn btn-outline-primary" :disabled="page <= 1" @click="loadOfferings(page - 1)">Previous</button><span class="align-self-center">Page {{ page }} of {{ pages }}</span><button class="btn btn-outline-primary" :disabled="page >= pages" @click="loadOfferings(page + 1)">Next</button></div>
        </div>
    `
}
