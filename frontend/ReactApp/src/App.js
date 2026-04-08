import React from "react";
import { Routes, Route } from "react-router-dom";
import BookAIPage from "./components/AI-OutputPage/BookAIPage";
import LandingPage from "./components/LandingPage/LandingPage";
import ForgotPasswordPopup from "./components/ForgotPasswordPopup/ForgotPasswordPopup";
import ResetPassword from "./components/ResetPassword/ResetPassword";

import Dashboard from "./components/Dashboard/Dashboard";
// import LoginPopup from "./components/LoginPopup/LoginPopup";

const App = () => {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPopup />} />
      <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path= "/ai" element={<BookAIPage/>}/>
    </Routes>
  );
 };

export default App;