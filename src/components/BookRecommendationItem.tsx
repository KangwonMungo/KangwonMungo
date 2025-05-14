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

  return (
    <div className="book-item">
      <div className="book-title">{title}</div>
      <button
        className="heart-icon"
        onClick={toggleLike}
        title="찜한 목록으로 가기"
      >
        {liked ? "❤️" : "🤍"}
      </button>
    </div>
  );
}



