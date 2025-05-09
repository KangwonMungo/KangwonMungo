import React from "react";

export default function BookRecommendCard({ title, desc }) {
  return (
    <div className="book-recommend-card">
      <h3>{title}</h3>
      <p>{desc}</p>
    </div>
  );
} 