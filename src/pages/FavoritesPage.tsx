import { useFavorites } from "../context/FavoriteContext";

export default function FavoritesPage() {
  const { favorites, removeFavorite } = useFavorites();

  return (
    <div style={{ padding: "2rem", textAlign: "center" }}>
      <h2> 관심 도서 목록</h2>

      {favorites.length === 0 ? (
        <p>아직 찜한 도서가 없습니다.</p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {favorites.map((book, idx) => (
            <li
              key={idx}
              style={{
                background: "#f5f5f5",
                margin: "1rem auto",
                padding: "1rem",
                borderRadius: "10px",
                maxWidth: "600px",
                textAlign: "left",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <span>{idx + 1}. {book.title}</span>
              <button
                style={{
                  backgroundColor: "#ff5c5c",
                  color: "white",
                  border: "none",
                  borderRadius: "6px",
                  padding: "0.4rem 0.8rem",
                  cursor: "pointer",
                }}
                onClick={() => removeFavorite(book.title)}
              >
                삭제
              </button>
            </li>
          ))}
        </ul>
      )}

      <button
        style={{
          marginTop: "2rem",
          padding: "0.5rem 1rem",
          border: "1px solid #aaa",
          borderRadius: "6px",
          cursor: "pointer",
        }}
        onClick={() => window.history.back()}
      >
        🔙 돌아가기
      </button>
    </div>
  );
}
