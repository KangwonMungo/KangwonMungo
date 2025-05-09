import React from "react";
import BookCard from "./BookCard";

export default function RecommendSection() {
  // 예시 데이터
  const books = [
    {
      title: "황금나침반 (His Dark Materials 시리즈 1)",
      desc: "평행 세계를 배경으로 소녀 라라가 진실을 찾아 모험하며 성장하는 이야기.",
    },
    {
      title: "안개born 1: 마지막 제국",
      desc: "독특한 능력과 어두운 세계 속에서 도둑 소녀 빈이 혁명의 불씨를 피우며 성장하는 이야기.",
    },
  ];

  return (
    <section className="recommend-section">
      <h2>추천 도서</h2>
      <div className="book-list">
        {books.map((book, idx) => (
          <BookCard key={idx} title={book.title} desc={book.desc} />
        ))}
      </div>
    </section>
  );
} 