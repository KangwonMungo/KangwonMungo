import { useState , useRef, useEffect } from "react";
import axios from "axios";
import ChatMessage from "../components/ChatMessage";
import ChatInput from "../components/ChatInput";
import "./BookRecommender.css";
import { Message } from "../../types";

interface BookRecommenderProps {
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
}

export default function BookRecommender({
  messages,
  setMessages,
}: BookRecommenderProps) {
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null); // 스크롤 ref

  const handleSend = async () => {
    if (!input.trim()) return;

    //  유저 메시지
    const userMessage: Message = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    try {
      // conversations 호출
      const res = await axios.post("http://localhost:8000/api/conversations", {
        question: input,
      });

      const generatedResponse = res.data[0]?.title; // generated_response
      const searchTrigger = res.data[0]?.author;    // search_trigger (true/false로 들어옴 → 문자열일 경우 true 처리 필요)

      // bot 메시지 (일단 추천 여부 상관없이)
      const botMessage: Message = { sender: "bot", text: generatedResponse };
      setMessages((prev) => [...prev, botMessage]);

      // search_trigger === true 면 recommendations 호출
      if (searchTrigger === true || searchTrigger === "true") {
        const recRes = await axios.get("http://localhost:8000/api/recommendations");

        const bookList = recRes.data;
        const bookListText = bookList
          .map((book: any, idx: number) => `${idx + 1}. ${book.title}`)
          .join("\n");

        const recommendationMessage: Message = {
          sender: "bot",
          text: `‘${input}’에 대해 이런 책을 추천합니다:\n${bookListText}`,
          bookList,
        };

        // 추천 결과 메시지
        setMessages((prev) => [...prev, recommendationMessage]);
      }

    } catch (err) {
      console.error("API 호출 오류:", err);
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: "추천 오류",
        },
      ]);
    }
  };

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="chat-container">
      <div className="chat-panel">
        <div className="chat-content">
          {messages.map((msg, idx) => (
            <ChatMessage
              key={idx}
              sender={msg.sender}
              text={msg.text}
              bookList={msg.bookList}
            />
          ))}
          <div ref={scrollRef} />
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
