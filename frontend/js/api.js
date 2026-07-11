const api = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json'
    }
})

api.interceptors.request.use(config => {
    const token = localStorage.getItem('skill_exchange_token')
    if (token) {
        config.headers['Authentication-Token'] = token
    }
    return config
})
