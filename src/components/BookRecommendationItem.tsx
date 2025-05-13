import { useState } from "react";
import "./BookRecommendationItem.css";

interface Props {
  title: string;
}

export default function BookRecommendationItem({ title }: Props) {
  const [liked, setLiked] = useState(false);

  return (
    <div className="book-card">
      <div className="book-title">
        {title}
      </div>
      <button
        className="heart-icon"
        onClick={() => setLiked(!liked)}
        title="찜한 목록으로 가기"
      >
        {liked ? "❤️" : "🤍"}
      </button>
    </div>
  );
}
