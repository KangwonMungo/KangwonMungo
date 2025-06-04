import { useNavigate } from "react-router-dom";
import "./ChatInput.css"

interface Props {
  question: string;
  setQuestion: (q: string) => void;
  onSubmit: () => void;
}

export default function ChatInput({
  question,
  setQuestion,
  onSubmit,
}: Props) {
  const navigate = useNavigate();
  return (
    <div className="chat-input-bar">
      <button 
        className="bookmark-button" 
        onClick={() => navigate("/favorites")}
        title="관심 도서"
      >
        {/* 📚 관심 도서 */}
         <img
          src="/favorites.png"
          alt="관심 도서"
          className="bookmark-icon"
        />
      </button>

      <input
        className="chat-input"
        placeholder="도서 추천을 받아보세요..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && onSubmit()}
      />

      <button className="chat-send-button" onClick={onSubmit}>
        📤
      </button>
    </div>
  );
}
