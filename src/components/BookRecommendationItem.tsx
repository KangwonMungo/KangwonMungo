import { useFavorites } from "../context/FavoriteContext";
import "./BookRecommendationItem.css";

interface Props {
  title: string;
}

export default function BookRecommendationItem({ title }: Props) {
  const { addFavorite, removeFavorite, isFavorite } = useFavorites();
  const liked = isFavorite(title);

  const toggleLike = () => {
    liked ? removeFavorite(title) : addFavorite({ title });
  };

  const markAsUninterested = () => {
    removeFavorite(title); // 관심 목록에서 제거
    alert(`'${title}'을(를) 관심없음으로 표시했습니다.`);
  };

  return (
    <div className="book-item">
      <div className="book-title">{title}</div>
      <div style={{ display: "flex", gap: "0.5rem" }}>
        <button
          className="heart-icon"
          onClick={toggleLike}
          title="찜한 목록으로 가기"
        >
          {liked ? "❤️" : "🤍"}
        </button>
        <button
          className="uninterested-button"
          onClick={markAsUninterested}
        >
          관심없음
        </button>
      </div>
    </div>
  );
}
