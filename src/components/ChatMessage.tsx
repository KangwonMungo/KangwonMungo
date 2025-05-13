import "../BookRecommender.css"

interface Props {
  sender: "user" | "bot";
  text: string;
}

export default function ChatMessage({ sender, text }: Props) {
  return (
    <div className={`chat-bubble ${sender}`}>
      <div className="chat-text">{text}</div>
    </div>
  );
}
