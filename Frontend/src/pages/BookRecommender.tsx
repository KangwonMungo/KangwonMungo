import { useState } from "react";
import axios from "axios";

import ChatMessage from "../components/ChatMessage";
import ChatInput from "../components/ChatInput";
import "./BookRecommender.css";
import { Message } from "../App";

interface BookRecommenderProps {
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
}

export default function BookRecommender({
  messages,
  setMessages,
}: BookRecommenderProps) {
  const [input, setInput] = useState("");

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { sender: "user", text: input };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    try {
      const res = await axios.post(
        "http://localhost:8000/api/recommend",
        {
          question: input,
        },
        {
          headers: {
            "Content-Type": "application/json",
          },
          withCredentials: true,
        }
      );

      const botMessage: Message = {
        sender: "bot",
        text: res.data.response,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error("API 호출 오류:", err);
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text:
            "감동적인 성장 소설이라면 이런 책들을 추천드려요:\n" +
            "1. 아몬드 - 감정을 배우는 소년의 성장 이야기\n" +
            "2. 소년이 온다 - 상실과 기억을 다룬 이야기\n" +
            "3. 나미야 잡화점의 기적 - 위로와 연결이 담긴 따뜻한 이야기",
        },
      ]);
    }
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
          question={input}
          setQuestion={setInput}
          onSubmit={handleSend}
        />
      </div>
    </div>
  );
}

