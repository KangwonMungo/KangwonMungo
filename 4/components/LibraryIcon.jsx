import React from "react";

export default function LibraryIcon({ count }) {
  return (
    <div className="library-icon">
      <img src="/library.png" alt="찜한목록" style={{ width: 48, height: 48 }} />
      <span>{count}</span>
    </div>
  );
} 