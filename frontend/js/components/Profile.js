const Profile = {
    data() {
        return { form: { name: '', bio: '', interests: '', profile_image_url: '' }, error: '', success: '', loading: false }
    },
    created() {
        const user = this.$root.user || {}
        this.form = { name: user.name || '', bio: user.bio || '', interests: user.interests || '', profile_image_url: user.profile_image_url || '' }
    },
    methods: {
        async save() {
            this.error = ''
            this.success = ''
            this.loading = true
            try {
                const response = await api.put('/auth/profile', this.form)
                this.$root.updateUser(response.data.user)
                this.success = response.data.message
            } catch (error) {
                this.error = error.response && error.response.data ? error.response.data.message : 'Could not update profile'
            } finally {
                this.loading = false
            }
        }
    },
    template: `
        <div class="container page-box">
            <div class="card p-4 p-md-5">
                <h1 class="h3 mb-4">My profile</h1>
                <div class="alert alert-danger" v-if="error">{{ error }}</div><div class="alert alert-success" v-if="success">{{ success }}</div>
                <form @submit.prevent="save"><div class="row g-3"><div class="col-md-6"><label class="form-label">Name</label><input class="form-control" v-model.trim="form.name" required></div><div class="col-md-6"><label class="form-label">Profile image URL</label><input class="form-control" v-model.trim="form.profile_image_url"></div><div class="col-12"><label class="form-label">Bio</label><textarea class="form-control" rows="4" v-model.trim="form.bio"></textarea></div><div class="col-12"><label class="form-label">Interests</label><input class="form-control" placeholder="Python, design, communication" v-model.trim="form.interests"></div></div><button class="btn btn-primary mt-4" :disabled="loading">{{ loading ? 'Saving...' : 'Save profile' }}</button></form>
            </div>
        </div>
    `
}
