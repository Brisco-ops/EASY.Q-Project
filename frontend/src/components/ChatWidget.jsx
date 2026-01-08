import { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Loader2, Bot, ShoppingCart, Check, Trash2 } from 'lucide-react';
import { api } from '../api';
import { t } from '../localization/translations';
import { useCart } from '../context/CartContext';

function DishButton({ name, item, onAdd }) {
  const [added, setAdded] = useState(false);
  
  const handleClick = () => {
    let price = item.price;
    if (typeof price === 'string') {
      price = parseFloat(price.replace(/[^0-9.,]/g, '').replace(',', '.'));
    }
    if (isNaN(price) || price == null) {
      price = 0;
    }
    
    onAdd(item.name || name, price);
    setAdded(true);
    setTimeout(() => setAdded(false), 2000);
  };
  
  return (
    <button
      onClick={handleClick}
      className={`inline-flex items-center gap-1 font-semibold px-2 py-0.5 rounded-md transition-all mx-0.5 ${
        added 
          ? 'bg-green-100 text-green-700' 
          : 'bg-neutral-100 hover:bg-neutral-200 text-black'
      }`}
      title={added ? 'Ajouté!' : 'Ajouter au panier'}
    >
      {name}
      {added ? (
        <Check className="h-3 w-3" />
      ) : (
        <ShoppingCart className="h-3 w-3" />
      )}
    </button>
  );
}

function parseMessageContent(content, onAddToCart, menuItems) {
  if (!content) return null;
  
  const parts = [];
  let lastIndex = 0;
  const regex = /\*\*([^*]+)\*\*/g;
  let match;
  
  while ((match = regex.exec(content)) !== null) {
    // Add text before the match
    if (match.index > lastIndex) {
      parts.push({ type: 'text', content: content.slice(lastIndex, match.index) });
    }
    
    const dishName = match[1];
    const menuItem = menuItems.find(item => {
      if (!item.name) return false;
      const itemNameLower = item.name.toLowerCase().trim();
      const dishNameLower = dishName.toLowerCase().trim();
      return itemNameLower === dishNameLower ||
             itemNameLower.includes(dishNameLower) ||
             dishNameLower.includes(itemNameLower);
    });
    
    if (menuItem && menuItem.price != null) {
      parts.push({ type: 'dish', name: dishName, item: menuItem });
    } else {
      parts.push({ type: 'bold', content: dishName });
    }
    
    lastIndex = regex.lastIndex;
  }
  
  if (lastIndex < content.length) {
    parts.push({ type: 'text', content: content.slice(lastIndex) });
  }
  
  return parts.map((part, i) => {
    if (part.type === 'text') {
      return <span key={i}>{part.content}</span>;
    } else if (part.type === 'bold') {
      return <strong key={i}>{part.content}</strong>;
    } else if (part.type === 'dish') {
      return (
        <DishButton 
          key={i} 
          name={part.name} 
          item={part.item} 
          onAdd={onAddToCart} 
        />
      );
    }
    return null;
  });
}

export default function ChatWidget({ slug, lang, menuItems = [] }) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const messagesEndRef = useRef(null);
  const { addItem } = useCart();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  useEffect(() => {
    if (isOpen && !historyLoaded) {
      loadHistory();
    }
  }, [isOpen]);

  const loadHistory = async () => {
    try {
      const { messages: savedMessages } = await api.getConversation(slug);
      if (savedMessages && savedMessages.length > 0) {
        setMessages(savedMessages);
      } else {
        setMessages([{
          role: 'assistant',
          content: t(lang, 'chat.welcome')
        }]);
      }
    } catch (e) {
      setMessages([{
        role: 'assistant',
        content: t(lang, 'chat.welcome')
      }]);
    }
    setHistoryLoaded(true);
  };

  const handleClearHistory = async () => {
    await api.clearConversation(slug);
    setMessages([{
      role: 'assistant',
      content: t(lang, 'chat.welcome')
    }]);
  };

  const handleAddToCart = (name, price) => {
    addItem(name, price);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = { role: 'user', content: input.trim() };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput('');
    setLoading(true);
    setStreamingContent('');

    try {
      let fullContent = '';
      for await (const chunk of api.chatStream(slug, newMessages, lang)) {
        fullContent += chunk;
        setStreamingContent(fullContent);
      }
      setMessages([...newMessages, { role: 'assistant', content: fullContent }]);
      setStreamingContent('');
    } catch {
      setMessages([...newMessages, { 
        role: 'assistant', 
        content: t(lang, 'chat.error')
      }]);
      setStreamingContent('');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-primary-600 text-white rounded-full shadow-lg hover:bg-primary-700 flex items-center justify-center z-50 transition-all hover:scale-105"
      >
        <MessageCircle className="h-6 w-6" />
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 w-96 h-[520px] bg-white rounded-2xl shadow-2xl border border-neutral-200 flex flex-col z-50 overflow-hidden">
      <div className="bg-black text-white px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
            <Bot className="h-4 w-4 text-black" />
          </div>
          <span className="font-medium">{t(lang, 'chat.title')}</span>
        </div>
        <div className="flex items-center gap-1">
          <button 
            onClick={handleClearHistory}
            className="hover:bg-neutral-800 p-1.5 rounded-full transition-colors"
            title={t(lang, 'chat.newConversation')}
          >
            <Trash2 className="h-4 w-4" />
          </button>
          <button 
            onClick={() => setIsOpen(false)}
            className="hover:bg-neutral-800 p-1.5 rounded-full transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-neutral-50">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex gap-2 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.role === 'assistant' && (
              <div className="w-7 h-7 bg-black rounded-full flex items-center justify-center flex-shrink-0">
                <Bot className="h-4 w-4 text-white" />
              </div>
            )}
            <div
              className={`max-w-[80%] px-4 py-2.5 ${
                msg.role === 'user'
                  ? 'bg-black text-white rounded-2xl rounded-br-sm'
                  : 'bg-white text-neutral-900 rounded-2xl rounded-bl-sm border border-neutral-200'
              }`}
            >
              <p className="text-sm leading-relaxed whitespace-pre-wrap">
                {msg.role === 'assistant' 
                  ? parseMessageContent(msg.content, handleAddToCart, menuItems)
                  : msg.content
                }
              </p>
            </div>
          </div>
        ))}
        {streamingContent && (
          <div className="flex gap-2 justify-start">
            <div className="w-7 h-7 bg-black rounded-full flex items-center justify-center flex-shrink-0">
              <Bot className="h-4 w-4 text-white" />
            </div>
            <div className="max-w-[80%] px-4 py-2.5 bg-white text-neutral-900 rounded-2xl rounded-bl-sm border border-neutral-200">
              <p className="text-sm leading-relaxed whitespace-pre-wrap">
                {parseMessageContent(streamingContent, handleAddToCart, menuItems)}
                <span className="inline-block w-1.5 h-4 bg-black animate-pulse ml-0.5" />
              </p>
            </div>
          </div>
        )}
        {loading && !streamingContent && (
          <div className="flex gap-2 justify-start">
            <div className="w-7 h-7 bg-black rounded-full flex items-center justify-center">
              <Loader2 className="h-4 w-4 text-white animate-spin" />
            </div>
            <div className="bg-white border border-neutral-200 px-4 py-2.5 rounded-2xl rounded-bl-sm">
              <p className="text-sm text-neutral-500">{t(lang, 'chat.thinking')}</p>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-4 border-t border-neutral-200 bg-white">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={t(lang, 'chat.placeholder')}
            className="flex-1 px-4 py-2.5 bg-neutral-100 border-none rounded-full focus:ring-2 focus:ring-black outline-none text-sm"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="w-10 h-10 bg-black text-white rounded-full flex items-center justify-center hover:bg-neutral-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </form>
    </div>
  );
}
