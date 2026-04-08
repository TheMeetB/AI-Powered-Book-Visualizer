import { useState } from "react";

export const Textarea = () => {
  const [text, setText] = useState("");

  return (
    <div className="p-4">
      <textarea
        className="w-full h-32 p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder="Enter text here..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <p className="mt-2 text-gray-600">You entered: {text}</p>
    </div>
  );
};
