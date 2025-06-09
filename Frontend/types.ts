// src/types.ts

export interface Book {
  title: string;
  author: string;
  isbn: string;
  image: string;
  recommendation: string;
  summary: string;
  genre?: string;              // optional
  introduction?: string;       // optional
  keyword?: string[]; 
}


export interface Message {
  sender: "user" | "bot";
  text: string;
  bookList?: Book[]; // bot이 추천할 때 포함
}
