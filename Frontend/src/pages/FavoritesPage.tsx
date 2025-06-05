import { useFavorites } from "../context/FavoriteContext";
import "./FavoritesPage.css";

export default function FavoritesPage() {
  const { favorites, removeFavorite } = useFavorites();


  return (
    <div className="favorites-container">
      <div className="favorites-card">
        <h2 className="favorites-title"> 관심 도서 목록</h2>

        <div className="favorites-scroll-box">
        {favorites.length === 0 ? (
          <p>아직 찜한 도서가 없습니다.</p>
        ) : (
          <div className="favorites-list">
            {favorites.map((book, idx) => (
              <div key={idx} className="favorites-item-card">
                <img src={book.image_url} alt={book.title} className="favorites-book-image" />

                <div className="favorites-book-details">
                  <h3>{book.title}</h3>
                  <p><strong>작가:</strong> {book.author}</p>
                  <p><strong>요약:</strong> {book.introduction}</p>
                <button
                  className="favorites-remove-btn"
                  onClick={() => removeFavorite(book.title)}
                >
                  삭제
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
      <div className="favorites-back-wrapper">
        <button className="favorites-back-btn" onClick={() => window.history.back()}>
          🔙 돌아가기
        </button>
      </div>
      </div>
    </div>
    </div>
  );
}
