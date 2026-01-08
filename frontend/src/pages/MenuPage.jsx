import { useState, useEffect } from 'react';
import { useParams, useSearchParams, Link } from 'react-router-dom';
import { Loader2, ShoppingCart } from 'lucide-react';
import { api } from '../api';
import MenuView from '../components/MenuView';
import ChatWidget from '../components/ChatWidget';
import LanguageSelector from '../components/LanguageSelector';
import { useCart } from '../context/CartContext';
import { t } from '../localization/translations';

export default function MenuPage() {
  const { slug } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const [menu, setMenu] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { itemCount } = useCart();
  
  const lang = searchParams.get('lang') || 'en';

  useEffect(() => {
    loadMenu();
  }, [slug, lang]);

  const loadMenu = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await api.getMenu(slug, lang);
      setMenu(data);
    } catch (err) {
      setError('Menu not found');
    } finally {
      setLoading(false);
    }
  };

  const handleLanguageChange = (newLang) => {
    setSearchParams({ lang: newLang });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-neutral-50 flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-neutral-600" />
      </div>
    );
  }

  if (error || !menu) {
    return (
      <div className="min-h-screen bg-neutral-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-neutral-600 text-lg">{error || 'Menu not found'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-50 pb-24">
      <header className="bg-black text-white sticky top-0 z-40">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold tracking-tight">{menu.restaurant_name}</h1>
              <p className="text-xs text-neutral-400 mt-0.5">
                {menu.currency && `${menu.currency}`}
              </p>
            </div>
            <div className="flex items-center gap-4">
              <LanguageSelector
                current={lang}
                available={menu.available_languages}
                onChange={handleLanguageChange}
              />
              <Link 
                to={`/menu/${slug}/cart?lang=${lang}&currency=${menu.currency}`}
                className="relative p-2 hover:bg-neutral-800 rounded-full transition-colors"
              >
                <ShoppingCart className="h-5 w-5" />
                {itemCount > 0 && (
                  <span className="absolute -top-1 -right-1 bg-white text-black text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center">
                    {itemCount}
                  </span>
                )}
              </Link>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6">
        <MenuView 
          sections={menu.sections} 
          wines={menu.wines}
          currency={menu.currency}
          lang={lang}
        />
      </main>

      <ChatWidget 
        slug={slug} 
        lang={lang} 
        menuItems={[
          ...(menu.sections?.flatMap(s => s.items) || []),
          ...(menu.wines || [])
        ]}
      />
    </div>
  );
}
