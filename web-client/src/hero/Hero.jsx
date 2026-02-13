import React from 'react';
import { motion } from 'framer-motion';

const Hero = ({ onStart }) => {
  return (
    <section className="relative h-screen w-full overflow-hidden bg-transparent font-sans selection:bg-cyan-500/30">
      
      {/* FOREGROUND CONTENT Wrapper */}
      <div className="relative z-10 flex flex-col h-full w-full max-w-7xl mx-auto px-6">

        {/* --- A. HEADER SECTION --- */}
        <header className="flex items-center justify-between py-8">
          
          {/* Brand Logo */}
          <div className="text-2xl font-bold tracking-tighter text-white z-20">
            Veri<span className="text-cyan-400">Trust</span>
          </div>

          {/* Centered Glass Navbar (The "Pill") */}
         <nav className="hidden md:flex items-center gap-14 px-28 py-4 rounded-full bg-white/15 backdrop-blur-md border border-white/20 shadow-[0_0_15px_rgba(255,255,255,0.1)]">
            {['Home', 'About', 'FAQ'].map((item) => (
              <a 
                key={item} 
                href={`#${item.toLowerCase()}`} 
                className="text-lg font-semibold text-neutral-300 hover:text-white transition-colors duration-200"
              >
                {item}
              </a>
            ))}
          </nav>

          {/* Login Button (Outside the bar, Top Right) */}
          <button className="px-8 py-3 rounded-full bg-white text-black text-lg font-bold hover:bg-neutral-200 transition-all shadow-[0_0_20px_rgba(255,255,255,0.3)]">
            Login
          </button>
        </header>


        {/* --- B. HERO MAIN CONTENT --- */}
        <main className="flex-grow flex flex-col items-center justify-center text-center mt-[-5vh]">
          
          {/* Animated Entry Wrapper */}
          <motion.div 
            initial={{ opacity: 0, y: 30 }} 
            animate={{ opacity: 1, y: 0 }} 
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="flex flex-col items-center"
          >
            
           
            <div className="px-4 py-1.5 rounded-full border border-cyan-500/30 bg-cyan-500/10 text-cyan-400 text-xs font-mono uppercase tracking-widest backdrop-blur-md mb-6 shadow-[0_0_15px_rgba(6,182,212,0.4)]">
               AI-Powered Forensic Engine
            </div>

            {/* Massive Headline */}
            <h1 className="text-6xl md:text-8xl font-extrabold text-white tracking-tighter leading-[1.1] mb-6">
              See the <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-purple-400 to-white animate-pulse">
                Real Truth
              </span>
            </h1>

            {/* Subtext */}
            <p className="text-lg md:text-xl text-neutral-300 max-w-2xl mx-auto mb-10 leading-relaxed drop-shadow-[0_0_10px_rgba(0,0,0,0.8)]">
              Detect deepfakes instantly with our EfficientNet model. 
              Verified immutably on the Polygon blockchain.
            </p>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row items-center gap-5">
              
              {/* Primary Button (White) */}
              <button 
                onClick={onStart}
                className="px-8 py-4 rounded-full bg-white text-black font-bold text-lg hover:scale-105 transition-transform duration-300 shadow-[0_0_40px_-10px_rgba(255,255,255,0.6)]"
              >
                Get Started
              </button>

              {/* Secondary Button (Glass) */}
              <button className="px-8 py-4 rounded-full bg-white/5 border border-white/10 text-white font-medium text-lg backdrop-blur-md hover:bg-white/10 hover:border-white/30 transition-all duration-300">
                Learn More
              </button>
            </div>

          </motion.div>
        </main>

      </div>
    </section>
  )
}

export default Hero;