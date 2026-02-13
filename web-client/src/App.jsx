import { useState } from 'react'
import Hero from './hero/Hero'
import About from './about/About'
import Faq from './faq/Faq'
import Upload from './upload/Upload'
import Hyperspeed from './hero/Hyperspeed'

function App() {
  const [showUpload, setShowUpload] = useState(false)

  return (
    <div className="relative min-h-screen bg-black">
      {/* Fixed Hyperspeed Background */}
      <div className="fixed inset-0 z-0">
        <Hyperspeed />
      </div>
      
      {/* Scrollable Content */}
      <div className="relative z-10">
        {showUpload ? (
          <Upload onBack={() => setShowUpload(false)} />
        ) : (
          <>
            <Hero onStart={() => setShowUpload(true)} />
            <About />
            <Faq />
            <footer className="footer">
            </footer>
          </>
        )}
      </div>
    </div>
  )
}

export default App
