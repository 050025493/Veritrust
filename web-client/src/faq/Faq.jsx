import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const Faq = () => {
  const [openIndex, setOpenIndex] = useState(null);

  const faqs = [
    {
      question: "What is deepfake detection and how does it work?",
      answer: "Our AI-powered deepfake detection uses EfficientNet B0, a state-of-the-art neural network, to analyze facial features, lighting inconsistencies, and artifacts that are common in AI-generated or manipulated videos. The system examines each frame to identify telltale signs of digital manipulation with N.A accuracy."
    },
    {
      question: "How accurate is VeriTrust's deepfake detection?",
      answer: "VeriTrust achieves N.A accuracy in detecting deepfakes. Our model has been trained on thousands of real and manipulated videos, and uses Grad-CAM visualization to show exactly which parts of the face triggered the detection, making our results both accurate and transparent."
    },
    {
      question: "What video formats are supported?",
      answer: "VeriTrust supports all major video formats including MP4, WebM, MOV, and AVI. Videos can be up to 500MB in size. For best results, we recommend videos with clear facial visibility and good lighting conditions."
    },
    {
      question: "What are the Grad-CAM heatmaps showing?",
      answer: "Grad-CAM (Gradient-weighted Class Activation Mapping) creates visual heatmaps that highlight which regions of the face our AI focused on when making its decision. Red/hot areas indicate strong deepfake indicators, while blue/cool areas appear more authentic. This helps you understand exactly why the AI flagged certain content."
    },
    {
      question: "Is my video data stored or shared?",
      answer: "Absolutely not. VeriTrust processes your videos in real-time and immediately deletes them after analysis. We only record the verification hash on the blockchain for proof of authenticity. Your privacy and data security are our top priorities - no videos are ever stored, shared, or used for training."
    }
  ];

  const toggleFaq = (index) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section id="faq" className="relative min-h-screen w-full py-24 px-6 bg-black">
      
      {/* Dark gradient background */}
      <div className="absolute inset-0 bg-gradient-to-b from-black via-neutral-950 to-black z-0" />
      
      {/* Subtle grid pattern overlay */}
      <div className="absolute inset-0 opacity-[0.02]" 
           style={{
             backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
             backgroundSize: '50px 50px'
           }} 
      />
      
      <div className="relative z-10 max-w-4xl mx-auto">
        
        {/* Section Header */}
        <motion.div 
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          
          <h2 className="text-5xl md:text-6xl font-extrabold text-white tracking-tight mt-6 mb-4">
            Frequently Asked <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400">Questions</span>
          </h2>
          <p className="text-neutral-400 text-lg max-w-2xl mx-auto">
            Everything you need to know about deepfake detection
          </p>
        </motion.div>

        {/* FAQ Items */}
        <div className="space-y-4">
          {faqs.map((faq, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 overflow-hidden hover:border-cyan-500/30 transition-all duration-300"
            >
              {/* Question Button */}
              <button
                onClick={() => toggleFaq(index)}
                className="w-full px-8 py-6 flex items-center justify-between text-left group"
              >
                <h3 className="text-lg md:text-xl font-bold text-white pr-8 group-hover:text-cyan-400 transition-colors">
                  {faq.question}
                </h3>
                
                {/* Animated Plus/Minus Icon */}
                <motion.div
                  animate={{ rotate: openIndex === index ? 45 : 0 }}
                  transition={{ duration: 0.3, ease: "easeInOut" }}
                  className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500/20 to-purple-500/20 flex items-center justify-center"
                >
                  <svg 
                    className="w-5 h-5 text-cyan-400" 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path 
                      strokeLinecap="round" 
                      strokeLinejoin="round" 
                      strokeWidth={2.5} 
                      d="M12 6v12M6 12h12" 
                    />
                  </svg>
                </motion.div>
              </button>

              {/* Answer with Slide Animation */}
              <AnimatePresence>
                {openIndex === index && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ 
                      height: "auto", 
                      opacity: 1,
                      transition: {
                        height: { duration: 0.4, ease: "easeInOut" },
                        opacity: { duration: 0.3, delay: 0.1 }
                      }
                    }}
                    exit={{ 
                      height: 0, 
                      opacity: 0,
                      transition: {
                        height: { duration: 0.3, ease: "easeInOut" },
                        opacity: { duration: 0.2 }
                      }
                    }}
                    className="overflow-hidden"
                  >
                    <motion.div 
                      initial={{ y: -10 }}
                      animate={{ y: 0 }}
                      exit={{ y: -10 }}
                      className="px-8 pb-6 pt-2"
                    >
                      <div className="border-t border-white/10 pt-4">
                        <p className="text-neutral-300 leading-relaxed">
                          {faq.answer}
                        </p>
                      </div>
                    </motion.div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>

        {/* Bottom CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          viewport={{ once: true }}
          className="mt-16 text-center"
        >
          <p className="text-neutral-400 mb-6">
            Still have questions?
          </p>
          <a 
            href="#about" 
            className="inline-block px-8 py-4 rounded-full bg-gradient-to-r from-cyan-500/10 to-purple-500/10 border border-cyan-500/30 text-cyan-400 font-semibold hover:bg-cyan-500/20 transition-all duration-300"
          >
            Learn More About Our Technology
          </a>
        </motion.div>

      </div>
    </section>
  );
};

export default Faq;