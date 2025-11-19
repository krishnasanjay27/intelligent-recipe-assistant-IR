import React, { useState } from "react";
import SearchBar from "./components/SearchBar";
import RecipeList from "./components/RecipeList";
import { ChefHat } from "lucide-react";
import "./App.css";

function App() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  return (
    <div className="min-h-screen bg-[#FAF9F6] text-stone-800 font-sans selection:bg-orange-100 selection:text-orange-900">
      
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-stone-200/50 transition-all">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="bg-orange-500 p-2 rounded-lg text-white">
                <ChefHat size={24} />
              </div>
              <h1 className="font-serif text-2xl font-bold tracking-tight text-stone-900">
                Pantry<span className="text-orange-600">Chef</span>
              </h1>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <SearchBar 
          setResults={setResults}
          loading={loading}          // FIXED
          setLoading={setLoading}
          setHasSearched={setHasSearched}
        />

        <RecipeList 
          results={results}
          loading={loading}
          hasSearched={hasSearched}
        />
      </main>
    </div>
  );
}

export default App;
