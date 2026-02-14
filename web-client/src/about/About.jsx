import { motion } from 'framer-motion';

const About = () => {
  return (
    <section id="about" className="relative min-h-screen w-full py-24 px-6">
      
      {/* Semi-transparent overlay for better readability */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/40 via-black/60 to-black/80 z-0" />
      
      <div className="relative z-10 max-w-7xl mx-auto">
        
        {/* Section Header */}
        <motion.div 
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          
          <h2 className="text-4xl md:text-6xl font-extrabold text-white tracking-tight mt-6 mb-4">
            Trust in Every <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400">Pixel</span>
          </h2>
          <p className="text-neutral-400 text-lg max-w-2xl mx-auto">
            We're building the future of digital authenticity verification.
          </p>
        </motion.div>

        {/* Glass Cards Grid */}
        <div className="grid md:grid-cols-3 gap-6">
          
          {/* Card 1 */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            whileHover={{ y: -8 }}
            transition={{ type: "spring", stiffness: 200 , damping: 10, delay: 0.1 }}
            
            viewport={{ once: true }}
            className="p-8 rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 hover:border-cyan-500/30 transition-all duration-300 group"
          >
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-cyan-500/20 to-cyan-500/5 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <svg className="w-7 h-7 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-white mb-3">AI Detection</h3>
            <p className="text-neutral-400 leading-relaxed">
              Our EfficientNet-based model analyzes media with N.A+ accuracy, detecting even the most sophisticated deepfakes.
            </p>
          </motion.div>

          {/* Card 2 */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            whileHover={{ y: -8 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            viewport={{ once: true }}
            className="p-8 rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 hover:border-purple-500/30 transition-all duration-300 group"
          >
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-purple-500/20 to-purple-500/5 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <svg className="w-7 h-7 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-white mb-3">Blockchain Verified</h3>
            <p className="text-neutral-400 leading-relaxed">
              Every analysis is permanently recorded on the Polygon blockchain, creating an immutable proof of authenticity.
            </p>
          </motion.div>

          {/* Card 3 */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            whileHover={{ y: -8 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            viewport={{ once: true }}
            className="p-8 rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 hover:border-green-500/30 transition-all duration-300 group"
          >
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-green-500/20 to-green-500/5 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <svg className="w-7 h-7 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-white mb-3">Privacy First</h3>
            <p className="text-neutral-400 leading-relaxed">
              Your media is processed securely and never stored. Only the verification hash is recorded on-chain.
            </p>
          </motion.div>

        </div>

        {/* Stats Section */}
        <motion.div 
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          viewport={{ once: true }}
          className="mt-20 p-8 rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10"
        >
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-extrabold text-cyan-400 mb-2">N.A</div>
              <div className="text-neutral-400 text-sm">Detection Accuracy</div>
            </div>
            <div>
              <div className="text-4xl font-extrabold text-purple-400 mb-2">N.A</div>
              <div className="text-neutral-400 text-sm">Media Analyzed</div>
            </div>
            <div>
              <div className="text-4xl font-extrabold text-green-400 mb-2">N.A</div>
              <div className="text-neutral-400 text-sm">Avg. Processing Time</div>
            </div>
            <div>
              <div className="text-4xl font-extrabold text-white mb-2">N.A</div>
              <div className="text-neutral-400 text-sm">On-Chain Verified</div>
            </div>
          </div>
        </motion.div>

      </div>
    </section>
  )
}

export default About
