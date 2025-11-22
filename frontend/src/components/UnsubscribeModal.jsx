import { useState } from 'react'
import toast from 'react-hot-toast'
import { unsubscribeFromDigest } from '../utils/api'

const UnsubscribeModal = ({ isOpen, onClose }) => {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!email) {
      toast.error('Please enter your email address')
      return
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      toast.error('Please enter a valid email address')
      return
    }

    setLoading(true)

    try {
      const response = await unsubscribeFromDigest(email)

      if (response.success) {
        toast.success('Successfully unsubscribed! Check your email for confirmation.')
        setEmail('')
        onClose()
      } else {
        toast.error(response.message || 'Failed to unsubscribe. Please try again.')
      }
    } catch (error) {
      console.error('Unsubscribe error:', error)
      toast.error(error.message || 'Something went wrong. Please try again later.')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-100 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-white/90 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 max-w-md w-full p-8 transform transition-all overflow-hidden">
        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-linear-to-br from-purple-500/5 via-pink-500/5 to-indigo-500/5"></div>

        <div className="relative">
          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute -top-2 -right-2 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          {/* Icon */}
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 bg-linear-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center shadow-lg transform -rotate-3">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
          </div>

          {/* Title */}
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-3">
            Unsubscribe
          </h2>

          {/* Subtitle */}
          <p className="text-center text-gray-600 mb-8">
            We're sorry to see you go. Enter your email to unsubscribe from our newsletter.
          </p>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="unsubscribe-email" className="block text-md font-medium text-gray-700 mb-2">
                Email Address *
              </label>
              <input
                id="unsubscribe-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                required
                className="w-full px-6 py-4 bg-white border-2 border-gray-200 rounded-2xl focus:border-purple-500 focus:ring-4 focus:ring-purple-500/10 outline-none transition-all duration-200 text-gray-900 placeholder-gray-400"
              />
            </div>

            {/* Buttons */}
            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={onClose}
                className="cursor-pointer flex-1 px-6 py-4 bg-gray-100 text-gray-700 font-semibold rounded-2xl hover:bg-gray-200 hover:scale-[1.02] active:scale-[0.98] transition-all duration-300"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="cursor-pointer flex-1 px-6 py-4 bg-linear-to-r from-purple-600 via-pink-600 to-indigo-600 text-white font-semibold rounded-2xl hover:shadow-2xl hover:scale-[1.02] active:scale-[0.98] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Processing...</span>
                  </>
                ) : (
                  'Unsubscribe'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

export default UnsubscribeModal
