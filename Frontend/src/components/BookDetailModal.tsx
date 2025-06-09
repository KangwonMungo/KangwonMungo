import "./BookDetailModal.css";
import { Book } from "../../types";

interface Props {
  book: Book;
  onClose: () => void;
}

export default function BookDetailModal({ book, onClose }: Props) {
  // 안전하게 이미지 경로 처리
  const imageSrc = book.image

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>&times;</button>
        <img src={imageSrc} alt={book.title} className="modal-image" />
        <h2>{book.title}</h2>
        <p><strong>저자:</strong> {book.author}</p>
        <p>{book.summary}</p>
        <p><strong>추천 이유</strong></p>
        <p>{book.recommendation}</p>
      </div>
    </div>
  );
  
}
