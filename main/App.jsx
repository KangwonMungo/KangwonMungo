import React from "react";
import MainHeader from "./components/MainHeader";
import BookPrompt from "./components/BookPrompt";
import InputBox from "./components/InputBox";
import RecommendSection from "./components/RecommendSection";

function App() {
  return (
    <div className="app">
      <MainHeader />
      <BookPrompt />
      <InputBox />
      <RecommendSection />
    </div>
  );
}

export default App; 