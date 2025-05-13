import { useState } from "react";
import ChatMessage from "../components/ChatMessage";
import ChatInput from "../components/ChatInput"
import "../BookRecommender.css";
import BookRecommendationItem from "../components/BookRecommendationItem";

export interface ChatMessageType {
  sender: "user" | "bot";
  text: string;
}

export default function BookRecommender() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessageType[]>([]);

  const handleSubmit = async () => {
    if (!question.trim()) return;

    const userMessage: ChatMessageType = { sender: "user", text: question };
    setMessages((prev) => [...prev, userMessage]);

    const botResponse = `감동적인 성장 소설이라면 이런 책들을 추천드려요:

1. 아몬드 - 감정을 배우는 소년의 성장 이야기
2. 소년이 온다 - 상실과 기억을 다룬 깊이 있는 이야기
3. 나미야 잡화점의 기적 - 위로와 연결이 담긴 따뜻한 이야기`;

    <BookRecommendationItem title="아몬드 - 감정을 배우는 소년의 성장 이야기" />
    
    const botMessage: ChatMessageType = { sender: "bot", text: botResponse };
    setMessages((prev) => [...prev, botMessage]);

    setQuestion("");
  };

  const handleBookmarkClick = () => {
    alert("관심 도서 페이지로 이동!");
  };

  return (
    <div className="chat-container">
      <div className="chat-panel">
        <div className="chat-content">
          {messages.map((msg, idx) => (
            <ChatMessage key={idx} sender={msg.sender} text={msg.text} />
          ))}
        </div>

        <ChatInput
          question={question}
          setQuestion={setQuestion}
          onSubmit={handleSubmit}
          onBookmarkClick={handleBookmarkClick}
        />
      </div>
    </div>
  );
}