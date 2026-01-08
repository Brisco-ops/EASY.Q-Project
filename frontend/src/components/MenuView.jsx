import { useState } from 'react';
import { Wine, Plus, Check } from 'lucide-react';
import { useCart } from '../context/CartContext';
import { t } from '../localization/translations';

function formatPrice(price, currency) {
  if (price == null) return '';
  try {
    return new Intl.NumberFormat(undefined, { 
      style: 'currency', 
      currency: currency || 'EUR' 
    }).format(price);
  } catch {
    return `${price}`;
  }
}

function MenuItem({ item, currency, lang, onAdd }) {
  const [added, setAdded] = useState(false);
  
  const handleAdd = () => {
    onAdd(item);
    setAdded(true);
    setTimeout(() => setAdded(false), 1500);
  };
  
  return (
    <div className="py-4 border-b border-neutral-100 last:border-b-0">
      <div className="flex justify-between items-start gap-4">
        <div className="flex-1">
          <h4 className="font-medium text-neutral-900">{item.name}</h4>
          {item.description && (
            <p className="text-sm text-neutral-500 mt-1">{item.description}</p>
          )}
          {item.tags && item.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {item.tags.map((tag, i) => (
                <span 
                  key={i}
                  className="text-xs bg-neutral-100 text-neutral-600 px-2 py-0.5 rounded-full"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
        <div className="flex items-center gap-3">
          {item.price != null && (
            <span className="font-semibold text-neutral-900 whitespace-nowrap">
              {formatPrice(item.price, currency)}
            </span>
          )}
          <button
            onClick={handleAdd}
            className={`flex items-center gap-1 px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
              added 
                ? 'bg-green-500 text-white' 
                : 'bg-black text-white hover:bg-neutral-800'
            }`}
          >
            {added ? (
              <>
                <Check className="h-4 w-4" />
                {t(lang, 'added')}
              </>
            ) : (
              <>
                <Plus className="h-4 w-4" />
                {t(lang, 'addToCart')}
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

function WineItem({ wine, currency, lang, onAdd }) {
  const [added, setAdded] = useState(false);
  const info = [wine.type, wine.region, wine.grape].filter(Boolean).join(' - ');
  
  const handleAdd = () => {
    onAdd({ name: wine.name, price: wine.price, description: info });
    setAdded(true);
    setTimeout(() => setAdded(false), 1500);
  };
  
  return (
    <div className="py-3 border-b border-neutral-100 last:border-b-0">
      <div className="flex justify-between items-start gap-4">
        <div className="flex-1">
          <h4 className="font-medium text-neutral-900">{wine.name}</h4>
          {info && (
            <p className="text-sm text-neutral-500 mt-0.5">{info}</p>
          )}
        </div>
        <div className="flex items-center gap-2">
          {wine.price != null && (
            <span className="font-medium text-neutral-900 whitespace-nowrap">
              {formatPrice(wine.price, currency)}
            </span>
          )}
          <button
            onClick={handleAdd}
            className={`p-1.5 rounded-full transition-all ${
              added 
                ? 'bg-green-500 text-white' 
                : 'bg-black text-white hover:bg-neutral-800'
            }`}
          >
            {added ? <Check className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function MenuView({ sections, wines, currency, lang }) {
  const { addItem } = useCart();
  
  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <div className="lg:col-span-2 space-y-6">
        {sections.map((section, i) => (
          <div key={i} className="bg-white rounded-xl shadow-sm border border-neutral-200 p-6">
            <h3 className="text-lg font-bold text-neutral-900 mb-4 pb-2 border-b border-neutral-200 uppercase tracking-wide">
              {section.title}
            </h3>
            <div>
              {(section.items || []).map((item, j) => (
                <MenuItem key={j} item={item} currency={currency} lang={lang} onAdd={addItem} />
              ))}
            </div>
          </div>
        ))}
      </div>

      {wines && wines.length > 0 && (
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl shadow-sm border border-neutral-200 p-6 sticky top-24">
            <h3 className="text-lg font-bold text-neutral-900 mb-4 pb-2 border-b border-neutral-200 flex items-center gap-2">
              <Wine className="h-5 w-5" />
              Wines
            </h3>
            <div>
              {wines.map((wine, i) => (
                <WineItem key={i} wine={wine} currency={currency} lang={lang} onAdd={addItem} />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
