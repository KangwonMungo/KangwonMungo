import { useState } from "react";
import { useFavorites } from "../context/FavoriteContext";
import "./BookRecommendationItem.css";
import BookDetailModal from "./BookDetailModal"
import { Book } from "../../types"


interface Props {
  book: Book;
}

export default function BookRecommendationItem({ book }: Props) {
  if (!book) return null;

  const { addFavorite, removeFavorite, isFavorite } = useFavorites();
  const liked = isFavorite(book.title);
  const [showModal, setShowModal] = useState(false); // Modal

  const toggleLike = () => {
  liked 
    ? removeFavorite(book.title) 
    : addFavorite({
      title: book.title,
      author: book.author,
      isbn: book.isbn,
      image: book.image,
      recommendation: book.recommendation,
      summary : book.summary,
      genre: "",
      introduction: book.summary,
      keyword: [],
      
  });
};

  return (
    <div className="book-item">
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
        <button className="more-button" onClick={() => setShowModal(true)}>
          <img src="/search.png" alt="상세 보기" className="button-icon" />
        </button>
      </div>

      {showModal && (
        <BookDetailModal book={book} onClose={() => setShowModal(false)} />
      )}
    </div>
  );
}
