import { useState } from "react";

import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import api from "../../api";
import { Button } from "../ui/button";
import "./LoginPopup.css";
import ForgotPasswordPopup from "../ForgotPasswordPopup/ForgotPasswordPopup";
import bookVisualizerLogo from "../Dashboard/test.png";
export default function LoginPopup({ isOpen, onClose }) {
    const navigate = useNavigate();
    const [isSignUp, setIsSignUp] = useState(false);
    const [showForgotPassword, setShowForgotPassword] = useState(false);
    const [rememberMe, setRememberMe] = useState(false);
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const [loadingScreen, setLoadingScreen] = useState(false);

    const toggleSignUp = () => {
        setIsSignUp(!isSignUp);
        setError("");
        setEmail("");
        setPassword("");
        setConfirmPassword("");
        setUsername("");
    };


    const handleSignUp = async (e) => {
        e.preventDefault();
        setError("");

        if (!username || !email || !password || !confirmPassword) {
            setError("All fields are required.");
            return;
        }
        if (password !== confirmPassword) {
            setError("Passwords do not match.");
            return;
        }

        setLoading(true);
        try {
            const response = await api.post("/register", {
                username, email, password,
            }, {

                headers: {
                    "Content-Type": "application/json",
                }
            });

            if (response.data.status_code === 201) {
                // alert("Registration successful! Please log in.");
                setIsSignUp(false); // Switch to login form
            }
        } catch (error) {
            setError(error.response?.data?.message || "Registration failed. Try again.");
        }
        setLoading(false);
    };

    const handleLogin = async (e) => {
        e.preventDefault();
        setError("");

        if (!email || !password) {
            setError("Please enter both email and password.");
            return;
        }

        setLoading(true);
        try {
            const response = await api.post("/login", {
                username: email,
                password: password,
            }, {

                headers: {
                    "Content-Type": "multipart/form-data",
                }
            });

            if (response.data.status_code === 202) {
                const storage = rememberMe ? [localStorage, sessionStorage] : [sessionStorage];
                storage.forEach(storageType => {
                    storageType.setItem("accessToken", response.data.data.access_token);
                    storageType.setItem("userId", response.data.data.user_id);
                    storageType.setItem("userName", response.data.data.username);
                });

                console.log("Stored Token:", sessionStorage.getItem("accessToken"));
                setLoadingScreen(true);
                setTimeout(() => {
                    setLoadingScreen(false);
                    onClose();
                    navigate("/dashboard");
                }, 2000);
            }
        } catch (error) {
            setError(error.response?.data?.message || "Invalid email or password.");
        }
        setLoading(false);
    };

    if (!isOpen) return null;

    return (
        <>
            {loadingScreen ? (
                <div className="loading-screen">
                    <img src={bookVisualizerLogo} alt="Book Visualizer" className="loading-logo" />
                </div>
            ) : (
                <motion.div className="login-popup-container">
                    <motion.div className="login-popup-content">
                        <h2 className="login-popup-title">
                            {isSignUp ? "Create an Account" : "Welcome Back"}
                        </h2>

                        {error && <p className="login-popup-error">{error}</p>}

                        <form className="flex flex-col" onSubmit={isSignUp ? handleSignUp : handleLogin}>
                            {isSignUp && (
                                <input
                                    type="text"
                                    placeholder="Username"
                                    className="login-popup-input"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                />
                            )}

                            <input
                                type="email"
                                placeholder="Email"
                                className="login-popup-input"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                            <input
                                type="password"
                                placeholder="Password"
                                className="login-popup-input"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />

                            {isSignUp && (
                                <input
                                    type="password"
                                    placeholder="Confirm Password"
                                    className="login-popup-input"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                />
                            )}

                            {!isSignUp && (
                                <div className="login-popup-remember">
                                    <input
                                        type="checkbox"
                                        id="rememberMe"
                                        checked={rememberMe}
                                        onChange={() => setRememberMe(!rememberMe)}
                                    />
                                    <label htmlFor="rememberMe">Remember Me</label>
                                </div>
                            )}

                            <Button className="login-popup-button" type="submit" disabled={loading}>
                                {loading ? "Processing..." : isSignUp ? "Sign Up" : "Login"}
                            </Button>
                        </form>

                        {!isSignUp && (
                            <p className="login-popup-forgot" onClick={() => setShowForgotPassword(true)}>
                                Forgot Password?
                            </p>
                        )}
                        <p className="login-popup-switch" onClick={toggleSignUp}>
                            {isSignUp ? "Already have an account? Login" : "Don't have an account? Sign Up"}
                        </p>

                        <button className="login-popup-close" onClick={onClose}>
                            ✕
                        </button>
                    </motion.div>
                </motion.div>
            )}
            {showForgotPassword && <ForgotPasswordPopup onClose={() => setShowForgotPassword(false)} />}
        </>
    );
}
