import React, { useState } from "react";

export const Tabs = ({ children }) => {
  const [activeTab, setActiveTab] = useState(0);

  return (
    <div>
      <div className="flex border-b-2 mb-4">{children[0]}</div>
      <div>{children[activeTab + 1]}</div>
    </div>
  );
};

export const TabsList = ({ children }) => {
  return <div className="flex">{children}</div>;
};

export const TabsTrigger = ({ children, index, setActiveTab }) => {
  return (
    <button
      onClick={() => setActiveTab(index)}
      className="px-4 py-2 border-b-2 focus:outline-none"
    >
      {children}
    </button>
  );
};

export const TabsContent = ({ children }) => {
  return <div>{children}</div>;
};
