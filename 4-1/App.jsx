import React from "react";
import BearImage from "./components/BearImage";
import WishListMessage from "./components/WishListMessage";
import WishBookList from "./components/WishBookList";
import BackButton from "./components/BackButton";
import "./App.css";

export default function App() {
  return (
    <div className="wishlist-bg">
      <BearImage />
      <WishListMessage />
      <WishBookList />
      <BackButton />
    </div>
  );
} 