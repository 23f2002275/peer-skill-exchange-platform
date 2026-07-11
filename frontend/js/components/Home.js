const Home = {
    data() {
        return {
            offerings: []
        }
    },
    created() {
        this.load()
    },
    methods: {
        async load() {
            try {
                const response = await api.get('/offerings?per_page=3')
                this.offerings = response.data.items
            } catch (error) {
                this.offerings = []
            }
        }
    },
    template: `
        <div>
            <section class="hero">
                <div class="container text-center">
                    <h1 class="display-4 fw-bold">Learn from peers. Teach what you know.</h1>
                    <p class="lead mt-3">Exchange practical skills using sessions, credits and verified reviews.</p>
                    <router-link class="btn btn-primary btn-lg mt-3" to="/discover">Discover skills</router-link>
                </div>
            </section>
            <section class="container py-5">
                <div class="row g-4 mb-5">
                    <div class="col-md-4"><div class="card p-4 text-center"><h3>Publish</h3><p class="mb-0">List a skill that you can teach</p></div></div>
                    <div class="col-md-4"><div class="card p-4 text-center"><h3>Schedule</h3><p class="mb-0">Accept requests and fix a session time</p></div></div>
                    <div class="col-md-4"><div class="card p-4 text-center"><h3>Exchange</h3><p class="mb-0">Complete sessions and earn credits</p></div></div>
                </div>
                <div class="d-flex justify-content-between align-items-center mb-3"><h2 class="h4 mb-0">Featured offerings</h2><router-link to="/discover">View all</router-link></div>
                <div class="row g-4">
                    <div class="col-md-4" v-for="item in offerings" :key="item.id">
                        <div class="card offering-card p-4">
                            <span class="badge bg-primary align-self-start mb-3">{{ item.skill_name }}</span>
                            <h3 class="h5">{{ item.title }}</h3>
                            <p class="text-muted">{{ item.teacher_name }} · {{ item.teacher_rating }}/5</p>
                            <p>{{ item.duration_minutes }} minutes · {{ item.credit_cost }} credit</p>
                            <router-link class="btn btn-outline-primary mt-auto" :to="'/offerings/' + item.id">View details</router-link>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    `
}
