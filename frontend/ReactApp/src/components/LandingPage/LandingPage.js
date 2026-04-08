import React, { useState, useEffect } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { FiBookOpen, FiImage, FiMic, FiFeather, FiBook, FiLayers, FiArrowRight, FiPlayCircle } from "react-icons/fi";
import LoginPopup from "../LoginPopup/LoginPopup";
import "./LandingPage.css";

const LandingPage = () => {
  const [scrolled, setScrolled] = useState(false);
  const [isLoginPopupOpen, setIsLoginPopupOpen] = useState(false);

  const { scrollY } = useScroll();
  const y1 = useTransform(scrollY, [0, 1000], [0, 200]);
  const y2 = useTransform(scrollY, [0, 1000], [0, -100]);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const openLoginPopup = () => setIsLoginPopupOpen(true);
  const closeLoginPopup = () => setIsLoginPopupOpen(false);

  return (
    <div className="landing-container">
      {/* Abstract Background */}
      <div className="bg-canvas"></div>
      <div className="particles-overlay"></div>

      {/* Navigation */}
      <nav className={`glass-navbar ${scrolled ? "scrolled" : ""}`}>
        <div className="nav-container">
          <div className="brand">
            <FiBookOpen size={28} className="brand-icon" />
            <span className="brand-text">
              Book <span className="brand-highlight">Visualizer</span>
            </span>
          </div>
          <div className="nav-actions">
            <button className="nav-btn ghost-btn" onClick={openLoginPopup}>Sign In</button>
            <button className="nav-btn primary-btn" onClick={openLoginPopup}>Get Access</button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="hero-badge">
              <FiFeather /> THE MODERN READING EXPERIENCE
            </div>
            <h1 className="hero-heading">
              Read <span>Beyond</span> <br /> The Pages.
            </h1>
            <p className="hero-subtext">
              Transform your digital reading into an immersive multimedia journey.
              Upload classic literature or modern texts and let our AI generate bespoke audio narrations
              and beautiful visual schemas, enhancing your comprehension.
            </p>

            <div className="hero-cta-group">
              <button className="cta-btn primary-glow-btn" onClick={openLoginPopup}>
                Open Library <FiArrowRight />
              </button>
              <button className="cta-btn secondary-btn" onClick={openLoginPopup}>
                <FiPlayCircle size={20} /> Discover How
              </button>
            </div>
          </motion.div>
        </div>

        {/* Hero Tech Book Visual */}
        <motion.div
          initial={{ opacity: 0, x: 50, rotateY: 30 }}
          animate={{ opacity: 1, x: 0, rotateY: 0 }}
          transition={{ duration: 1, delay: 0.5 }}
          className="hero-visual"
        >
          <div className="classic-book-container">
            {/* The 6-sided 3D Book */}
            <div className="book-3d-model classic-edition">
              <div className="book-cover back"></div>
              <div className="book-pages top"></div>
              <div className="book-pages bottom"></div>
              <div className="book-pages right"></div>
              <div className="book-spine">
                <div className="spine-ribs">
                  <div className="spine-rib"></div>
                  <div className="spine-rib"></div>
                </div>
              </div>
              <div className="book-cover front">
                <div className="cover-art library-art">
                  <div className="library-cover-border">
                    <FiBook size={40} className="library-cover-icon" />
                    <span className="library-cover-title">Volume I.</span>
                    <span className="library-cover-subtitle">The Digital Archive</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Hovering interface elements */}
            <motion.div animate={{ y: [0, -10, 0] }} transition={{ repeat: Infinity, duration: 4 }} className="floating-element el-1"><FiImage size={24} /></motion.div>
            <motion.div animate={{ y: [0, 15, 0] }} transition={{ repeat: Infinity, duration: 5 }} className="floating-element el-2"><FiMic size={24} /></motion.div>
            <motion.div animate={{ y: [0, -20, 0] }} transition={{ repeat: Infinity, duration: 3 }} className="floating-element el-3"><FiLayers size={24} /></motion.div>
          </div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="features-header">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="section-title"
          >
            A New Way To <span>Consume Knowledge</span>.
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="section-subtitle"
          >
            A suite of elegant tools designed to elevate your interaction with written material, turning long texts into rich sensory experiences.
          </motion.p>
        </div>

        <div className="features-grid">
          {[
            {
              icon: <FiBookOpen size={28} />,
              title: "Serene Workspace",
              desc: "A beautifully crafted, distraction-free environment that respects the art of reading."
            },
            {
              icon: <FiMic size={28} />,
              title: "Neural Narration",
              desc: "Listen to your books with incredibly lifelike, nuanced AI voices that capture the mood of the text."
            },
            {
              icon: <FiImage size={28} />,
              title: "Visual Context",
              desc: "Generate stunning accompanying artwork and diagrams to provide deeper context."
            },
            {
              icon: <FiLayers size={28} />,
              title: "Deep Comprehension",
              desc: "Highlight, annotate, and ask the integrated AI scholar to explain complex passages instantly."
            }
          ].map((feature, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="feature-card"
            >
              <div className="feature-icon-wrapper">
                {feature.icon}
              </div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Bottom CTA */}
      <section className="bottom-cta-section">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="cta-glass-box"
        >
          <h2>Begin your literary journey.</h2>
          <p>Join thousands of readers accessing the next generation of digital literature.</p>
          <button className="cta-btn primary-glow-btn" onClick={openLoginPopup}>
            Enter Library <FiArrowRight />
          </button>
        </motion.div>
      </section>

      {/* Simple Footer */}
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-brand">
            <FiBookOpen size={20} className="brand-icon" /> Book Visualizer
          </div>
          <div className="footer-links">
            <a href="#">About</a>
            <span className="dot-sep">&bull;</span>
            <a href="#">Terms</a>
            <span className="dot-sep">&bull;</span>
            <a href="#">Privacy</a>
          </div>
        </div>
      </footer>

      <LoginPopup isOpen={isLoginPopupOpen} onClose={closeLoginPopup} />
    </div>
  );
};

export default LandingPage;
