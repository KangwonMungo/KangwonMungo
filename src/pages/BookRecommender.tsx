// 📁 src/pages/BookRecommender.tsx (챗봇형 말풍선 UI로 리팩토링)

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

    // 가짜 추천 결과
    const recommendationText = `해리포터 시리즈를 재미있게 보셨다니, 혹시 다음과 같은 요소들이 담긴 책을을
    찾으 시는 걸까요?
    
    * 장르: 판타지, 영 어덜트, 모험, 학교/기숙학교, 성장, 미스터리
    * 줄거리 특징: 숨겨진 마법 세계, 특별한 운명을 가진 주인공의 성장, 마법 학
      교 생활, 선과 악의 대결, 친구들과의 우정과 동료애
    * 매력 포인트: 매력적인 세계관, 주인공의 성장, 짜임새 있는 이야기, 유머와
      감동

     좀 더 중요하게 생각하시는 요소가 있으시거나, 다른 '이런 느낌'을 표현하는
     단어가 있다면 알려주세요!`
    ; 

    const botMessage: ChatMessage = { sender: "bot", text: recommendationText };
    setMessages((prev) => [...prev, botMessage]);

    setQuestion("");
  };

  return (
    <div className="layout">
      <div className="sidebar"></div>
        <div className="chat-panel">
          <div className="chat-container">
      <div className="chat-content">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-bubble ${msg.sender}`}>
            <div className="chat-text">{msg.text}</div>
          </div>
        ))}
      </div>

      <div className="chat-input-bar">
        <input
          className="chat-input"
          placeholder="무슨 책을 찾고 계신가요?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
        />
        <button className="chat-send-button" onClick={handleSubmit}></button>
      </div>
    </div>
    </div>
    </div>
  );
}