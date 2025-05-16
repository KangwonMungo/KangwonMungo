import { useNavigate } from "react-router-dom";
import "../components/BookRecommender.css"

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
      >
        📚 관심 도서
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
