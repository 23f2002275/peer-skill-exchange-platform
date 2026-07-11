const Register = {
    data() {
        return {
            form: { name: '', email: '', password: '', bio: '', interests: '' },
            error: '',
            success: '',
            loading: false
        }
    },
    methods: {
        async submit() {
            this.error = ''
            this.success = ''
            this.loading = true
            try {
                const response = await api.post('/auth/register', this.form)
                this.success = response.data.message
                setTimeout(() => this.$router.push('/login'), 700)
            } catch (error) {
                this.error = error.response && error.response.data ? error.response.data.message : 'Registration failed'
            } finally {
                this.loading = false
            }
        }
    },
    template: `
        <div class="container auth-box">
            <div class="card p-4 p-md-5">
                <h1 class="h3 mb-4">Create member account</h1>
                <div class="alert alert-danger" v-if="error">{{ error }}</div>
                <div class="alert alert-success" v-if="success">{{ success }}</div>
                <form @submit.prevent="submit">
                    <div class="mb-3"><label class="form-label">Name</label><input class="form-control" v-model.trim="form.name" required></div>
                    <div class="mb-3"><label class="form-label">Email</label><input class="form-control" type="email" v-model.trim="form.email" required></div>
                    <div class="mb-3"><label class="form-label">Password</label><input class="form-control" type="password" minlength="6" v-model="form.password" required></div>
                    <div class="mb-3"><label class="form-label">Bio</label><textarea class="form-control" rows="3" v-model.trim="form.bio"></textarea></div>
                    <div class="mb-3"><label class="form-label">Interests</label><input class="form-control" placeholder="Python, design, public speaking" v-model.trim="form.interests"></div>
                    <button class="btn btn-primary w-100" :disabled="loading">{{ loading ? 'Creating...' : 'Register' }}</button>
                </form>
                <p class="text-muted mt-3 mb-0">Every new member starts with 3 credits.</p>
            </div>
        </div>
    `
}
