"use client";
import { createContext, useContext, useEffect, useState } from "react";
import type { CartItem, Skill } from "@/lib/types";

type CartContextType = {
  items: CartItem[];
  addItem: (skill: Skill) => void;
  removeItem: (skillId: string) => void;
  clearCart: () => void;
  total: number;
  count: number;
};

const CartContext = createContext<CartContextType>({
  items: [],
  addItem: () => {},
  removeItem: () => {},
  clearCart: () => {},
  total: 0,
  count: 0,
});

export function CartProvider({ children }: { children: React.ReactNode }) {
  const [items, setItems] = useState<CartItem[]>([]);

  useEffect(() => {
    const saved = localStorage.getItem("mina_cart");
    if (saved) setItems(JSON.parse(saved));
  }, []);

  const persist = (next: CartItem[]) => {
    setItems(next);
    localStorage.setItem("mina_cart", JSON.stringify(next));
  };

  const addItem = (skill: Skill) => {
    const exists = items.find((i) => i.skill.id === skill.id);
    if (!exists) persist([...items, { skill, quantity: 1 }]);
  };

  const removeItem = (skillId: string) =>
    persist(items.filter((i) => i.skill.id !== skillId));

  const clearCart = () => persist([]);

  const total = items.reduce((sum, i) => sum + i.skill.price, 0);
  const count = items.length;

  return (
    <CartContext.Provider value={{ items, addItem, removeItem, clearCart, total, count }}>
      {children}
    </CartContext.Provider>
  );
}

export const useCart = () => useContext(CartContext);
