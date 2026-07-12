const ManageOffering = {
    data() {
        return {
            skills: [],
            form: { skill_id: '', title: '', description: '', proficiency_level: 'Beginner', teaching_mode: 'Online', duration_minutes: 60, availability_text: '', credit_cost: 1 },
            editing: Boolean(this.$route.params.id),
            error: '',
            loading: false
        }
    },
    created() {
        this.loadSkills()
        if (this.editing) this.loadOffering()
    },
    methods: {
        async loadSkills() {
            try {
                const response = await api.get('/skills')
                this.skills = response.data
            } catch (error) {
                this.error = 'Could not load skills'
            }
        },
        async loadOffering() {
            try {
                const response = await api.get('/offerings/' + this.$route.params.id)
                const item = response.data
                this.form = { skill_id: item.skill_id, title: item.title, description: item.description || '', proficiency_level: item.proficiency_level, teaching_mode: item.teaching_mode, duration_minutes: item.duration_minutes, availability_text: item.availability_text || '', credit_cost: item.credit_cost }
            } catch (error) {
                this.error = 'Could not load offering'
            }
        },
        async submit() {
            this.error = ''
            this.loading = true
            try {
                if (this.editing) await api.put('/offerings/' + this.$route.params.id, this.form)
                else await api.post('/offerings', this.form)
                this.$router.push('/my-offerings')
            } catch (error) {
                this.error = error.response && error.response.data ? error.response.data.message : 'Could not save offering'
            } finally {
                this.loading = false
            }
        }
    },
    template: `
        <div class="container page-box">
            <div class="card p-4 p-md-5">
                <h1 class="h3 mb-4">{{ editing ? 'Edit offering' : 'Create offering' }}</h1>
                <div class="alert alert-danger" v-if="error">{{ error }}</div>
                <form @submit.prevent="submit">
                    <div class="row g-3">
                        <div class="col-md-4"><label class="form-label">Skill</label><select class="form-select" v-model="form.skill_id" required><option value="" disabled>Select skill</option><option v-for="skill in skills" :value="skill.id">{{ skill.name }} · {{ skill.category_name }}</option></select></div>
                        <div class="col-md-8"><label class="form-label">Title</label><input class="form-control" v-model.trim="form.title" required></div>
                        <div class="col-12"><label class="form-label">Description</label><textarea class="form-control" rows="4" v-model.trim="form.description"></textarea></div>
                        <div class="col-md-3"><label class="form-label">Level</label><select class="form-select" v-model="form.proficiency_level"><option>Beginner</option><option>Intermediate</option><option>Advanced</option></select></div>
                        <div class="col-md-3"><label class="form-label">Mode</label><select class="form-select" v-model="form.teaching_mode"><option>Online</option><option>Offline</option><option>Hybrid</option></select></div>
                        <div class="col-md-3"><label class="form-label">Duration</label><input class="form-control" type="number" min="15" max="240" v-model.number="form.duration_minutes" required></div>
                        <div class="col-md-3"><label class="form-label">Credit cost</label><input class="form-control" type="number" min="1" max="5" v-model.number="form.credit_cost" required></div>
                        <div class="col-12"><label class="form-label">Availability</label><input class="form-control" placeholder="Weekdays after 7 PM" v-model.trim="form.availability_text"></div>
                    </div>
                    <div class="d-flex gap-2 mt-4"><button class="btn btn-primary" :disabled="loading">{{ loading ? 'Saving...' : 'Save offering' }}</button><router-link class="btn btn-outline-secondary" to="/my-offerings">Cancel</router-link></div>
                </form>
            </div>
        </div>
    `
}
