import React from "react";
import BearImage from "./components/BearImage";
import PromptSection from "./components/PromptSection";
import BookRecommendList from "./components/BookRecommendList";
import InputBox from "./components/InputBox";
import SubMessage from "./components/SubMessage";
import LibraryIcon from "./components/LibraryIcon";
import WishListButton from "./components/WishListButton";
import "./App.css";

export default function App() {
  return (
    <div className="main-bg">
      <BearImage />
      <PromptSection />
      <BookRecommendList />
      <InputBox />
      <SubMessage />
      <div className="bottom-bar">
        <LibraryIcon count={0} />
        <WishListButton />
      </div>
    </div>
  );
} 