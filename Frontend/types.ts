// src/types.ts

export interface Book {
  title: string;
  author: string;
  summary: string;
  recommendation: string;
  isbn: string;
  image: string;
}

export interface FavoriteBook {
  title: string;
  author: string;
  isbn: string;
  genre: string;
  image_url: string;
  introduction: string;
  keyword: string[];
  recommendation: string;
}

export interface Message {
  sender: "user" | "bot";
  text: string;
  bookList?: Book[]; // bot이 추천할 때 포함
}
