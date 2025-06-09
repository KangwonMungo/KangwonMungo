import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import axios from "axios";
import {Book} from "../../types";

// context 타입
interface FavoriteContextType {
  favorites: Book[];
  addFavorite: (book: Book) => void;
  removeFavorite: (title: string) => void;
  isFavorite: (title: string) => boolean;
}

const FavoriteContext = createContext<FavoriteContextType | undefined>(undefined);

export function FavoriteProvider({ children }: { children: ReactNode }) {
  const [favorites, setFavorites] = useState<Book[]>([]);

  //  서버에서 최초 목록 불러오기
  useEffect(() => {
    axios
      .get("http://localhost:8000/api/favorites")
      .then((res) => {
        const titles = res.data.favorites as string[];
        // setFavorites(titles.map((title) => ({ title })));
        setFavorites(res.data.favorites);
      })
      .catch((err) => console.error("관심 도서 불러오기 실패", err));
  }, []);

// 서버에 관심 도서 추가
const addFavorite = async (book: Book) => {
  try {
    const payload = {
      title: book.title,
      author: book.author,
      isbn: book.isbn ?? "",
      genre: book.genre ?? "",
      image: book.image ?? "",
      introduction: book.introduction ?? "",
      keyword: Array.isArray(book.keyword) ? book.keyword : [],
    };

    console.log("📦 보내는 payload:", payload);  // 여기 추가!

    const res = await axios.post("http://localhost:8000/api/favorites", payload);
    setFavorites(res.data.favorites);
  } catch (err) {
    console.error("관심 도서 추가 실패", err);
  }
};


  //  서버에서 삭제
  const removeFavorite = async (title: string) => {
    try {
      const res = await axios.delete("http://localhost:8000/api/favorites", {
        params: { title },
      });
      // setFavorites(titles.map((title) => ({ title })));
      setFavorites(res.data.favorites);
    } catch (err) {
      console.error("관심 도서 삭제 실패", err);
    }
  };

  // 좋아요 여부 판단
  const isFavorite = (title: string) => {
    return favorites.some((b) => b.title === title);
  };

  return (
    <FavoriteContext.Provider
      value={{ favorites, addFavorite, removeFavorite, isFavorite }}
    >
      {children}
    </FavoriteContext.Provider>
  );
}

// context 가져오는 커스텀 훅
export function useFavorites() {
  const context = useContext(FavoriteContext);
  if (!context) throw new Error("useFavorites must be used within a FavoriteProvider");
  return context;
}
