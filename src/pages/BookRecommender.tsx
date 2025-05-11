import { useState } from "react";
import "../BookRecommender.css";

interface ChatMessage {
  sender: "user" | "bot";
  text: string;
}

export default function BookRecommender() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const handleSubmit = async () => {
    if (!question.trim()) return;

    const userMessage: ChatMessage = { sender: "user", text: question };
    setMessages((prev) => [...prev, userMessage]);

    const botResponse = `감동적인 성장 소설이라면 이런 책들을 추천드려요:

1. 아몬드 - 감정을 배우는 소년의 성장 이야기
2. 소년이 온다 - 상실과 기억을 다룬 깊이 있는 이야기
3. 나미야 잡화점의 기적 - 위로와 연결이 담긴 따뜻한 이야기`;

    const botMessage: ChatMessage = { sender: "bot", text: botResponse };
    setMessages((prev) => [...prev, botMessage]);

    setQuestion("");
  };

  const handleBookmarkClick = () => {
    alert("관심 도서 페이지로 이동!");
  };

  return (
    <div className="chat-container">
      <main className="chat-panel">
        <div className="chat-content">
          {messages.map((msg, idx) => (
            <div key={idx} className={`chat-bubble ${msg.sender}`}>
              <div className="chat-text">{msg.text}</div>
            </div>
          ))}
        </div>

        <div className="chat-input-bar">
          <button className="bookmark-button" onClick={handleBookmarkClick}>
            📚 관심 도서
          </button>

          <input
            className="chat-input"
            placeholder="도서 추천을 받아보세요..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
          />

          <button className="chat-send-button" onClick={handleSubmit}>📤</button>
        </div>
      </main>
    </div>
  );
}
