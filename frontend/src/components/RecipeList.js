import React from "react";
import RecipeCard from "./RecipeCard";
import { Loader2, Utensils, ChefHat } from "lucide-react";

export default function RecipeList({ results, loading, hasSearched }) {
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 space-y-4">
        <Loader2 size={48} className="text-orange-500 animate-spin" />
        <p className="text-stone-400 font-serif text-lg">Consulting the chefs...</p>
      </div>
    );
  }

  if (!results || results.length === 0) {
    return hasSearched ? (
      <div className="text-center py-20 bg-white rounded-2xl border border-dashed border-stone-300">
        <div className="inline-block p-4 bg-stone-50 rounded-full mb-4">
          <Utensils className="text-stone-300" size={32} />
        </div>
        <h3 className="text-lg font-medium text-stone-900 mb-1">No recipes found</h3>
        <p className="text-stone-500">Try adjusting your ingredients or search filters.</p>
      </div>
    ) : (
      <div className="flex flex-col items-center justify-center py-12 text-center opacity-60">
        <ChefHat size={64} className="text-stone-300 mb-4" />
        <p className="font-serif text-xl text-stone-400">Delicious possibilities await.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center gap-2 mb-6 pb-4 border-b border-stone-200">
        <h3 className="font-serif text-2xl text-stone-800">Suggested Recipes</h3>
        <span className="bg-stone-100 text-stone-500 text-xs font-bold px-2 py-1 rounded-md">
          {results.length}
        </span>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {results.map((recipe, index) => (
          <RecipeCard key={index} recipe={recipe} />
        ))}
      </div>
    </div>
  );
}