import React, { useState } from "react";
import axios from "axios";
import { Search, Loader2, ChevronDown } from "lucide-react";

export default function SearchBar({ setResults, setLoading, setHasSearched }) {
  const [query, setQuery] = useState("");
  const [diet, setDiet] = useState([]);
  const [cuisine, setCuisine] = useState("");
  const [maxTime, setMaxTime] = useState(60);

  const toggleDiet = (option) => {
    setDiet(prev => 
      prev.includes(option) 
        ? prev.filter(item => item !== option)
        : [...prev, option]
    );
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setHasSearched(true);
    setResults([]); // Clear previous results

    try {
      // --- START OF FIX: Dynamically build the payload ---
      const payload = {
        query: query,
        max_time: maxTime,
        top_k: 20
      };

      // Only add the 'diet' filter if diets are actually selected
      if (diet.length > 0) {
        payload.diet = diet;
      }
      
      // Only add the 'cuisine' filter if a specific cuisine is chosen (i.e., not "")
      if (cuisine) { 
        payload.cuisine = cuisine;
      }
      // --- END OF FIX ---


      // --- REAL API CALL ---
      const response = await axios.post("http://127.0.0.1:8000/search", payload);
      setResults(response.data.results || []);
      
    } catch (err) {
      console.error("Search error:", err);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-3xl shadow-xl shadow-stone-200/50 overflow-hidden mb-12 border border-stone-100">
      <div className="p-8 md:p-10">
        <h2 className="font-serif text-3xl md:text-4xl text-center text-stone-800 mb-2">
          What's in your kitchen?
        </h2>
        <p className="text-center text-stone-500 mb-8 max-w-lg mx-auto">
          Enter ingredients separated by commas (e.g. chicken, lemon, rice).
        </p>

        <form onSubmit={handleSearch} className="max-w-3xl mx-auto space-y-6">
          {/* Main Input */}
          <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="h-6 w-6 text-stone-400 group-focus-within:text-orange-500 transition-colors" />
            </div>
            <input
              type="text"
              className="block w-full pl-12 pr-4 py-4 bg-stone-50 border-2 border-stone-100 rounded-xl text-lg focus:ring-0 focus:border-orange-400 focus:bg-white transition-all placeholder:text-stone-400"
              placeholder="Enter ingredients..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>

          {/* Filters Row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            {/* Cuisine */}
            <div className="space-y-2">
              <label className="text-xs font-bold text-stone-400 uppercase tracking-wider">Cuisine</label>
              <div className="relative">
                <select 
                  value={cuisine} 
                  onChange={(e) => setCuisine(e.target.value)}
                  className="appearance-none w-full bg-white border border-stone-200 text-stone-700 py-3 px-4 pr-8 rounded-lg leading-tight focus:outline-none focus:border-orange-400 focus:ring-1 focus:ring-orange-400"
                >
                  <option value="">All Cuisines</option> 
                  <option value="indian">Indian</option>
                  <option value="italian">Italian</option>
                  <option value="chinese">Chinese</option>
                  <option value="mexican">Mexican</option>
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-stone-500">
                  <ChevronDown size={16} />
                </div>
              </div>
            </div>

            {/* Time */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-bold text-stone-400 uppercase tracking-wider">
                <label>Max Time</label>
                <span className="text-orange-600">{maxTime} min</span>
              </div>
              <input
                type="range"
                min="10"
                max="120"
                step="5"
                value={maxTime}
                onChange={(e) => setMaxTime(Number(e.target.value))}
                className="w-full h-2 bg-stone-200 rounded-lg appearance-none cursor-pointer accent-orange-500"
              />
            </div>

            {/* Diet */}
            <div className="space-y-2">
              <label className="text-xs font-bold text-stone-400 uppercase tracking-wider">Dietary Needs</label>
              <div className="flex flex-wrap gap-2">
                {['vegetarian', 'vegan', 'gluten-free'].map(opt => (
                  <button
                    key={opt}
                    type="button"
                    onClick={() => toggleDiet(opt)}
                    className={`text-xs px-3 py-1.5 rounded-full border transition-all ${
                      diet.includes(opt)
                        ? 'bg-green-100 border-green-200 text-green-800 font-medium shadow-sm'
                        : 'bg-white border-stone-200 text-stone-500 hover:border-stone-300'
                    }`}
                  >
                    {opt.charAt(0).toUpperCase() + opt.slice(1)}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Button */}
          <div className="pt-2">
            <button 
              type="submit"
              className="w-full bg-stone-900 text-white font-medium py-4 rounded-xl hover:bg-orange-600 active:bg-orange-700 transition-colors shadow-lg shadow-stone-300 flex justify-center items-center gap-2"
            >
              Find Recipes
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}