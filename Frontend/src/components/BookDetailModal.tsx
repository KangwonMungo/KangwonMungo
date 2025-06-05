// components/BookDetailModal.tsx
import "./BookDetailModal.css";
import { Book } from "../../types"
interface Props {
  book: Book;
  onClose: () => void;
}

export default function BookDetailModal({ book, onClose }: Props) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>닫기</button>
        <img src={book.image} alt={book.title} className="modal-image" />
        <h2>{book.title}</h2>
        <p><strong>저자:</strong> {book.author}</p>
        <p>{book.summary}</p>
        <p><strong>추천 이유:</strong></p>
        <p>{book.recommendation}</p>
      </div>
    </div>
  );
}
