import { useState } from "react";
import ChatMessage from "../components/ChatMessage";
import ChatInput from "../components/ChatInput";
import "./BookRecommender.css";
import { Message } from "../App";

interface BookRecommenderProps {
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
}

export default function BookRecommender({ messages, setMessages }: BookRecommenderProps) {
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage: Message = { sender: "user", text: input };
    const botMessage: Message = {
      sender: "bot",
      text:
        "감동적인 성장 소설이라면 이런 책들을 추천드려요:\n" +
        "1. 아몬드 - 감정을 배우는 소년의 성장 이야기\n" +
        "2. 소년이 온다 - 상실과 기억을 다룬 이야기\n" +
        "3. 나미야 잡화점의 기적 - 위로와 연결이 담긴 따뜻한 이야기",
    };

    setMessages((prev) => [...prev, userMessage, botMessage]);
    setInput("");
  };

  return (
    <div className="chat-container">
      <div className="chat-panel">
        <div className="chat-content">
          {messages.map((msg, idx) => (
           <ChatMessage key={idx} sender={msg.sender} text={msg.text} />
         ))}
        </div>
        
       <ChatInput question={input} setQuestion={setInput} onSubmit={handleSend} />
     </div>
    </div>
  );
}