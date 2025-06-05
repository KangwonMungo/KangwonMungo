import { FavoriteBook, useFavorites } from "../context/FavoriteContext";
import "./BookRecommendationItem.css";

interface Props {
  book: {
    title: string;
    author: string;
    summary: string;
    recommendation: string;
    isbn: string;
    image: string;
  };
}

export default function BookRecommendationItem({ book }: Props) {
  if (!book) return null;

  const { addFavorite, removeFavorite, isFavorite } = useFavorites();
  const liked = isFavorite(book.title);

  const toggleLike = () => {
  liked 
    ? removeFavorite(book.title) 
    : addFavorite({
      title: book.title,
      author: book.author,
      isbn: book.isbn,
      genre: "",
      image_url: book.image,
      introduction: book.summary,
      keyword: [] 
  });
};

  const markAsUninterested = () => {
    removeFavorite(book.title); // 관심 목록에서 제거
    alert(`'${book.title}'을(를) 관심없음으로 표시했습니다.`);
  };

  return (
    <div className="book-item">
      {/*<img src={book.image} alt={book.title} className="book-image" />*/}
      <div className="book-title">{book.title}</div>
      <div style={{ display: "flex", gap: "0.5rem" }}>
        <button
          className="heart-icon"
          onClick={toggleLike}
          title="찜한 목록으로 가기"
        >
          <img
            src={liked ? "/heart-filled.png" : "/heart-outline.png"}
            alt="찜하기"
            className="heart-img"
          />
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
