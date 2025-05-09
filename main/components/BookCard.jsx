import React from "react";

export default function BookCard({ title, desc }) {
  return (
    <div className="book-card">
      <h3>{title}</h3>
      <p>{desc}</p>
    </div>
  );
} 