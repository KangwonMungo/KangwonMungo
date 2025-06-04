import "./ChatMessage.css"
import BookRecommendationItem from "./BookRecommendationItem";

interface Props {
  sender: "user" | "bot";
  text: string;
}

export default function ChatMessage({ sender, text }: Props) {
  const isBot = sender === "bot";
  const avatarSrc = isBot ? "../../public/bot.jpg" : "../../public/user.jpg";

  if (sender === "bot" && text.includes("1.")) {
    // 추천 메시지인 경우 파싱하여 BookRecommendationItem으로 출력
    const lines = text.split("\n").filter((line) => line.trim() !== "");
    const header = lines[0];
    const items = lines.slice(1);

    return (
        <div className={`chat-message ${sender}`}>
          <div className="chat-avatar-container">
            {/* <img src={avatarSrc} alt="avatar" className="chat-avatar" /> */}
          </div>
          <div className={`chat-bubble ${sender}`}>
            <div className="chat-text">
              <div style={{ marginBottom: "0.5rem" }}>{header}</div>
              {items.map((line, idx) => (
                <BookRecommendationItem key={idx} title={line} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  // 일반 메시지 출력
  return (
      <div className={`chat-message ${sender}`}>
        <div className="chat-avatar-container">
          {/* <img src={avatarSrc} alt="avatar" className="chat-avatar" /> */}
        </div>
        <div className={`chat-bubble ${sender}`}>
        <div className="chat-text">{text}</div>
      </div>
    </div>
  );
}