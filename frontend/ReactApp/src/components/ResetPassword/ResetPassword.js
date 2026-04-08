import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../api"; // Ensure you have API setup
import "./ResetPassword.css"; // Add styles as needed

const ResetPassword = () => {
    const [email, setEmail] = useState("");
    const [otp, setOtp] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [isOtpVerified, setIsOtpVerified] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");
    const [successMessage, setSuccessMessage] = useState("");
    const navigate = useNavigate();

    useEffect(() => {
        // Autofill email from sessionStorage
        const storedEmail = sessionStorage.getItem("forgotEmail");
        if (storedEmail) {
            setEmail(storedEmail);
        }
    }, []);

    const handleOtpVerification = async () => {
        try {
            const response = await api.post("/verify-otp", { email, otp });
            if (response.data.status_code===200) {
                setIsOtpVerified(true);
                setSuccessMessage("OTP Verified! You can now reset your password.");
                setErrorMessage("");
            } else {
                setErrorMessage("Invalid OTP. Please try again.");
            }
        } catch (error) {
            setErrorMessage("Error verifying OTP: " + error.message);
        }
    };

    const handleResetPassword = async (e) => {
        e.preventDefault();
        if (password !== confirmPassword) {
            setErrorMessage("Passwords do not match!");
            return;
        }

        try {
            const response = await api.post("/reset-password", { email, password });
            if (response.data.status_code===200) {
                sessionStorage.removeItem("forgotEmail"); // Clear stored email
                navigate("/"); // Redirect to login page
            } else {
                setErrorMessage("Failed to reset password. Try again.");
            }
        } catch (error) {
            setErrorMessage("Error resetting password: " + error.message);
        }
    };

    return (
        <div className="reset-password-overlay">
            <div className="reset-password-container">
            <h2>Reset Password</h2>
            <form onSubmit={handleResetPassword}>
                <div className="input-group">
                    <label>Email</label>
                    <input type="email" value={email} readOnly />
                </div>

                {!isOtpVerified && (
                    <div className="input-group">
                        <label>OTP</label>
                        <input
                            type="text"
                            value={otp}
                            onChange={(e) => setOtp(e.target.value)}
                            required
                        />
                        <button type="button" onClick={handleOtpVerification}>
                            Verify OTP
                        </button>
                    </div>
                )}

                {isOtpVerified && (
                    <>
                        <div className="input-group">
                            <label>New Password</label>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>

                        <div className="input-group">
                            <label>Confirm Password</label>
                            <input
                                type="password"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                required
                            />
                        </div>

                        {successMessage && <p className="success">{successMessage}</p>}
                        {errorMessage && <p className="error">{errorMessage}</p>}

                        <button type="submit">Reset Password</button>
                    </>
                )}
            </form>
        </div>
        </div>
    );
};

export default ResetPassword;
