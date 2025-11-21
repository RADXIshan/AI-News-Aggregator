import { useState } from 'react'
import UnsubscribeModal from './UnsubscribeModal'

const Navbar = () => {
  const [isUnsubscribeModalOpen, setIsUnsubscribeModalOpen] = useState(false)

  const scrollToSubscribe = () => {
    const subscribeSection = document.querySelector('#subscribe-section')
    if (subscribeSection) {
      subscribeSection.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }

  return (
    <>
      <nav className="fixed top-0 left-0 right-0 z-50 bg-transparent backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo/Brand */}
            <div className="flex items-center gap-3">
              <img src="/logo.png" alt="AI News Digest" className="w-10 h-10 object-contain" />
              <span className="text-2xl font-bold bg-linear-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                AI News Digest
              </span>
            </div>

            {/* Right side buttons */}
            <div className="flex items-center gap-3">
              <button
                onClick={() => setIsUnsubscribeModalOpen(true)}
                className="cursor-pointer px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors"
              >
                Unsubscribe
              </button>
              <button
                onClick={scrollToSubscribe}
                className="cursor-pointer px-6 py-2 bg-linear-to-r from-purple-600 via-pink-600 to-indigo-600 text-white font-semibold rounded-xl hover:shadow-lg hover:scale-105 active:scale-95 transition-all duration-300"
              >
                Subscribe
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Unsubscribe Modal */}
      <UnsubscribeModal
        isOpen={isUnsubscribeModalOpen}
        onClose={() => setIsUnsubscribeModalOpen(false)}
      />
    </>
  )
}

export default Navbar