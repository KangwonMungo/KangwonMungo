import { useState , useRef, useEffect} from "react";
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
  const scrollRef = useRef<HTMLDivElement>(null); // 스크롤 ref

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
        });

        let botMessage

        const data = res.data;

        if (Array.isArray(data) && data[0]?.title && data[0]?.isbn) {
          const bookList = data.map((book, idx) => `${idx + 1}.${book.title}`).join("\n");
          const text = `‘${input}’에 대해 이런 책을 추천합니다:\n${bookList}`
          botMessage = { sender: "bot", text , bookList: data};
        } else {
          // 단순 LLM 응답
          botMessage = { sender: "bot", text: data[0]?.title || "추천 결과 없음" };
        }

        setMessages((prev) => [...prev, botMessage]);
      } catch (err) {
        console.error("API 호출 오류:", err);
        setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: "추천 오류"
        },
      ]);
    }
  };

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth"});
  }, [messages]);

  return (
    <div className="chat-container">
      <div className="chat-panel">
        <div className="chat-content">
          {messages.map((msg, idx) => (

            <ChatMessage key={idx} sender={msg.sender} text={msg.text} bookList={msg.bookList}/>
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

