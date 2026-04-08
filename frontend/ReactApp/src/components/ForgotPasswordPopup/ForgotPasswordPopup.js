import { useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom"; // Import useNavigate
import api from "../../api"// Import axios
import { Button } from "../ui/button";
import "./ForgotPasswordPopup.css";

export default function ForgotPasswordPopup({ onClose }) {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate(); // Initialize navigation

  const handleReset = async () => {
    setMessage("");
    setError("");

    if (!email) {
      setError("Please enter a valid email address.");
      return;
    }

    setLoading(true);

    try {
      const response = await api.post("/forget-password", {
        email,
      });

      if (response.data.status_code === 200) {
        setMessage("A password reset link has been sent to your email.");

        // Store email in sessionStorage for ResetPasswordPage
        sessionStorage.setItem("forgotEmail", email);

        setTimeout(() => {
          navigate("/reset-password"); // Navigate to Reset Password Page
        }, 2000);
      }
    } catch (error) {
      setError(error.response?.data?.message || "Something went wrong. Try again.");
    }

    setLoading(false);
  };

  return (
    <motion.div className="forgot-password-popup-container">
      <motion.div className="forgot-password-popup-content">
        <h2 className="forgot-password-popup-title">Forgot Password</h2>
        <p className="forgot-password-popup-text">
          Enter your email address, and we'll send you a link to reset your password.
        </p>
        <input
          type="email"
          placeholder="Email"
          className="forgot-password-popup-input"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <Button className="forgot-password-popup-button" onClick={handleReset} disabled={loading}>
          {loading ? "Sending..." : "Send Reset Link"}
        </Button>
        {message && <p className="forgot-password-popup-message success">{message}</p>}
        {error && <p className="forgot-password-popup-message error">{error}</p>}
        <button className="forgot-password-popup-close" onClick={onClose}>
          ✕
        </button>
      </motion.div>
    </motion.div>
  );
}
