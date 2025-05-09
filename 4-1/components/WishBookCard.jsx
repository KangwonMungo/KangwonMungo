import React from "react";

export default function WishBookCard({ title, desc, img }) {
  return (
    <div className="wish-book-card">
      <img src={img} alt={title} className="book-cover" />
      <div>
        <h3>{title}</h3>
        <p>{desc}</p>
      </div>
    </div>
  );
} 