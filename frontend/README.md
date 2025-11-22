# Multimodal RAG - Frontend

React + Vite frontend for the Multimodal RAG system.

## Features

- 🔍 **AI-Powered Search** - RAG queries with LLM-generated answers
- 📤 **File Upload** - Drag-and-drop support for PDF, DOCX, images, audio
- 🎨 **Modern UI** - Premium dark theme with smooth animations
- 🔗 **Citations** - Expandable source references with relevance scores
- 🌐 **Cross-Modal Search** - Search across text, images, and audio

## Setup

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

The app will be available at http://localhost:3000

### Build for Production

```bash
npm run build
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── QueryInterface.jsx    # Search/query input
│   │   ├── FileUpload.jsx        # File upload with drag-drop
│   │   ├── ResultsDisplay.jsx    # Results & answers
│   │   └── CitationCard.jsx      # Citation component
│   ├── services/
│   │   └── api.js                # API client
│   ├── styles/
│   │   ├── index.css             # Global styles
│   │   ├── App.css               # App layout
│   │   ├── QueryInterface.css
│   │   ├── FileUpload.css
│   │   ├── ResultsDisplay.css
│   │   └── CitationCard.css
│   ├── App.jsx                   # Main component
│   └── main.jsx                  # Entry point
├── index.html
├── vite.config.js
└── package.json
```

## Usage

1. **Upload Documents**: Click "Upload Documents" tab and drag files
2. **Ask Questions**: Switch to "Query & Search" tab
3. **Choose Mode**:
   - **AI Answer**: Get LLM-generated answers with citations
   - **Search**: Semantic search results
   - **Cross-Modal**: Search across text and images
4. **View Results**: Expand citations to see source details

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000`

Endpoints used:
- `POST /api/upload/` - Upload files
- `POST /api/search/` - Semantic search
- `POST /api/search/cross-modal` - Cross-modal search
- `POST /api/query/` - RAG queries

## Design

- **Dark Theme** with modern color palette
- **Gradient Accents** for visual appeal
- **Smooth Animations** for better UX
- **Responsive Layout** for all screen sizes
- **Premium Aesthetics** with glassmorphism effects
