import { useNavigate } from "react-router-dom";

export default function FavoritesPage() {
  const navigate = useNavigate();

  return (
    <div style={{ padding: "2rem", textAlign: "center" }}>
      <h2> 관심 도서 목록</h2>
      <p>(여기에 관심 도서들을 나중에 리스트로 표시)</p>
      <button
        style={{
          marginTop: "2rem",
          padding: "0.5rem 1rem",
          border: "1px solid #aaa",
          borderRadius: "6px",
          cursor: "pointer",
        }}
        onClick={() => navigate("/")}
      >
         돌아가기
      </button>
    </div>
  );
}
