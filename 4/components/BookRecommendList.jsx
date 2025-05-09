import React from "react";
import BookRecommendCard from "./BookRecommendCard";

export default function BookRecommendList() {
  const books = [
    {
      title: "황금 나침반 <His Dark Materials 시리즈 1>",
      desc: "평행 세계를 배경으로 소녀 라라가 진실을 찾아 모험하며 성장하는 이야기.",
    },
    {
      title: "안개born 1: 마지막 제국",
      desc: "독특한 능력과 어두운 세계 속에서 도둑 소녀 빈이 혁명의 불씨를 피우며 성장하는 이야기.",
    },
  ];
  return (
    <div className="book-recommend-list">
      {books.map((book, idx) => (
        <BookRecommendCard key={idx} {...book} />
      ))}
    </div>
  );
} 