import "./ChatMessage.css"
import BookRecommendationItem from "./BookRecommendationItem";

interface Book {
  title: string;
  author: string;
  summary: string;
  recommendation: string;
  isbn: string;
  image: string;
}

interface Props {
  sender: "user" | "bot";
  text: string;
  bookList?: Book[]; // 
}

export default function ChatMessage({ sender, text, bookList }: Props) {
  const isBot = sender === "bot";

  const isRecommendation = sender === "bot" && bookList && bookList.length > 0;
  
  if (isRecommendation) {
    return (
        <div className={`chat-message ${sender}`}>
          <div className={`chat-bubble ${sender}`}>
            <div className="chat-text">
              <div style={{ marginBottom: "0.5rem" }}>{text}</div>


              {isRecommendation &&
              bookList!.map((book, idx) => (
              <BookRecommendationItem key={idx} book={book} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  // 일반 메시지 출력
  return (
      <div className={`chat-message ${sender}`}>
        <div className={`chat-bubble ${sender}`}>
        <div className="chat-text">{text}</div>
      </div>
    </div>
  );
}