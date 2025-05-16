import { useFavorites } from "../context/FavoriteContext";
import "./FavoritesPage.css";

export default function FavoritesPage() {
  const { favorites, removeFavorite } = useFavorites();

  const cleanTitle = (title: string) => title.replace(/^\d+\.\s*/, "");

  return (
    <div className="favorites-container">
      <div className="favorites-card">
        <h2 className="favorites-title"> 관심 도서 목록</h2>

        {favorites.length === 0 ? (
          <p>아직 찜한 도서가 없습니다.</p>
        ) : (
          <ul className="favorites-list">
            {favorites.map((book, idx) => (
              <li key={idx} className="favorites-item">
                <span>{cleanTitle(book.title)}</span>
                <button
                  className="favorites-remove-btn"
                  onClick={() => removeFavorite(book.title)}
                >
                  삭제
                </button>
              </li>
            ))}
          </ul>
        )}

        <button
          className="favorites-back-btn"
          onClick={() => window.history.back()}
        >
          🔙 돌아가기
        </button>
      </div>
    </div>
  );
}
