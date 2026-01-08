import { createContext, useContext, useState, useEffect } from 'react';

const CartContext = createContext();

export function CartProvider({ children }) {
  const [items, setItems] = useState([]);

  useEffect(() => {
    const saved = localStorage.getItem('cart');
    if (saved) {
      try {
        setItems(JSON.parse(saved));
      } catch (e) {
        console.error('Failed to load cart:', e);
      }
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('cart', JSON.stringify(items));
  }, [items]);

  const addItem = (nameOrItem, priceArg) => {
    let name, price;
    if (typeof nameOrItem === 'object') {
      name = nameOrItem.name;
      price = nameOrItem.price;
    } else {
      name = nameOrItem;
      price = priceArg;
    }
    
    if (typeof price === 'string') {
      price = parseFloat(price.replace(/[^0-9.,]/g, '').replace(',', '.'));
    }
    if (isNaN(price) || price == null) {
      price = 0;
    }
    
    setItems(prev => {
      const existing = prev.find(i => i.name === name && i.price === price);
      if (existing) {
        return prev.map(i => 
          i.name === name && i.price === price
            ? { ...i, quantity: i.quantity + 1 }
            : i
        );
      }
      return [...prev, { name, price, quantity: 1 }];
    });
  };

  const removeItem = (name, price) => {
    setItems(prev => prev.filter(i => !(i.name === name && i.price === price)));
  };

  const updateQuantity = (name, price, quantity) => {
    if (quantity <= 0) {
      removeItem(name, price);
      return;
    }
    setItems(prev => prev.map(i => 
      i.name === name && i.price === price
        ? { ...i, quantity }
        : i
    ));
  };

  const clearCart = () => {
    setItems([]);
  };

  const total = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  const itemCount = items.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <CartContext.Provider value={{
      items,
      addItem,
      removeItem,
      updateQuantity,
      clearCart,
      total,
      itemCount
    }}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
}
