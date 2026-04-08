import React from "react";
import { Button } from "./button";  // Importing the Button component

export const Dialog = ({ isOpen, onClose, children }) => {
  if (!isOpen) return null; // If the dialog is not open, do not render it

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white p-6 rounded-lg max-w-md w-full">
        <div className="mb-4">
          <Button onClick={onClose} className="absolute top-4 right-4">
            X
          </Button>
        </div>
        {children}
      </div>
    </div>
  );
};

export const DialogContent = ({ children }) => {
  return <div>{children}</div>;
};

export const DialogTitle = ({ children }) => {
  return <h2 className="text-xl font-bold">{children}</h2>;
};
