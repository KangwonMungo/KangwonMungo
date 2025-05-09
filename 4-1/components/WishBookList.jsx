import React from "react";
import WishBookCard from "./WishBookCard";

export default function WishBookList() {
  const books = [
    {
      title: "황금 나침반 1",
      desc: "판타지 3대 거장 '필립 폴먼'의 걸작 환상소설. ... (생략)",
      img: "/golden-compass.png"
    },
    // 필요시 더 추가
  ];
  return (
    <div className="wish-book-list">
      {books.map((book, idx) => (
        <WishBookCard key={idx} {...book} />
      ))}
    </div>
  );
} 