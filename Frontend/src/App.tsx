import { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import BookRecommender from "./pages/BookRecommender";
import FavoritesPage from "./pages/FavoritesPage";

export interface Message {
  sender: "user" | "bot";
  text: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={
            <BookRecommender
              messages={messages}
              setMessages={setMessages}
            />
          }
        />
        <Route path="/favorites" element={<FavoritesPage />} />
      </Routes>
    </Router>
  );
}

export default App;
