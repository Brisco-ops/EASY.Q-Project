# EasyQ

Your restaurant's AI-powered menu assistant. Upload a PDF menu, translate it if needed, and let customers chat with an AI waiter.

## What it does

- **PDF to digital menu** - Upload any menu PDF, AI extracts dishes, prices, descriptions automatically
- **Instant translations** - Pre-translated to English, French, and Spanish during upload
- **QR code access** - Generate a QR code customers can scan to view the menu
- **Smart chatbot** - AI assistant helps customers choose dishes, suggests wine pairings, answers questions
- **Shopping cart** - Customers add items directly from the menu or chatbot suggestions
- **Conversation memory** - Chat history is saved so customers can continue their conversation
- **Mobile money payments** - Ready for Orange Money and MTN MoMo integration

## How to use it

### Backend setup

```bash
cd backend

# Create virtual environment
python3 -m venv ../env
source ../env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create database tables
python create_tables.py

# Start the server
uvicorn app.main:app --reload --port 8000
```

### Frontend setup

```bash
cd frontend

# Install packages
npm install

# Start dev server
npm run dev
```

Open http://localhost:5173 and you're good to go.

## For restaurant owners

1. Upload your menu PDF on the homepage
2. Get a QR code - print it or display it in your restaurant
3. That's it! Customers can now scan and browse your menu in their language

## For customers

1. Scan the QR code at the restaurant
2. Pick your language (EN/FR/ES) - menu updates instantly
3. Browse dishes or ask the AI chatbot for recommendations
4. Add items to your cart
5. Review and pay (Orange Money / MTN MoMo)

## Cool features

**AI understands context** - Ask "what goes well with fish?" and it'll suggest dishes and wines from the actual menu.

**Streaming responses** - Chat feels natural, responses appear word by word like a real conversation.

**Click to add** - When the bot suggests a dish, click the dish name to add it to your cart instantly.

**No language barriers** - Everything translates - menu, cart, chat interface.

**Conversation continues** - Close the chat and come back later, it remembers what you talked about.

## Built with

**Backend**
- FastAPI - web framework
- Google Gemini 2.5 Flash - OCR and AI chat
- SQLAlchemy + SQLite - database
- pdf2image - PDF processing

**Frontend**
- React 18 - UI framework
- Vite - build tool
- Tailwind CSS - styling
- Lucide icons - icons
