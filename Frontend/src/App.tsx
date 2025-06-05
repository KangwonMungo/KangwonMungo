import { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import BookRecommender from "./pages/BookRecommender";
import FavoritesPage from "./pages/FavoritesPage";


export interface Book {
  title: string;
  author: string;
  summary: string;
  recommendation: string;
  isbn: string;
  image: string;
}

export interface Message {
  sender: "user" | "bot";
  text: string;
  bookList?: Book[];
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={
            <BookRecommender messages={messages} setMessages={setMessages} />
          }
        />
        <Route path="/favorites" element={<FavoritesPage />} />
      </Routes>
    </Router>
  );
}

export default App;
