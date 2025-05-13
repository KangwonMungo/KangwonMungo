import "../BookRecommender.css"

interface Props {
  question: string;
  setQuestion: (q: string) => void;
  onSubmit: () => void;
  onBookmarkClick: () => void;
}

export default function ChatInput({
  question,
  setQuestion,
  onSubmit,
  onBookmarkClick,
}: Props) {
  return (
    <div className="chat-input-bar">
      <button className="bookmark-button" onClick={onBookmarkClick}>
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
