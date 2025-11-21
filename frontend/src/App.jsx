import { Toaster } from 'react-hot-toast'
import Navbar from './components/Navbar'
import SubscribeForm from './components/SubscribeForm'
import Hero from './components/Hero'
import Features from './components/Features'
import Footer from './components/Footer'

const App = () => {
  return (
    <div className="min-h-screen bg-linear-to-br from-indigo-50 via-purple-50 to-pink-50">
      <Toaster
        position="top-center"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#fff',
            color: '#363636',
            padding: '16px',
            borderRadius: '12px',
            boxShadow: '0 10px 40px rgba(0, 0, 0, 0.1)',
          },
          success: {
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
      <Navbar />
      <Hero />
      <SubscribeForm />
      <Features />
      <Footer />
    </div>
  )
}

export default App
