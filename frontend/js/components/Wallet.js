const Wallet = {
    data() {
        return { balance: 0, items: [], error: '', loading: true }
    },
    created() {
        this.loadWallet()
    },
    methods: {
        async loadWallet() {
            try {
                const response = await api.get('/credits/transactions')
                this.balance = response.data.balance
                this.items = response.data.transactions
            } catch (error) {
                this.error = 'Could not load wallet'
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
            <h1 class="h2 mb-4">Credit wallet</h1>
            <div class="alert alert-danger" v-if="error">{{ error }}</div>
            <div class="text-center py-5" v-if="loading">Loading...</div>
            <div v-else>
                <div class="card p-4 mb-4"><div class="text-muted">Available balance</div><div class="display-5 fw-bold">{{ balance }} credits</div><p class="mb-0 text-muted">Credits are reserved when a teacher accepts a request and transferred after both participants confirm completion.</p></div>
                <div class="card p-4"><h2 class="h5 mb-3">Transaction history</h2><div class="text-muted" v-if="items.length === 0">No transactions.</div><div class="table-responsive" v-else><table class="table"><thead><tr><th>Date</th><th>Type</th><th>Reason</th><th class="text-end">Amount</th></tr></thead><tbody><tr v-for="item in items" :key="item.id"><td>{{ date(item.created_at) }}</td><td>{{ item.transaction_type }}</td><td>{{ item.reason }}</td><td class="text-end fw-bold" :class="item.amount >= 0 ? 'credit-positive' : 'credit-negative'">{{ item.amount > 0 ? '+' : '' }}{{ item.amount }}</td></tr></tbody></table></div></div>
            </div>
        </div>
    `
}
