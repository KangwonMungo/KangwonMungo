import { createContext, useContext, useState, ReactNode } from "react";

// 관심 도서 타입 정의
export interface FavoriteBook {
  title: string;
}

// context 타입
interface FavoriteContextType {
  favorites: FavoriteBook[];
  addFavorite: (book: FavoriteBook) => void;
  removeFavorite: (title: string) => void;
  isFavorite: (title: string) => boolean;
}

const FavoriteContext = createContext<FavoriteContextType | undefined>(undefined);


export function FavoriteProvider({ children }: { children: ReactNode }) {
  const [favorites, setFavorites] = useState<FavoriteBook[]>([]);

  const addFavorite = (book: FavoriteBook) => {
    if (!favorites.some((b) => b.title === book.title)) {
      setFavorites((prev) => [...prev, book]);
    }
  };

  const removeFavorite = (title: string) => {
    setFavorites((prev) => prev.filter((b) => b.title !== title));
  };

  const isFavorite = (title: string) => {
    return favorites.some((b) => b.title === title);
  };

  return (
    <FavoriteContext.Provider value={{ favorites, addFavorite, removeFavorite, isFavorite }}>
      {children}
    </FavoriteContext.Provider>
  );
}

// context 가져오는 훅
export function useFavorites() {
  const context = useContext(FavoriteContext);
  if (!context) throw new Error("useFavorites must be used within a FavoriteProvider");
  return context;
}
