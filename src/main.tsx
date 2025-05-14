import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
// import App from "./App";
import "./index.css";
import BookRecommender from "./pages/BookRecommender";
import FavoritesPage from "./pages/FavoritesPage";
import { FavoriteProvider } from "./context/FavoriteContext";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <FavoriteProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<BookRecommender />} />
          <Route path="/favorites" element={<FavoritesPage />} />
        </Routes>
      </BrowserRouter>
    </FavoriteProvider>
  </React.StrictMode>
);
