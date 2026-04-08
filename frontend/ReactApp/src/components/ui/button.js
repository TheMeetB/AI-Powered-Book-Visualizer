import React from "react";

export const Button = ({ children, onClick, className = "", ...props }) => {
  return (
    <button
      onClick={onClick}
      className={`button-glow ${className}`}
      style={{ padding: '12px 24px', borderRadius: '8px', fontSize: '16px' }}
      {...props}
    >
      {children}
    </button>
  );
};
