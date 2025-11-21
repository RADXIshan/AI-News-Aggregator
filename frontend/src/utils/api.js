import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_BASE_URL || 'http://localhost:8000'

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const subscribeToDigest = async (email, name = null) => {
  try {
    const response = await api.post('/api/subscribe', {
      email,
      name: name || null,
    })

    return response.data
  } catch (error) {
    console.error('Subscription error:', error)
    // Axios wraps the response in error.response
    const errorMessage = error.response?.data?.detail || 'Failed to subscribe'
    throw new Error(errorMessage)
  }
}

export const getSubscriberCount = async () => {
  try {
    const response = await api.get('/api/subscribers/count')
    return response.data.count
  } catch (error) {
    console.error('Error fetching subscriber count:', error)
    return 0
  }
}

export const unsubscribeFromDigest = async (email) => {
  try {
    const response = await api.post('/api/unsubscribe', { email })
    return response.data
  } catch (error) {
    console.error('Unsubscribe error:', error)
    const errorMessage = error.response?.data?.detail || 'Failed to unsubscribe'
    throw new Error(errorMessage)
  }
}
